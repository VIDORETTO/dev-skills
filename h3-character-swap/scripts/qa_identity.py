"""QA de identidade: o rosto gerado é o PERSONAGEM da referência, e não a pessoa original?

Backend `arcface` (padrão, rosto realista): InsightFace buffalo_l (ArcFace). Para cada frame amostrado do gerado, mede a
similaridade de cosseno do maior rosto contra a referência (média de todos os rostos achados na imagem/folha de
referência) e contra o rosto da FONTE no mesmo frame (vazamento da identidade original).
Backend `dino` (personagem cartoon/3D/estilizado, onde o ArcFace não acha rosto): DINOv2 ViT-S/14 no recorte da pessoa.

Uso (venv): python qa_identity.py referencia.png gerado.mp4 [fonte_no_canvas.mp4] [--step 6] [--backend arcface|dino]
            [--extra ref2.png,ref3.png] [--json saida.json]
Leitura (arcface): id_ref >= ~0,45 bom · < ~0,30 identidade fraca. A margem id_ref − id_fonte deve ser claramente
positiva (>= ~0,2); margem perto de 0 ou negativa = o rosto original está vazando. Quedas localizadas = deriva (giro,
oclusão, fim de janela longa). Os limiares são de referência para rostos realistas; para referência pintada/ilustrada
os valores absolutos caem; compare takes entre si.
"""
import json, os, sys, warnings
import cv2, numpy as np
warnings.filterwarnings("ignore")  # avisos de depreciação do insightface/skimage
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_APP = None
_DINO = None


def arcface():
    global _APP
    if _APP is None:
        from insightface.app import FaceAnalysis
        _APP = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"],
                            providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
        _APP.prepare(ctx_id=0, det_size=(640, 640))
    return _APP


def faces(img):
    return sorted(arcface().get(img), key=lambda f: -(f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))


def ref_embedding_arcface(paths):
    """Média normalizada dos rostos de todas as imagens de referência (folha com várias vistas conta cada rosto)."""
    embs = []
    for p in paths:
        img = cv2.imread(p)
        if img is None:
            raise SystemExit(f"não abriu {p}")
        # folhas grandes: o detector trabalha melhor com o lado maior <= 2048
        s = min(1.0, 2048 / max(img.shape[:2]))
        if s < 1: img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        embs += [f.normed_embedding for f in faces(img) if f.det_score >= 0.5]
    if not embs:
        return None
    e = np.mean(embs, axis=0)
    return e / np.linalg.norm(e), len(embs)


def dino():
    global _DINO
    if _DINO is None:
        import torch
        _DINO = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14").eval()
    return _DINO


def dino_embedding(img):
    """Embedding DINOv2 do recorte da pessoa (bbox da máscara rembg) em 224x224."""
    import torch
    from qa_mask import person_mask
    m = person_mask(img)
    if m.any():
        ys, xs = np.where(m)
        img = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    x = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), (224, 224), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
    with torch.no_grad():
        e = dino()(torch.from_numpy(x.transpose(2, 0, 1)[None]).float())[0].numpy()
    return e / np.linalg.norm(e)


def measure(ref_paths, gen, src=None, step=6, backend="arcface", fps=24, quiet=False):
    if backend == "arcface":
        r = ref_embedding_arcface(ref_paths)
        if r is None:
            if not quiet: print("ArcFace não achou rosto na referência -> usando backend dino (personagem estilizado?)")
            backend = "dino"
        else:
            ref, nref = r
    if backend == "dino":
        refs = [dino_embedding(cv2.imread(p)) for p in ref_paths]
        ref = np.mean(refs, axis=0); ref /= np.linalg.norm(ref); nref = len(refs)
    cg = cv2.VideoCapture(gen); cs = cv2.VideoCapture(src) if src else None
    rows, n = [], 0
    while True:
        ok, fg = cg.read()
        fs = cs.read()[1] if cs is not None else None
        if not ok: break
        if n % step == 0:
            row = {"frame": n, "id_ref": None, "id_src": None}
            if backend == "arcface":
                fgs = faces(fg)
                if fgs:
                    e = fgs[0].normed_embedding
                    row["id_ref"] = float(e @ ref)
                    if fs is not None:
                        fss = faces(fs)
                        if fss: row["id_src"] = float(e @ fss[0].normed_embedding)
            else:
                e = dino_embedding(fg)
                row["id_ref"] = float(e @ ref)
                if fs is not None: row["id_src"] = float(e @ dino_embedding(fs))
            rows.append(row)
        n += 1
    vals = [r["id_ref"] for r in rows if r["id_ref"] is not None]
    src_vals = [r["id_src"] for r in rows if r["id_src"] is not None]
    res = {"backend": backend, "ref_faces": nref, "frames": n, "sampled": len(rows),
           "face_found": len(vals) / max(len(rows), 1),
           "id_ref_mean": float(np.mean(vals)) if vals else None,
           "id_ref_p10": float(np.percentile(vals, 10)) if vals else None,
           "id_ref_min": float(np.min(vals)) if vals else None,
           "id_src_mean": float(np.mean(src_vals)) if src_vals else None,
           "rows": rows}
    res["margin"] = (res["id_ref_mean"] - res["id_src_mean"]) if vals and src_vals else None
    # janelas de 1 s
    res["windows"] = []
    for s in range(0, n, int(fps)):
        w = [r["id_ref"] for r in rows if s <= r["frame"] < s + fps and r["id_ref"] is not None]
        res["windows"].append({"start": s, "end": s + int(fps) - 1, "id_ref": float(np.mean(w)) if w else None})
    return res


def report(r):
    print(f"backend {r['backend']} · rostos na referência {r['ref_faces']} · frames amostrados {r['sampled']} "
          f"· rosto achado {r['face_found']*100:.0f}%")
    if r["id_ref_mean"] is None:
        print("nenhum rosto medido no gerado"); return
    print(f"identidade x referência: média {r['id_ref_mean']:.3f} · p10 {r['id_ref_p10']:.3f} · mín {r['id_ref_min']:.3f}")
    if r["id_src_mean"] is not None:
        flag = "  <-- VAZAMENTO DA PESSOA ORIGINAL?" if r["margin"] < 0.2 else ""
        print(f"identidade x fonte (vazamento): média {r['id_src_mean']:.3f} · margem {r['margin']:+.3f}{flag}")
    lo = r["id_ref_mean"] - 0.1
    for w in r["windows"]:
        if w["id_ref"] is None: continue
        print(f"{w['start']:4d}-{w['end']:4d}  id {w['id_ref']:.3f}" + ("  <-- QUEDA" if w["id_ref"] < lo else ""))


if __name__ == "__main__":
    args = sys.argv[1:]
    def pop(flag, default=None):
        if flag in args:
            i = args.index(flag); v = args[i + 1]; del args[i:i + 2]; return v
        return default
    out_json, step, backend = pop("--json"), int(pop("--step", 6)), pop("--backend", "arcface")
    extra = [p for p in (pop("--extra", "") or "").split(",") if p]
    ref, gen = args[0], args[1]
    src = args[2] if len(args) > 2 else None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    r = measure([ref] + extra, gen, src, step, backend)
    report(r)
    if out_json:
        json.dump(r, open(out_json, "w", encoding="utf-8"), indent=1)
