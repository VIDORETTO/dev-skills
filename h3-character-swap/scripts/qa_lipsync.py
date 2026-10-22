# QA de lip sync: compara a abertura da boca (MAR) frame a frame entre fonte e gerado (MediaPipe FaceLandmarker).
# Uso: python qa_lipsync.py fonte_no_canvas.mp4 gerado.mp4 [modelo.task|-] [janela_frames=24] [--fps 24] [--json saida.json]
# A fonte deve estar na MESMA timeline do gerado (use o _ref.mp4 do assemble.py, ou o trecho correspondente).
# Saída: correlação global e por janela (padrão 1 s), razão de amplitude e atraso (±24 frames).
# Leitura: corr >= 0,6 bom · < 0,4 ruim. Atraso deve ser 0/±1. Razão de amplitude ideal 0,8–1,25.
# Limites: lábios em bico (sopro) inflam a MAR; perfis/giros (rosto de lado) não são confiáveis. Sempre ouvir também.
# Complementar: qa_syncnet.py mede a sincronia com o ÁUDIO (LSE-C/LSE-D), sem depender da boca da fonte.
import json, os, sys
import cv2, numpy as np, mediapipe as mp
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from mediapipe.tasks.python import vision, BaseOptions

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"


def face_model(path=None):
    model = path or os.environ.get("H3_FACE_MODEL", os.path.join(os.path.expanduser("~"), ".cache", "h3swap", "face_landmarker.task"))
    if not os.path.exists(model):  # modelo oficial do MediaPipe (3,7 MB), baixado na primeira vez
        import urllib.request
        os.makedirs(os.path.dirname(model), exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, model)
    return model


def landmarks(path, model=None, fps=24):
    """Landmarks (468+) do maior rosto por frame, normalizados ao quadro inteiro (None se não houver rosto).
    Rosto pequeno no quadro (plano médio/aberto, ~130 px de largura) faz o FaceLandmarker falhar na imagem inteira:
    nesses frames ele tenta de novo num recorte ampliado em volta do rosto (último rosto achado ou o detector do
    InsightFace) e devolve os pontos já convertidos para o quadro inteiro."""
    from types import SimpleNamespace as P
    opts = lambda mode: vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=face_model(model)),
                                                     running_mode=mode, num_faces=1)
    lm = vision.FaceLandmarker.create_from_options(opts(vision.RunningMode.VIDEO))
    lm_img = None
    cap, out, n, last_box, rescued = cv2.VideoCapture(path), [], 0, None, 0
    while True:
        ok, f = cap.read()
        if not ok: break
        h, w = f.shape[:2]
        r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB)), int(n * 1000 / fps))
        pts = r.face_landmarks[0] if r.face_landmarks else None
        if pts is None:
            box = last_box
            if box is None:
                try:
                    import qa_identity
                    fs = qa_identity.faces(f)
                    box = tuple(fs[0].bbox) if fs else None
                except ImportError:
                    box = None
            if box is not None:
                x0, y0, x1, y1 = box
                m = 0.6 * max(x1 - x0, y1 - y0)
                ox, oy = int(max(0, x0 - m)), int(max(0, y0 - m))
                crop = f[oy:int(min(h, y1 + m)), ox:int(min(w, x1 + m))]
                if crop.size:
                    k = 512 / max(crop.shape[:2])
                    big = cv2.resize(crop, None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC)
                    lm_img = lm_img or vision.FaceLandmarker.create_from_options(opts(vision.RunningMode.IMAGE))
                    rr = lm_img.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(cv2.cvtColor(big, cv2.COLOR_BGR2RGB))))
                    if rr.face_landmarks:
                        cw, ch = crop.shape[1], crop.shape[0]
                        pts = [P(x=(ox + q.x * cw) / w, y=(oy + q.y * ch) / h) for q in rr.face_landmarks[0]]
                        rescued += 1
        if pts is not None:
            xs, ys = [q.x * w for q in pts], [q.y * h for q in pts]
            last_box = (min(xs), min(ys), max(xs), max(ys))
        else:
            last_box = None
        out.append((pts, w, h) if pts is not None else None)
        n += 1
    lm.close()
    if lm_img: lm_img.close()
    if rescued:
        print(f"  (rosto pequeno: {rescued} frames medidos num recorte ampliado)", flush=True)
    return out


