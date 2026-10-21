"""Final em resolução cheia: cola o personagem gerado sobre o vídeo ORIGINAL (plate), só dentro de uma máscara suave.

Por quê: o H3 entrega o canvas (736x1344 no preset 768) decodificado pelo VAE; a ferramenta não cola nada sobre o
RGB da fonte (`body_composited: False`). Aqui o fundo volta a ser a fonte bit a bit, em resolução cheia, os shots
`preserve` saem com o quadro inteiro (sem o recorte do canvas) e só a região do personagem é ampliada.

Uso (venv): python composite.py JOB.json [saida.mp4] [--mask union|expanded] [--margin 32] [--feather 12]
                                [--takes-dir out] [--crf 14] [--debug-mask]
  --mask union     (padrão) pessoa da fonte ∪ personagem gerado (rembg), dilatados por --margin px do canvas
         expanded  pessoa da fonte dilatada por settings.expansion_px (a região que o H3 regenerou) ∪ personagem
  --takes-dir      pasta com os takes escolhidos (padrão out/); pode ser uma versão ampliada (upscale) dos takes,
                   em qualquer resolução com o mesmo aspecto do canvas
  --debug-mask     grava também <saida>_alpha.mp4 (a máscara usada, para revisão)
Saída: <saida> no tamanho de source_sdr.mp4 (1080 no lado menor), áudio original completo.
A máscara é estabilizada no tempo (máximo de t-1, t, t+1) para não "piscar" na borda.
"""
import collections, os, subprocess, sys
import cv2, numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, plate_region, count_frames, history_ok, FPS
from qa_mask import person_mask

args = sys.argv[1:]
def pop(flag, default=None):
    if flag in args:
        i = args.index(flag); v = args[i + 1]; del args[i:i + 2]; return v
    return default
MODE, MARGIN, FEATHER = pop("--mask", "union"), int(pop("--margin", 32)), int(pop("--feather", 12))
TAKES, CRF = pop("--takes-dir"), pop("--crf", "14")
DEBUG = "--debug-mask" in args
args = [a for a in args if a != "--debug-mask"]

job = load_job(args[0])
D = job["_dir"]
out = os.path.abspath(args[1] if len(args) > 1 else os.path.join(D, "final_full.mp4"))
TAKES = TAKES or os.path.join(D, "out")
W, H = job["canvas"]["width"], job["canvas"]["height"]
src = os.path.join(D, job["source"]["sdr"])
cap = cv2.VideoCapture(src)
W0, H0 = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
s, x0, y0 = plate_region(W0, H0, W, H)
M = np.float32([[1 / s, 0, x0 + 0.5 / s - 0.5], [0, 1 / s, y0 + 0.5 / s - 0.5]])   # canvas -> plate
EXP = int(job["settings"].get("expansion_px", 144))
print(f"plate {W0}x{H0} · canvas {W}x{H} em x={x0:.1f} y={y0:.1f} (×{1/s:.3f}) · máscara {MODE}", flush=True)

# ---- plano: lista de (frame da fonte, arquivo do take | None, frame no take) ---------------------------------------
plan, problems = [], []
for shot in job["shots"]:
    if shot["mode"] == "preserve":
        plan += [(f, None, None) for f in range(shot["start"], shot["end"])]
        continue
    for i, seg in enumerate(shot["segments"]):
        t = seg.get("selected_take")
        f = os.path.join(TAKES, f"{t}.mp4") if t else None
        if not f or not os.path.exists(f):
            problems.append(f"{seg['id']}: sem take escolhido em {TAKES}"); continue
        if not history_ok(shot, i):
            problems.append(f"{seg['id']}: o take {t} foi gerado com outro histórico (regere ou selecione de novo)")
        got, exp = count_frames(f), seg["end"] - seg["start"]
        if got != exp:
            problems.append(f"{seg['id']}: {got} frames (esperado {exp})")
        plan += [(seg["start"] + k, f, k) for k in range(exp)]
if problems:
    raise SystemExit("Não dá para compor:\n- " + "\n- ".join(problems))

# ---- saída ---------------------------------------------------------------------------------------------------------
def writer(path, with_audio):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W0}x{H0}", "-r", str(FPS), "-i", "-"]
    if with_audio:
        cmd += ["-i", src, "-map", "0:v", "-map", "1:a:0?", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-crf", CRF, "-preset", "slow", "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)

