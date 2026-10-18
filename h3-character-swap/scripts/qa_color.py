"""QA de cor/brilho do FUNDO: compara luminância (Y) e saturação só fora das pessoas (fonte ∪ gerado, dilatado 180 px).
Por quê só o fundo: a região da pessoa muda de propósito (figurino escuro no lugar de pele clara derruba o Y médio do
quadro em ~30 sem nenhum defeito — medido no caso Sherlock). Defeito de cor real (ex.: fonte HDR não convertida) aparece no fundo.
Uso (venv): python qa_color.py fonte_no_canvas.mp4 gerado.mp4 [passo_frames=12]
Leitura: |ΔY| fundo <= ~5 ok; > 8 = problema de cor/tone mapping/range.
"""
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import cv2, numpy as np
from rembg import new_session, remove
from scipy.ndimage import distance_transform_edt

src, gen = sys.argv[1], sys.argv[2]
STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 12
sess = new_session("u2net_human_seg")
cs, cg = cv2.VideoCapture(src), cv2.VideoCapture(gen)
n, bad = 0, 0
while True:
    a, fs = cs.read(); b, fg = cg.read()
    if not (a and b): break
    if n % STEP == 0:
        if fs.shape != fg.shape: fs = cv2.resize(fs, (fg.shape[1], fg.shape[0]))
        m = (np.asarray(remove(fs, session=sess, only_mask=True)) > 127) | (np.asarray(remove(fg, session=sess, only_mask=True)) > 127)
        bg = ~(distance_transform_edt(~m) <= 180) if m.any() else np.ones(m.shape, bool)
        if bg.mean() < 0.03:
            print(f"frame {n:4d}: fundo visível < 3% (close) — pulado"); n += 1; continue
        hs, hg = cv2.cvtColor(fs, cv2.COLOR_BGR2HSV), cv2.cvtColor(fg, cv2.COLOR_BGR2HSV)
        ys, yg = cv2.cvtColor(fs, cv2.COLOR_BGR2GRAY)[bg].mean(), cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY)[bg].mean()
        ss, sg = hs[..., 1][bg].mean(), hg[..., 1][bg].mean()
        flag = "  <-- COR" if abs(yg - ys) > 8 or abs(sg - ss) > 12 else ""; bad += bool(flag)
        print(f"frame {n:4d}: fundo {bg.mean()*100:3.0f}% · Y fonte {ys:6.1f} gerado {yg:6.1f} (Δ{yg-ys:+5.1f}) · SAT {ss:5.1f}/{sg:5.1f}{flag}")
    n += 1
print("frames com desvio de cor no fundo:", bad)
