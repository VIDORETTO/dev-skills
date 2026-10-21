"""QA e escolha automática das variações de âncora (frame da fonte editado com o personagem).

Por quê: a âncora só ajuda se for um frame do PRÓPRIO vídeo com o personagem no lugar: mesma composição, mesma
escala e posição do rosto, mesma abertura de boca. No caso Sherlock, a âncora do Qwen recompôs a cena, mudou a escala,
fechou/abriu a boca diferente e, numa borda, inventou uma 2ª pessoa; o H3 seguiu a âncora e o lip sync caiu de 0,67
para 0,28. Este script mede exatamente esses defeitos e escolhe a melhor variação antes de gastar GPU no vídeo.

Uso (venv): python qa_anchor.py JOB.json <shot|seg> [anchor1.png anchor2.png ...] [--no-paste] [--set] [--json saida.json]
  sem arquivos: usa JOB/out/anchor_<id>_s*.png (saída do `run_job.py anchor`)
  --no-paste  não cola de volta (por padrão grava <âncora>_paste.png: o personagem da âncora colado sobre o frame
              ORIGINAL dentro da máscara suave; o fundo fica idêntico à fonte e pessoas inventadas LONGE da original
              somem. Pessoa inventada encostada na original não dá para separar: a variação é reprovada por "pessoa extra")
  --set       grava a melhor (colada) em seg.anchor no job.json (1º segmento do shot, ou o próprio segmento)

Medidas por variação (contra o frame da fonte no canvas, frames/<id>_0.png):
  fundo_psnr   fundo fora das pessoas igual ao da fonte? (na versão colada é a fonte por construção)
  iou          sobreposição das silhuetas fonte x âncora (recomposição, zoom, deslocamento derrubam)
  rosto_escala tamanho do rosto âncora / fonte (ideal ~1,0; o Qwen tende a afastar a câmera)
  rosto_desloc deslocamento do centro do rosto, em larguras de rosto (ideal ~0)
  boca_dif     |MAR âncora − MAR fonte| (abertura da boca; a âncora fixa a boca do frame 0)
  id_ref/id_src identidade ArcFace contra a referência e contra a pessoa original (vazamento)
  pessoas      rostos detectados na âncora x na fonte (pessoa inventada)
Nota = id_ref − id_src + iou − 2·|escala−1| − deslocamento − 3·boca_dif − 1·pessoa_extra (ordena; não é absoluta).
Reprova (✗) se escala fora de 0,8–1,25, deslocamento > 0,35, iou < 0,5, pessoa extra ou rosto ainda da pessoa original
(id_src > 0,5 ou id_ref − id_src < 0,1).
"""
import glob, json, os, sys, warnings
import cv2, numpy as np
warnings.filterwarnings("ignore")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, save_job, find_segment
from qa_mask import person_mask

_FL = None


def face_geom(img):
    """(centro_x, centro_y, largura, MAR) do maior rosto, em pixels; None se não houver rosto."""
    global _FL
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    from qa_lipsync import face_model
    if _FL is None:
        _FL = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=face_model()), running_mode=vision.RunningMode.IMAGE, num_faces=1))
    r = _FL.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
    if not r.face_landmarks:
        return None
    p, h, w = r.face_landmarks[0], img.shape[0], img.shape[1]
    xs, ys = np.array([q.x * w for q in p]), np.array([q.y * h for q in p])
    v = np.hypot(p[13].x - p[14].x, p[13].y - p[14].y); hz = np.hypot(p[78].x - p[308].x, p[78].y - p[308].y)
    return (xs.mean(), ys.mean(), xs.max() - xs.min(), v / hz if hz else 0.0)


def target_component(ma, ms):
    """Da máscara de pessoas da âncora, só o componente que mais se sobrepõe à pessoa original (descarta inventadas)."""
    n, lab = cv2.connectedComponents(ma.astype(np.uint8), connectivity=8)
    if n <= 2:
        return ma
    near = cv2.dilate(ms.astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool)
    best = max(range(1, n), key=lambda i: ((lab == i) & near).sum())
    return lab == best


def paste_back(src, anc, ms, ma, margin=24, feather=10):
    """Personagem da âncora sobre o frame original: máscara = fonte ∪ personagem da âncora, dilatada e suavizada."""
    ma = target_component(ma, ms)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * margin + 1, 2 * margin + 1))
    m = cv2.dilate((ms | ma).astype(np.uint8), k).astype(np.float32)
    a = cv2.GaussianBlur(m, (2 * feather + 1, 2 * feather + 1), 0)[..., None]
    return np.clip(src * (1 - a) + anc * a + 0.5, 0, 255).astype(np.uint8)


def psnr(a, b, mask):
    if mask.sum() < 100:
        return None
    mse = ((a[mask].astype(np.float32) - b[mask]) ** 2).mean()
    return float(10 * np.log10(255 ** 2 / max(mse, 1e-6)))


