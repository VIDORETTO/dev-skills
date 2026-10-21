"""QA de lip sync audiovisual com SyncNet (a métrica LSE-C / LSE-D da literatura: Wav2Lip, LatentSync, etc.).

Diferente do qa_lipsync.py (que compara a boca gerada com a boca da FONTE), aqui a boca gerada é comparada com o
ÁUDIO. Não pune o personagem por articular diferente da pessoa original; mede se a boca bate com a voz.

Uso (venv, precisa de torch): python qa_syncnet.py gerado.mp4 [--audio voz.wav] [--ref fonte.mp4] [--fps 24] [--json saida.json]
  --audio  áudio do trecho (padrão: a faixa do próprio vídeo). Use a voz isolada do segmento.
  --ref    mede também a fonte no mesmo trecho e com o mesmo áudio (linha de base)
Saída: LSE-C (confiança; maior = melhor), LSE-D (distância; menor = melhor), offset em frames e confiança por janela.
Leitura: compare com a FONTE no mesmo trecho (rode também no _ref com o mesmo áudio). Valores de referência para
vídeo real: LSE-C ~6–8, LSE-D ~6–8. LSE-C < ~3 = boca não acompanha a fala. Offset deve ser 0/±1.

Primeira execução: baixa o repositório oficial joonson/syncnet_python e o modelo syncnet_v2 (~50 MB) da VGG/Oxford
para ~/.cache/h3swap/. O recorte do rosto usa o FaceLandmarker do MediaPipe (o mesmo do qa_lipsync), com a mesma
geometria e suavização do pipeline oficial (crop_scale 0,4; mediana de 13 frames; 224x224).
O SyncNet só aceita 25 fps: os frames são reetiquetados 1:1 para 25 fps e o áudio acelerado 25/24 (pitch mantido),
sem duplicar nem descartar frames.
"""
import io, json, os, subprocess, sys, tempfile, types, urllib.request, zipfile
import cv2, numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from scipy import signal

CACHE = os.path.join(os.path.expanduser("~"), ".cache", "h3swap")
REPO = os.path.join(CACHE, "syncnet_python")
REPO_ZIP = "https://codeload.github.com/joonson/syncnet_python/zip/refs/heads/master"
MODEL_URL = "http://www.robots.ox.ac.uk/~vgg/software/lipsync/data/syncnet_v2.model"
SN_FPS, CROP_SCALE, VSHIFT = 25, 0.4, 15


def ensure_syncnet():
    if not os.path.exists(os.path.join(REPO, "SyncNetInstance.py")):
        os.makedirs(CACHE, exist_ok=True)
        data = urllib.request.urlopen(REPO_ZIP, timeout=120).read()
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            root = z.namelist()[0].split("/")[0]
            for name in z.namelist():
                if name.endswith("/") or "/detectors/" in name:
                    continue
                dest = os.path.join(REPO, name[len(root) + 1:])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, "wb").write(z.read(name))
    model = os.path.join(REPO, "data", "syncnet_v2.model")
    if not os.path.exists(model):
        os.makedirs(os.path.dirname(model), exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, model)
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    return model


def face_track(video, fps):
    """bbox (x1,y1,x2,y2) do maior rosto por frame, via landmarks; frames sem rosto são interpolados."""
    from qa_lipsync import landmarks
    boxes = []
    for item in landmarks(video, None, fps):
        if item is None:
            boxes.append(None); continue
        p, w, h = item
        xs, ys = [q.x * w for q in p], [q.y * h for q in p]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    ok = [b is not None for b in boxes]
    if sum(ok) < 0.5 * len(boxes):
        raise SystemExit(f"rosto achado em só {sum(ok)}/{len(boxes)} frames — SyncNet não é confiável neste trecho")
    idx = np.flatnonzero(ok)
    arr = np.array([boxes[i] for i in idx], float)
    full = np.stack([np.interp(np.arange(len(boxes)), idx, arr[:, k]) for k in range(4)], 1)
    return full, np.array(ok)


