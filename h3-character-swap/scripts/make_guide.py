"""Clipes-guia no estilo Genjutsu: a pessoa original sai do vídeo de entrada e vira profundidade colorida e/ou face mesh.

Ideia (Genjutsu-Skill / Seedance Edit): se o modelo não vê os pixels do rosto original, não tem o que vazar; a
profundidade preserva silhueta, pose e movimento, e o face mesh preserva expressão e lábios. O prompt manda remover
as cores e as linhas da saída. No H3 isto é EXPERIMENTAL (o LoRA do akatz não foi treinado com essa entrada): use
como A/B no 1º segmento (`run_job.py seg|best ... --guide MODO`) e compare pela QA.

Uso (venv): python make_guide.py JOB.json --mode depth|mesh|depth_mesh [--segs A1,A2] [--depth da2|midas] [--erode 6]
Gera JOB/clips_guide/<modo>/<seg>.mp4 (mesmos frames, fps e áudio do clips/<seg>.mp4) e <seg>_preview.jpg.

Detalhes que importam:
- A região pintada é a pessoa (rembg, maior componente, ERODIDA --erode px): fica sempre DENTRO da máscara do SAM +
  expansion_px que o H3 regenera. Fora dessa máscara o latente da entrada é preservado; se a profundidade vazasse para
  fora, ela apareceria no resultado. Com várias pessoas na cena, só a maior é pintada (combine com selection=largest).
- O SAM da ferramenta continua rodando no clipe ORIGINAL (o run_job liga o guia só na geração).
- A cor da profundidade é normalizada no clipe inteiro (percentis da região da pessoa), não por frame: sem "pisca".
- Profundidade: `da2` = Depth Anything V2 Small (transformers; padrão) · `midas` = MiDaS small (torch.hub).
"""
import argparse, os, subprocess, sys
import cv2, numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, segments, FPS
from qa_mask import person_mask

ap = argparse.ArgumentParser()
ap.add_argument("job")
ap.add_argument("--mode", required=True, choices=["depth", "mesh", "depth_mesh"])
ap.add_argument("--segs", default="")
ap.add_argument("--depth", default="da2", choices=["da2", "midas"])
ap.add_argument("--erode", type=int, default=6, help="px (na resolução do clipe) para manter a pintura dentro da máscara do H3")
a = ap.parse_args()

job = load_job(a.job)
D = job["_dir"]
OUT = os.path.join(D, "clips_guide", a.mode)
os.makedirs(OUT, exist_ok=True)

_depth = None


def depth_fn():
    """Devolve f(frame_bgr) -> mapa de disparidade (maior = mais perto), float32 HxW."""
    global _depth
    if _depth is not None:
        return _depth
    import torch
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    if a.depth == "da2":
        from transformers import pipeline
        from PIL import Image
        pipe = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=dev)
        def f(img):
            r = pipe(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
            return cv2.resize(r["predicted_depth"].squeeze().float().cpu().numpy(), (img.shape[1], img.shape[0]))
    else:
        model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small").to(dev).eval()
        tf = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform
        def f(img):
            with torch.no_grad():
                p = model(tf(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).to(dev))
            return cv2.resize(p.squeeze().float().cpu().numpy(), (img.shape[1], img.shape[0]))
    _depth = f
    return f


def target_mask(img):
    """Pessoa-alvo: maior componente da máscara rembg, erodida."""
    m = person_mask(img).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n <= 1:
        return np.zeros(m.shape, bool)
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    m = (lab == big).astype(np.uint8)
    if a.erode:
        m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * a.erode + 1, 2 * a.erode + 1)))
    return m > 0


_lm = None


def mesh_landmarks(img, t_ms):
    global _lm
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    from qa_lipsync import face_model
    if _lm is None:
        _lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=face_model()), running_mode=vision.RunningMode.VIDEO, num_faces=1))
    r = _lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), t_ms)
    return r.face_landmarks[0] if r.face_landmarks else None


