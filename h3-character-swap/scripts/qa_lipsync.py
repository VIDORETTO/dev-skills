# QA de lip sync: compara a abertura da boca (MAR) frame a frame entre fonte e gerado (MediaPipe FaceLandmarker).
# Uso: python qa_lipsync.py fonte_no_canvas.mp4 gerado.mp4 [modelo.task|-] [janela_frames=24]
# A fonte deve estar na MESMA timeline do gerado (use o _ref.mp4 do assemble.py, ou o trecho correspondente).
# Saída: correlação global e por janela (padrão 1 s), razão de amplitude e atraso (±24 frames).
# Leitura: corr >= 0,6 bom · < 0,4 ruim. Atraso deve ser 0/±1. Razão de amplitude ideal 0,8–1,25.
# Limites: lábios em bico (sopro) inflam a MAR; perfis/giros (rosto de lado) não são confiáveis. Sempre ouvir também.
import os, sys, cv2, numpy as np, mediapipe as mp
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from mediapipe.tasks.python import vision, BaseOptions

src, gen = sys.argv[1], sys.argv[2]
model = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else os.environ.get(
    "H3_FACE_MODEL", os.path.join(os.path.expanduser("~"), ".cache", "h3swap", "face_landmarker.task"))
if not os.path.exists(model):  # modelo oficial do MediaPipe (3,7 MB), baixado na primeira vez
    import urllib.request
    os.makedirs(os.path.dirname(model), exist_ok=True)
    urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task", model)
WIN = int(sys.argv[4]) if len(sys.argv) > 4 else 24


def mar_series(path):
    lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model), running_mode=vision.RunningMode.VIDEO, num_faces=1))
    cap, out, n = cv2.VideoCapture(path), [], 0
    while True:
        ok, f = cap.read()
        if not ok: break
        r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB)), int(n * 1000 / 24))
        if r.face_landmarks:
            p = r.face_landmarks[0]
            v = np.hypot(p[13].x - p[14].x, p[13].y - p[14].y); h = np.hypot(p[78].x - p[308].x, p[78].y - p[308].y)
            out.append(v / h if h else np.nan)
        else:
            out.append(np.nan)
        n += 1
    return np.array(out)


a, b = mar_series(src), mar_series(gen)
n = min(len(a), len(b)); a, b = a[:n], b[:n]
ok = ~np.isnan(a) & ~np.isnan(b)
print(f"frames {n} | rosto detectado fonte {np.mean(~np.isnan(a))*100:.0f}% gerado {np.mean(~np.isnan(b))*100:.0f}%")
if ok.sum() > 10:
    print(f"correlação global MAR: {np.corrcoef(a[ok], b[ok])[0,1]:.2f}   (>=0.6 bom, <0.4 ruim)")
    print(f"amplitude média fonte {np.nanmean(a):.3f} gerado {np.nanmean(b):.3f} (razão {np.nanmean(b)/np.nanmean(a):.2f})")

    def lagcorr(s):  # s>0: gerado atrasado em relação à fonte
        x, y = (a[:n - s], b[s:]) if s >= 0 else (a[-s:], b[:n + s])
        m = ~np.isnan(x) & ~np.isnan(y)
        return np.corrcoef(x[m], y[m])[0, 1] if m.sum() > 10 else np.nan
    sc = {s: lagcorr(s) for s in range(-24, 25)}
    best = max(sc, key=lambda s: -1 if np.isnan(sc[s]) else sc[s])
    print(f"melhor atraso: {best:+d} frames ({best/24*1000:+.0f} ms)" + ("  <-- DESALINHAMENTO" if abs(best) > 1 else ""))
for s in range(0, n, WIN):
    m = ok[s:s + WIN]
    if m.sum() < WIN // 2:
        print(f"{s:4d}-{s+WIN-1:4d}  sem rosto suficiente"); continue
    c = np.corrcoef(a[s:s + WIN][m], b[s:s + WIN][m])[0, 1]
    flag = "  <-- RUIM" if c < 0.4 else ""
    print(f"{s:4d}-{s+WIN-1:4d}  corr {c:+.2f}  boca fonte {np.nanmean(a[s:s+WIN]):.3f} gerado {np.nanmean(b[s:s+WIN]):.3f}{flag}")