enc = writer(out, True)
dbg = writer(out.replace(".mp4", "_alpha.mp4"), False) if DEBUG else None
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * MARGIN + 1, 2 * MARGIN + 1)) if MARGIN else None


def raw_mask(plate, gen_canvas):
    src_canvas = cv2.warpAffine(plate, M, (W, H), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_AREA)
    ms, mg = person_mask(src_canvas), person_mask(gen_canvas)
    if MODE == "expanded":
        from scipy.ndimage import distance_transform_edt
        ms = distance_transform_edt(~ms) <= EXP if ms.any() else ms
        m = ms | mg
    else:
        m = (ms | mg).astype(np.uint8)
        m = cv2.dilate(m, kernel) > 0 if kernel is not None else m > 0
    return m.astype(np.uint8)


readers = {}
pending = collections.deque()      # (plate, gen_full|None, mask_canvas|None) com 1 frame de antecedência
prev_mask = None
n_src = 0


def read_plate():
    global n_src
    ok, fr = cap.read()
    if not ok:
        raise SystemExit(f"fonte acabou no frame {n_src}")
    n_src += 1
    return fr


def read_gen(path, k):
    r = readers.get(path)
    if r is None or r[1] != k:
        c = cv2.VideoCapture(path); c.set(cv2.CAP_PROP_POS_FRAMES, k); r = [c, k]; readers[path] = r
    ok, fr = r[0].read(); r[1] += 1
    if not ok:
        raise SystemExit(f"{path}: faltou o frame {k}")
    return fr


def emit(item, mask_prev, mask_next):
    plate, gen, m = item
    if gen is None:
        enc.stdin.write(plate.tobytes())
        if dbg: dbg.stdin.write(np.zeros_like(plate).tobytes())
        return
    stable = m.copy()
    for o in (mask_prev, mask_next):            # estabilização temporal: máximo entre vizinhos do mesmo shot
        if o is not None: stable |= o
    a = cv2.GaussianBlur(stable.astype(np.float32), (2 * FEATHER + 1, 2 * FEATHER + 1), 0) if FEATHER else stable.astype(np.float32)
    gh, gw = gen.shape[:2]
    Mg = M @ np.float32([[W / gw, 0, 0], [0, H / gh, 0], [0, 0, 1]])   # take em qualquer resolução -> plate
    gp = cv2.warpAffine(gen, Mg, (W0, H0), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    ap = cv2.warpAffine(a, M, (W0, H0), flags=cv2.INTER_LINEAR, borderValue=0)[..., None]
    comp = plate.astype(np.float32) * (1 - ap) + gp.astype(np.float32) * ap
    enc.stdin.write(np.clip(comp + 0.5, 0, 255).astype(np.uint8).tobytes())
    if dbg: dbg.stdin.write(np.repeat((ap * 255).astype(np.uint8), 3, axis=2).tobytes())


done = 0
for idx, (f, path, k) in enumerate(plan):
    if f != n_src:
        raise SystemExit(f"plano fora de ordem no frame {f} (fonte em {n_src})")
    plate = read_plate()
    if path is None:
        item = (plate, None, None)
    else:
        gen = read_gen(path, k)
        gen_canvas = cv2.resize(gen, (W, H), interpolation=cv2.INTER_AREA) if gen.shape[:2] != (H, W) else gen
        item = (plate, gen, raw_mask(plate, gen_canvas))
    pending.append(item)
    if len(pending) == 2:
        cur, nxt = pending[0], pending[1]
        emit(cur, prev_mask, nxt[2] if cur[1] is not None and nxt[1] is not None else None)
        prev_mask = cur[2] if nxt[1] is not None else None
        pending.popleft(); done += 1
        if done % 48 == 0: print(f"  {done}/{len(plan)} frames", flush=True)
emit(pending[0], prev_mask, None); done += 1
enc.stdin.close(); enc.wait()
if dbg: dbg.stdin.close(); dbg.wait()
total = count_frames(out)
print(f"final em resolução cheia: {out} · {total} frames (fonte {job['source']['frames']}) "
      f"{'OK' if total == job['source']['frames'] else '<-- DIVERGE'}")