def evaluate(src, anc, ref_emb, faces_fn):
    ms, ma = person_mask(src), person_mask(anc)
    bg = ~cv2.dilate((ms | ma).astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
    r = {"fundo_psnr": psnr(src, anc, bg), "iou": float((ms & ma).sum() / max((ms | ma).sum(), 1))}
    gs, ga = face_geom(src), face_geom(anc)
    if gs and ga:
        r["rosto_escala"] = float(ga[2] / gs[2])
        r["rosto_desloc"] = float(np.hypot(ga[0] - gs[0], ga[1] - gs[1]) / gs[2])
        r["boca_dif"] = float(abs(ga[3] - gs[3]))
    fa, fs = faces_fn(anc), faces_fn(src)
    r["pessoas"] = [len(fa), len(fs)]
    if fa and ref_emb is not None:
        r["id_ref"] = float(fa[0].normed_embedding @ ref_emb)
        if fs:
            r["id_src"] = float(fa[0].normed_embedding @ fs[0].normed_embedding)
    return r, ms, ma


def score(r):
    s = r["iou"]
    if r.get("id_ref") is not None:
        s += r["id_ref"] - (r.get("id_src") or 0)
    if "rosto_escala" in r:
        s -= 2 * abs(r["rosto_escala"] - 1) + r["rosto_desloc"] + 3 * r["boca_dif"]
    if r.get("pessoas_colada", r["pessoas"])[0] > r["pessoas"][1]:
        s -= 1
    return round(s, 4)


def verdict(r):
    bad = []
    if "rosto_escala" not in r: bad.append("sem rosto")
    else:
        if not 0.8 <= r["rosto_escala"] <= 1.25: bad.append(f"escala {r['rosto_escala']:.2f}")
        if r["rosto_desloc"] > 0.35: bad.append(f"rosto deslocado {r['rosto_desloc']:.2f}")
    if r["iou"] < 0.5: bad.append(f"silhueta iou {r['iou']:.2f}")
    if r.get("id_src") is not None and (r["id_src"] > 0.5 or (r.get("id_ref") is not None and r["id_ref"] - r["id_src"] < 0.1)):
        bad.append(f"rosto ainda é o original (id fonte {r['id_src']:.2f})")
    if r["pessoas"][0] > r["pessoas"][1] and r.get("pessoas_colada", r["pessoas"])[0] > r["pessoas"][1]:
        bad.append("pessoa extra")
    return bad


def main():
    args = sys.argv[1:]
    out_json = None
    if "--json" in args:
        i = args.index("--json"); out_json = args[i + 1]; del args[i:i + 2]
    flags = {a for a in args if a.startswith("--")}
    args = [a for a in args if not a.startswith("--")]
    job = load_job(args[0]); D = job["_dir"]; target = args[1]
    files = args[2:] or sorted(f for f in glob.glob(os.path.join(D, "out", f"anchor_{target}_s*.png")) if "_paste" not in f)
    if not files:
        raise SystemExit(f"nenhuma âncora para {target}: rode  run_job.py JOB anchor <pod> {target} 11,22,33")
    src_path = os.path.join(D, "frames", f"{target}_0.png")
    src = cv2.imread(src_path)
    if src is None:
        raise SystemExit(f"{src_path} não existe (o prepare.py extrai; ou rode run_job.py anchor, que extrai na hora)")
    import qa_identity
    refs = [job["character"]["image"]] + ([job["character"]["extra_image"]] if job["character"].get("extra_image") else [])
    ref = qa_identity.ref_embedding_arcface([p if os.path.isabs(p) else os.path.join(D, p) for p in refs])
    ref_emb = ref[0] if ref else None
    rows = []
    for f in files:
        anc = cv2.imread(f)
        if anc.shape[:2] != src.shape[:2]:
            anc = cv2.resize(anc, (src.shape[1], src.shape[0]), interpolation=cv2.INTER_LANCZOS4)
        r, ms, ma = evaluate(src, anc, ref_emb, qa_identity.faces)
        r["arquivo"] = os.path.relpath(f, D)
        if "--no-paste" not in flags:
            pasted = paste_back(src, anc, ms, ma)
            pf = f.replace(".png", "_paste.png"); cv2.imwrite(pf, pasted)
            r["colada"] = os.path.relpath(pf, D)
            rp, _, _ = evaluate(src, pasted, ref_emb, qa_identity.faces)
            r["pessoas_colada"] = rp["pessoas"]; r["fundo_psnr_colada"] = rp["fundo_psnr"]
        r["nota"], r["problemas"] = score(r), verdict(r)
        rows.append(r)
    rows.sort(key=lambda r: (not r["problemas"], r["nota"]), reverse=True)
    fmt = lambda v, d=2: "—" if v is None else f"{v:.{d}f}"
    print(f"âncoras de {target} (fonte {os.path.relpath(src_path, D)})")
    for r in rows:
        print(f"  {'✓' if not r['problemas'] else '✗'} {r['arquivo']:34s} nota {r['nota']:6.3f} · iou {fmt(r['iou'])} · "
              f"escala {fmt(r.get('rosto_escala'))} · desloc {fmt(r.get('rosto_desloc'))} · boca {fmt(r.get('boca_dif'), 3)} · "
              f"id {fmt(r.get('id_ref'))}/{fmt(r.get('id_src'))} · fundo {fmt(r['fundo_psnr'], 1)} dB · pessoas {r['pessoas'][0]}"
              + (f"  <-- {', '.join(r['problemas'])}" if r["problemas"] else ""))
    best = rows[0]
    if best["problemas"]:
        print("Nenhuma variação passou: gere mais seeds, endureça o brief ou NÃO use âncora neste shot (05-ancora.md).")
    else:
        use = best.get("colada", best["arquivo"])
        print(f"-> melhor: {use}")
        if "--set" in flags:
            try:
                shot, idx, seg = find_segment(job, target)
            except SystemExit:
                seg = next(s for s in job["shots"] if s["id"] == target)["segments"][0]
            seg["anchor"] = use
            save_job(job, args[0])
            print(f"   gravado em {seg['id']}.anchor (no 1º segmento a âncora só entra com settings.use_anchor=true ou seg --anchor)")
    if out_json:
        json.dump(rows, open(out_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