def draw_mesh(img, lm, mask):
    """Mesmo desenho do Genjutsu: malha fina + contornos de olhos, sobrancelhas, lábios e oval, só dentro da máscara."""
    from mediapipe.tasks.python.vision import FaceLandmarksConnections as C
    h, w = img.shape[:2]
    pts = [(int(p.x * w), int(p.y * h)) for p in lm]
    layer = img.copy()
    for c in C.FACE_LANDMARKS_TESSELATION:
        cv2.line(layer, pts[c.start], pts[c.end], (205, 170, 50), 1, cv2.LINE_AA)
    for conn, col in [(C.FACE_LANDMARKS_LIPS, (60, 60, 255)), (C.FACE_LANDMARKS_LEFT_EYE, (80, 255, 80)),
                      (C.FACE_LANDMARKS_RIGHT_EYE, (80, 255, 80)), (C.FACE_LANDMARKS_LEFT_EYEBROW, (255, 200, 80)),
                      (C.FACE_LANDMARKS_RIGHT_EYEBROW, (255, 200, 80)), (C.FACE_LANDMARKS_FACE_OVAL, (240, 240, 240))]:
        for c in conn:
            cv2.line(layer, pts[c.start], pts[c.end], col, 2, cv2.LINE_AA)
    img[mask] = layer[mask]
    return img


def read_frames(path):
    cap = cv2.VideoCapture(path)
    while True:
        ok, f = cap.read()
        if not ok: break
        yield f


wanted = set(x for x in a.segs.split(",") if x)
for shot, idx, seg in segments(job):
    if wanted and seg["id"] not in wanted:
        continue
    clip = os.path.join(D, seg["clip"])
    dest = os.path.join(OUT, os.path.basename(seg["clip"]))
    frames = list(read_frames(clip))
    masks = [target_mask(f) for f in frames]
    out_frames = [f.copy() for f in frames]
    if a.mode in ("depth", "depth_mesh"):
        fn = depth_fn()
        disp = [fn(f) for f in frames]
        vals = np.concatenate([d[m] for d, m in zip(disp, masks) if m.any()]) if any(m.any() for m in masks) else np.zeros(1)
        lo, hi = np.percentile(vals, 2), np.percentile(vals, 98)
        for o, d, m in zip(out_frames, disp, masks):
            col = cv2.applyColorMap(np.clip((d - lo) / max(hi - lo, 1e-6) * 255, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
            o[m] = col[m]
    if a.mode in ("mesh", "depth_mesh"):
        miss = 0
        for i, (o, src, m) in enumerate(zip(out_frames, frames, masks)):
            lm = mesh_landmarks(src, int(i * 1000 / FPS))   # landmarks sempre do frame ORIGINAL
            if lm is None:
                miss += 1; continue
            draw_mesh(o, lm, m)
        if miss:
            print(f"  {seg['id']}: face mesh ausente em {miss}/{len(frames)} frames (perfil/oclusão)")
        _lm = None                                          # timestamps recomeçam no próximo clipe
    h, w = frames[0].shape[:2]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                            "-r", str(FPS), "-i", "-", "-i", clip, "-map", "0:v", "-map", "1:a:0?", "-c:a", "copy",
                            "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", dest],
                           stdin=subprocess.PIPE)
    for o in out_frames:
        enc.stdin.write(o.tobytes())
    enc.stdin.close(); enc.wait()
    sel = [0, len(out_frames) // 2, len(out_frames) - 1]
    cv2.imwrite(dest.replace(".mp4", "_preview.jpg"),
                np.hstack([cv2.resize(out_frames[i], (360, int(360 * h / w))) for i in sel]))
    empty = sum(1 for m in masks if not m.any())
    print(f"{seg['id']}: {dest} · {len(out_frames)} frames" + (f" · {empty} frames sem pessoa" if empty else ""), flush=True)
