"""QA de máscara: % do personagem GERADO que cai fora da máscara aproximada da pessoa ORIGINAL (+expansão).
Acima de ~2% num frame = provável recorte (chapéu/cabelo/ombro cortado pelo fundo original).
Uso: python qa_mask.py fonte_no_canvas.mp4 gerado.mp4 saida.jpg [expansao_px=144] [frames=10,60,...|auto] [--json saida.json]
"""
import json, sys
import cv2, numpy as np
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from scipy.ndimage import distance_transform_edt

_SESS = None


def person_mask(img):
    """Máscara de pessoa (rembg u2net_human_seg), bool HxW."""
    global _SESS
    from rembg import new_session, remove
    if _SESS is None:
        _SESS = new_session("u2net_human_seg")
    return np.asarray(remove(img, session=_SESS, only_mask=True)) > 127


def check(src, gen, out=None, exp_px=144, idx=None, quiet=False):
    cg = cv2.VideoCapture(gen); N = int(cg.get(cv2.CAP_PROP_FRAME_COUNT))
    idx = idx or list(range(0, N, max(1, N // 10)))
    cs = cv2.VideoCapture(src); tiles = []; n = 0; frames = []
    while True:
        a, fs = cs.read(); b, fg = cg.read()
        if not (a and b) or n > max(idx): break
        if n in idx:
            if fs.shape != fg.shape: fs = cv2.resize(fs, (fg.shape[1], fg.shape[0]))
            m = person_mask(fs)
            exp = distance_transform_edt(~m) <= exp_px if m.any() else m
            mg = person_mask(fg)
            outside = float((mg & ~exp).sum() / max(mg.sum(), 1) * 100)
            frames.append({"frame": n, "outside_pct": outside})
            if not quiet:
                print(f"frame {n}: personagem fora da máscara {outside:.1f}%" + ("  <-- RECORTE?" if outside > 2 else ""))
            if out:
                vis = fg.copy()
                cnts, _ = cv2.findContours(exp.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(vis, cnts, -1, (0, 255, 0), 3)
                cv2.putText(vis, f"f{n} fora:{outside:.1f}%", (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 3)
                tiles.append(cv2.resize(vis, (240, int(240 * vis.shape[0] / vis.shape[1]))))
        n += 1
    if out and tiles:
        cv2.imwrite(out, np.hstack(tiles))
    worst = max(frames, key=lambda f: f["outside_pct"]) if frames else None
    return {"frames": frames, "worst": worst, "outside_max": worst["outside_pct"] if worst else None}


if __name__ == "__main__":
    args = sys.argv[1:]
    out_json = None
    if "--json" in args:
        i = args.index("--json"); out_json = args[i + 1]; del args[i:i + 2]
    src, gen, out = args[:3]
    exp_px = int(args[3]) if len(args) > 3 else 144
    idx = [int(x) for x in args[4].split(",")] if len(args) > 4 and args[4] != "auto" else None
    r = check(src, gen, out, exp_px, idx)
    print("pior:", r["worst"])
    if out_json:
        json.dump(r, open(out_json, "w", encoding="utf-8"), indent=1)