def crop_video(video, boxes, out_avi):
    """Mesma geometria do crop_video() oficial (run_pipeline.py), gravado a 25 fps 1:1."""
    s = signal.medfilt(np.maximum(boxes[:, 3] - boxes[:, 1], boxes[:, 2] - boxes[:, 0]) / 2, kernel_size=13)
    y = signal.medfilt((boxes[:, 1] + boxes[:, 3]) / 2, kernel_size=13)
    x = signal.medfilt((boxes[:, 0] + boxes[:, 2]) / 2, kernel_size=13)
    cap = cv2.VideoCapture(video)
    vout = cv2.VideoWriter(out_avi, cv2.VideoWriter_fourcc(*"XVID"), SN_FPS, (224, 224))
    for i in range(len(boxes)):
        ok, image = cap.read()
        if not ok: break
        bs = s[i]; bsi = int(bs * (1 + 2 * CROP_SCALE))
        frame = np.pad(image, ((bsi, bsi), (bsi, bsi), (0, 0)), "constant", constant_values=(110, 110))
        my, mx = y[i] + bsi, x[i] + bsi
        face = frame[int(my - bs):int(my + bs * (1 + 2 * CROP_SCALE)), int(mx - bs * (1 + CROP_SCALE)):int(mx + bs * (1 + CROP_SCALE))]
        vout.write(cv2.resize(face, (224, 224)))
    vout.release()


def measure(video, audio=None, fps=24.0, win=None, device=None):
    model = ensure_syncnet()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import torch
    from SyncNetInstance import SyncNetInstance
    boxes, ok = face_track(video, fps)
    with tempfile.TemporaryDirectory() as tmp:
        crops, wav, avi = os.path.join(tmp, "crops.avi"), os.path.join(tmp, "a.wav"), os.path.join(tmp, "clip.avi")
        crop_video(video, boxes, crops)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", audio or video, "-vn", "-ac", "1", "-ar", "16000",
                        "-af", f"atempo={SN_FPS / fps}", "-c:a", "pcm_s16le", wav], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", crops, "-i", wav, "-c:v", "copy", "-c:a", "copy",
                        "-shortest", avi], check=True)
        sn = SyncNetInstance(device=device or ("cuda" if torch.cuda.is_available() else "cpu"))
        sn.loadParameters(model)
        opt = types.SimpleNamespace(tmp_dir=tmp, reference="sn", batch_size=20, vshift=VSHIFT)
        offset, conf, dists = sn.evaluate(opt, videofile=avi)
    mdist = dists.mean(0)
    best = int(mdist.argmin())
    fconf = np.median(mdist) - dists[:, best]
    fconfm = signal.medfilt(fconf, kernel_size=9)
    w = int(win or round(fps))
    res = {"lse_c": float(conf), "lse_d": float(mdist.min()), "offset": int(offset), "frames": int(len(boxes)),
           "face_found": float(ok.mean()), "windows": []}
    for st in range(0, len(fconfm), w):
        res["windows"].append({"start": st, "end": st + w - 1, "conf": float(np.mean(fconfm[st:st + w]))})
    return res


def report(r, base=None):
    print(f"SyncNet · LSE-C {r['lse_c']:.2f} (maior = melhor) · LSE-D {r['lse_d']:.2f} (menor = melhor) · "
          f"offset {r['offset']:+d} frames" + ("  <-- DESALINHAMENTO" if abs(r["offset"]) > 1 else ""))
    if base:
        print(f"fonte no mesmo trecho: LSE-C {base['lse_c']:.2f} · LSE-D {base['lse_d']:.2f} "
              f"(razão gerado/fonte {r['lse_c'] / base['lse_c']:.2f})" if base["lse_c"] else "")
    for wd in r["windows"]:
        print(f"{wd['start']:4d}-{wd['end']:4d}  conf {wd['conf']:+.2f}" + ("  <-- FRACO" if wd["conf"] < 1.5 else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    def pop(flag, default=None):
        if flag in args:
            i = args.index(flag); v = args[i + 1]; del args[i:i + 2]; return v
        return default
    out_json, audio, fps, ref = pop("--json"), pop("--audio"), float(pop("--fps", 24)), pop("--ref")
    r = measure(args[0], audio, fps)
    base = measure(ref, audio, fps) if ref else None
    report(r, base)
    if out_json:
        json.dump({"gen": r, "src": base}, open(out_json, "w", encoding="utf-8"), indent=1)
