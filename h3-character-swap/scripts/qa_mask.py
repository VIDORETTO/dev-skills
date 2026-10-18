"""QA de máscara: % do personagem GERADO que cai fora da máscara aproximada da pessoa ORIGINAL (+expansão).
Acima de ~2% num frame = provável recorte (chapéu/cabelo/ombro cortado pelo fundo original).
Uso: python qa_mask.py fonte_no_canvas.mp4 gerado.mp4 saida.jpg [expansao_px=144] [frames=10,60,...|auto]
"""
import sys, cv2, numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from rembg import new_session, remove
from scipy.ndimage import distance_transform_edt
src, gen, out = sys.argv[1:4]
EXP = int(sys.argv[4]) if len(sys.argv) > 4 else 144
cg = cv2.VideoCapture(gen); N = int(cg.get(cv2.CAP_PROP_FRAME_COUNT))
idx = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 and sys.argv[5] != "auto" else list(range(0, N, max(1, N // 10)))
sess = new_session("u2net_human_seg")
cs = cv2.VideoCapture(src); tiles = []; n = 0; worst = []
while True:
    a, fs = cs.read(); b, fg = cg.read()
    if not (a and b) or n > max(idx): break
    if n in idx:
        if fs.shape != fg.shape: fs = cv2.resize(fs, (fg.shape[1], fg.shape[0]))
        m = np.asarray(remove(fs, session=sess, only_mask=True)) > 127
        exp = distance_transform_edt(~m) <= EXP if m.any() else m
        mg = np.asarray(remove(fg, session=sess, only_mask=True)) > 127
        outside = (mg & ~exp).sum() / max(mg.sum(), 1) * 100
        vis = fg.copy()
        cnts, _ = cv2.findContours(exp.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(vis, cnts, -1, (0, 255, 0), 3)
        cv2.putText(vis, f"f{n} fora:{outside:.1f}%", (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3)
        tiles.append(cv2.resize(vis, (240, int(240 * vis.shape[0] / vis.shape[1]))))
        worst.append((outside, n)); print(f"frame {n}: personagem fora da máscara {outside:.1f}%" + ("  <-- RECORTE?" if outside > 2 else ""))
    n += 1
cv2.imwrite(out, np.hstack(tiles))
print("pior:", max(worst))