def mar_series(path, model=None, fps=24):
    out = []
    for item in landmarks(path, model, fps):
        if item is None:
            out.append(np.nan); continue
        p = item[0]
        v = np.hypot(p[13].x - p[14].x, p[13].y - p[14].y); h = np.hypot(p[78].x - p[308].x, p[78].y - p[308].y)
        out.append(v / h if h else np.nan)
    return np.array(out)


def compare(a, b, win=24):
    n = min(len(a), len(b)); a, b = a[:n], b[:n]
    ok = ~np.isnan(a) & ~np.isnan(b)
    res = {"frames": n, "face_src": float(np.mean(~np.isnan(a))), "face_gen": float(np.mean(~np.isnan(b))),
           "corr": None, "amp_ratio": None, "lag": None, "windows": []}
    if ok.sum() > 10:
        res["corr"] = float(np.corrcoef(a[ok], b[ok])[0, 1])
        res["amp_ratio"] = float(np.nanmean(b) / np.nanmean(a))

        def lagcorr(s):  # s>0: gerado atrasado em relação à fonte
            x, y = (a[:n - s], b[s:]) if s >= 0 else (a[-s:], b[:n + s])
            m = ~np.isnan(x) & ~np.isnan(y)
            return np.corrcoef(x[m], y[m])[0, 1] if m.sum() > 10 else np.nan
        sc = {s: lagcorr(s) for s in range(-24, 25)}
        res["lag"] = int(max(sc, key=lambda s: -1 if np.isnan(sc[s]) else sc[s]))
    for s in range(0, n, win):
        m = ok[s:s + win]
        if m.sum() < win // 2:
            res["windows"].append({"start": s, "end": s + win - 1, "corr": None}); continue
        c = np.corrcoef(a[s:s + win][m], b[s:s + win][m])[0, 1]
        res["windows"].append({"start": s, "end": s + win - 1, "corr": None if np.isnan(c) else float(c),
                               "mouth_src": float(np.nanmean(a[s:s + win])), "mouth_gen": float(np.nanmean(b[s:s + win]))})
    return res


def report(r, fps=24):
    print(f"frames {r['frames']} | rosto detectado fonte {r['face_src']*100:.0f}% gerado {r['face_gen']*100:.0f}%")
    if r["corr"] is not None:
        print(f"correlação global MAR: {r['corr']:.2f}   (>=0.6 bom, <0.4 ruim)")
        print(f"razão de amplitude gerado/fonte: {r['amp_ratio']:.2f}")
        print(f"melhor atraso: {r['lag']:+d} frames ({r['lag']/fps*1000:+.0f} ms)" + ("  <-- DESALINHAMENTO" if abs(r['lag']) > 1 else ""))
    for w in r["windows"]:
        if w["corr"] is None:
            print(f"{w['start']:4d}-{w['end']:4d}  sem rosto suficiente"); continue
        flag = "  <-- RUIM" if w["corr"] < 0.4 else ""
        print(f"{w['start']:4d}-{w['end']:4d}  corr {w['corr']:+.2f}  boca fonte {w['mouth_src']:.3f} gerado {w['mouth_gen']:.3f}{flag}")


if __name__ == "__main__":
    args = [x for x in sys.argv[1:]]
    def pop(flag, default=None):
        if flag in args:
            i = args.index(flag); v = args[i + 1]; del args[i:i + 2]; return v
        return default
    out_json, fps = pop("--json"), float(pop("--fps", 24))
    src, gen = args[0], args[1]
    model = args[2] if len(args) > 2 and args[2] != "-" else None
    win = int(args[3]) if len(args) > 3 else int(round(fps))
    r = compare(mar_series(src, model, fps), mar_series(gen, model, fps), win)
    report(r, fps)
    if out_json:
        json.dump(r, open(out_json, "w", encoding="utf-8"), indent=1)
