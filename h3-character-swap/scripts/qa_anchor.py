"""QA e escolha automática das variações de âncora (frame da fonte editado com o personagem).

Por quê: a âncora só ajuda se for um frame do PRÓPRIO vídeo com o personagem no lugar: mesma composição, mesma
escala e posição do rosto, mesma abertura de boca. No caso Sherlock, a âncora do Qwen recompôs a cena, mudou a escala,
fechou/abriu a boca diferente e, numa borda, inventou uma 2ª pessoa; o H3 seguiu a âncora e o lip sync caiu de 0,67
para 0,28. Este script mede exatamente esses defeitos e escolhe a melhor variação antes de gastar GPU no vídeo.

Uso (venv): python qa_anchor.py JOB.json <shot|seg> [anchor1.png anchor2.png ...] [--no-paste] [--set] [--json saida.json]
Saídas: a tabela, as versões _paste.png, a folha de revisão visual review_<id>.jpg (original | editada | colada | rosto e
boca ampliados, por variação: o agente DEVE abrir e conferir a checklist do 05-ancora.md) e, para cada problema, a
frase pronta para pedir a correção ao editor (Nano Banana / GPT Image).
  sem arquivos: usa JOB/out/anchor_<id>_s*.png (saída do `run_job.py anchor`, Qwen no pod) e
               JOB/anchors_user/<id>*.png|jpg|webp (feitas pelo usuário no Nano Banana / GPT Image; ver anchor_kit.py)
  Toda variação é ALINHADA ao frame original antes de medir (ORB + RANSAC no fundo, transformação de similaridade):
  editores externos devolvem outro tamanho/proporção (GPT Image: 2:3) ou reenquadram de leve. Sem pontos suficientes,
  cai para redimensionar com recorte central e avisa.
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
  nitidez      nitidez do rosto na âncora / na fonte (variância do Laplaciano; < 0,5 = borrado ou plastificado)
Nota = id_ref − id_src + iou − 2·|escala−1| − deslocamento − 3·boca_dif − 1·pessoa_extra (ordena; não é absoluta).
Reprova (✗) se escala fora de 0,8–1,25, deslocamento > 0,35, iou < 0,5, pessoa extra, rosto com < 35% da nitidez da
fonte, edição que cortou > 5% da pessoa
(bordas recortadas pelo editor: ali ficaria a pessoa original) ou rosto ainda da pessoa original
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
from h3common import load_job, save_job, find_segment, ensure_frame
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


def align(src, anc, ms):
    """Leva a âncora (qualquer tamanho/proporção) para o enquadramento do frame original.
    Casa pontos ORB no FUNDO do frame (fora da pessoa, que mudou de propósito) e estima escala+rotação+translação."""
    H, W = src.shape[:2]
    # pré-escala: mesma altura do frame, para os descritores ORB trabalharem em escala parecida
    k = H / anc.shape[0]
    a0 = cv2.resize(anc, (max(1, int(round(anc.shape[1] * k))), H), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_LANCZOS4)
    g1, g2 = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY), cv2.cvtColor(a0, cv2.COLOR_BGR2GRAY)
    bg = (~cv2.dilate(ms.astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool)).astype(np.uint8) * 255
    orb = cv2.ORB_create(5000)
    k1, d1 = orb.detectAndCompute(g1, bg)
    k2, d2 = orb.detectAndCompute(g2, None)
    info = {"metodo": "redimensionado", "inliers": 0}
    if d1 is not None and d2 is not None and len(k1) >= 20 and len(k2) >= 20:
        m = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d2, d1), key=lambda x: x.distance)[:800]
        if len(m) >= 20:
            p2 = np.float32([k2[x.queryIdx].pt for x in m]); p1 = np.float32([k1[x.trainIdx].pt for x in m])
            M, inl = cv2.estimateAffinePartial2D(p2, p1, method=cv2.RANSAC, ransacReprojThreshold=3.0, maxIters=5000)
            n = int(inl.sum()) if inl is not None else 0
            if M is not None and n >= 25:
                sc = float(np.hypot(M[0, 0], M[0, 1]))
                info = {"metodo": "alinhado", "inliers": n, "escala": sc * k, "rot_graus": float(np.degrees(np.arctan2(M[1, 0], M[0, 0]))),
                        "tx": float(M[0, 2]), "ty": float(M[1, 2])}
                valid = cv2.warpAffine(np.ones(a0.shape[:2], np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0) > 0.99
                return cv2.warpAffine(a0, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE), info, valid
    # sem fundo reconhecível: cobre o frame e recorta no centro (proporção diferente perde as bordas)
    s = max(W / anc.shape[1], H / anc.shape[0])
    r = cv2.resize(anc, (int(np.ceil(anc.shape[1] * s)), int(np.ceil(anc.shape[0] * s))), interpolation=cv2.INTER_LANCZOS4)
    y0, x0 = (r.shape[0] - H) // 2, (r.shape[1] - W) // 2
    return r[y0:y0 + H, x0:x0 + W], info, np.ones((H, W), bool)


def target_component(ma, ms):
    """Da máscara de pessoas da âncora, só o componente que mais se sobrepõe à pessoa original (descarta inventadas)."""
    n, lab = cv2.connectedComponents(ma.astype(np.uint8), connectivity=8)
    if n <= 2:
        return ma
    near = cv2.dilate(ms.astype(np.uint8), np.ones((41, 41), np.uint8)).astype(bool)
    best = max(range(1, n), key=lambda i: ((lab == i) & near).sum())
    return lab == best


def paste_back(src, anc, ms, ma, margin=24, feather=10, valid=None):
    """Personagem da âncora sobre o frame original: máscara = fonte ∪ personagem da âncora, dilatada e suavizada.
    valid = onde a âncora alinhada tem conteúdo real (fora disso, p.ex. faixas que o editor recortou, fica a fonte)."""
    ma = target_component(ma, ms)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * margin + 1, 2 * margin + 1))
    m = cv2.dilate((ms | ma).astype(np.uint8), k).astype(np.float32)
    if valid is not None:
        m *= cv2.erode(valid.astype(np.uint8), np.ones((2 * feather + 1, 2 * feather + 1), np.uint8))
    a = cv2.GaussianBlur(m, (2 * feather + 1, 2 * feather + 1), 0)[..., None]
    return np.clip(src * (1 - a) + anc * a + 0.5, 0, 255).astype(np.uint8)


def psnr(a, b, mask):
    if mask.sum() < 100:
        return None
    mse = ((a[mask].astype(np.float32) - b[mask]) ** 2).mean()
    return float(10 * np.log10(255 ** 2 / max(mse, 1e-6)))


def evaluate(src, anc, ref_emb, faces_fn, valid=None):
    ms, ma = person_mask(src), person_mask(anc)
    if valid is not None:
        ma &= valid
    bg = ~cv2.dilate((ms | ma).astype(np.uint8), np.ones((31, 31), np.uint8)).astype(bool)
    r = {"fundo_psnr": psnr(src, anc, bg), "iou": float((ms & ma).sum() / max((ms | ma).sum(), 1))}
    gs, ga = face_geom(src), face_geom(anc)
    if gs and ga:
        r["rosto_escala"] = float(ga[2] / gs[2])
        r["rosto_desloc"] = float(np.hypot(ga[0] - gs[0], ga[1] - gs[1]) / gs[2])
        r["boca_dif"] = float(abs(ga[3] - gs[3]))
        r["boca_mais_aberta_na_fonte"] = bool(gs[3] > ga[3])
        r["nitidez"] = sharpness_ratio(src, anc, gs)
    fa, fs = faces_fn(anc), faces_fn(src)
    r["pessoas"] = [len(fa), len(fs)]
    if fa and ref_emb is not None:
        r["id_ref"] = float(fa[0].normed_embedding @ ref_emb)
        if fs:
            r["id_src"] = float(fa[0].normed_embedding @ fs[0].normed_embedding)
    return r, ms, ma


def face_box(src, g, k=1.6):
    """Quadrado em volta do rosto (k larguras de rosto), recortado aos limites da imagem."""
    cx, cy, w = g[0], g[1], g[2] * k
    H, W = src.shape[:2]
    x0, y0 = int(max(0, cx - w / 2)), int(max(0, cy - w / 2))
    return x0, y0, int(min(W, cx + w / 2)), int(min(H, cy + w / 2))


def sharpness_ratio(src, anc, g):
    """Nitidez do rosto na âncora / na fonte (variância do Laplaciano). < 0,5 = borrado ou "plastificado"."""
    x0, y0, x1, y1 = face_box(src, g, 1.0)
    lap = lambda im: cv2.Laplacian(cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
    base = lap(src)
    return float(lap(anc) / base) if base > 1e-6 else None


# Como pedir a correção ao editor (Nano Banana / GPT Image): (explicação, frase para colar no mesmo chat do editor)
HINTS = {
    "enquadramento": ("o editor mudou o enquadramento (zoom, posição ou tamanho da pessoa)",
                      "The framing changed. Use Image 1 exactly as it is: same crop and zoom. The character must occupy "
                      "exactly the same place and size as the original person."),
    "cortou": ("o editor recortou o quadro e cortou parte da pessoa",
               "Do not crop the image. Keep all of Image 1; if you need another aspect ratio, add plain borders instead."),
    "original": ("a pessoa original continua lá (a troca não aconteceu ou ficou misturada)",
                 "The original person is still visible. Replace the person's face, hair and clothes completely with the "
                 "character from Image 2."),
    "extra": ("o editor inventou outra pessoa",
              "Do not add any other person. Only one person, in the original person's place."),
    "sem_rosto": ("não dá para ver o rosto do personagem",
                  "The character's face must be clearly visible, at the same angle as the person in Image 1."),
    "boca_aberta": ("a boca está mais fechada do que no frame original",
                    "Match the mouth of the person in Image 1 exactly: lips slightly open, mid-word, as in Image 1."),
    "boca_fechada": ("a boca está mais aberta do que no frame original",
                     "Match the mouth of the person in Image 1 exactly: lips closed or relaxed, as in Image 1."),
    "nitidez": ("o rosto saiu borrado ou com aparência plástica",
                "Keep the image sharp and photographic at full resolution, with natural skin texture and fine fabric "
                "detail; no blur, no smoothing."),
    "resolucao": ("a imagem voltou em resolução menor que o frame",
                  "Return the edited image at the highest resolution available, without downscaling or cropping."),
}


def hints_for(r):
    keys = []
    for p in r["problemas"]:
        if p.startswith(("escala", "rosto deslocado", "silhueta")): keys.append("enquadramento")
        elif p.startswith("edição cortou"): keys.append("cortou")
        elif p.startswith("rosto ainda"): keys.append("original")
        elif p == "pessoa extra": keys.append("extra")
        elif p == "sem rosto": keys.append("sem_rosto")
        elif p.startswith("rosto borrado"): keys.append("nitidez")
    if r.get("boca_dif", 0) > 0.06:
        keys.append("boca_aberta" if r.get("boca_mais_aberta_na_fonte") else "boca_fechada")
    if r.get("nitidez") is not None and r["nitidez"] < 0.6: keys.append("nitidez")
    if r.get("alinhamento", {}).get("escala", 1) > 1.05: keys.append("resolucao")
    return list(dict.fromkeys(keys))


def review_sheet(path, src, rows, imgs, gs):
    """Folha para a revisão VISUAL do agente: por variação, original | editada (alinhada) | colada | rosto e boca
    ampliados (original x colada). O agente abre a imagem e confere a checklist do 05-ancora.md."""
    H, W = src.shape[:2]; tw = 240; th = int(tw * H / W); fz = th // 3   # 2 rostos + 2 bocas (meia altura) = th
    def lab(im, t, ok=None):
        im = im.copy(); c = (0, 170, 0) if ok else (0, 0, 220) if ok is not None else (40, 40, 40)
        cv2.rectangle(im, (0, 0), (im.shape[1], 26), (255, 255, 255), -1)
        cv2.putText(im, t, (5, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.5, c, 1, cv2.LINE_AA)
        return im
    def face(im, k, size):
        if not gs: return np.full((size, size, 3), 200, np.uint8)
        x0, y0, x1, y1 = face_box(im, gs, k)
        return cv2.resize(im[y0:y1, x0:x1], (size, size), interpolation=cv2.INTER_CUBIC)
    def mouth(im):
        if not gs: return np.full((fz // 2, fz, 3), 200, np.uint8)
        cx, cy, w = gs[0], gs[1] + gs[2] * 0.28, gs[2] * 0.7
        x0, y0 = int(max(0, cx - w / 2)), int(max(0, cy - w / 4))
        return cv2.resize(im[y0:int(min(H, cy + w / 4)), x0:int(min(W, cx + w / 2))], (fz, fz // 2), interpolation=cv2.INTER_CUBIC)
    blocks = []
    for r in rows:
        al, pasted = imgs[r["arquivo"]]
        ok = not r["problemas"]
        sm = lambda im: cv2.resize(im, (tw, th), interpolation=cv2.INTER_AREA)
        faces = np.vstack([lab(face(src, 1.6, fz), "rosto original"), lab(face(pasted, 1.6, fz), "rosto colado", ok),
                           lab(mouth(src), "boca original"), lab(mouth(pasted), "boca colada", ok)])
        faces = cv2.copyMakeBorder(faces, 0, max(0, th - faces.shape[0]), 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))[:th]
        row = np.hstack([lab(sm(src), "original"), lab(sm(al), "editada (alinhada)"),
                         lab(sm(pasted), ("OK " if ok else "REPROVADA ") + f"nota {r['nota']:.2f}", ok), faces])
        title = np.full((30, row.shape[1], 3), 255, np.uint8)
        cv2.putText(title, f"{r['arquivo']}  " + ("; ".join(r["problemas"]) if r["problemas"] else "sem problema medido"),
                    (6, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 220) if r["problemas"] else (0, 140, 0), 1, cv2.LINE_AA)
        blocks.append(np.vstack([title, row, np.full((8, row.shape[1], 3), 255, np.uint8)]))
    cv2.imwrite(path, np.vstack(blocks), [cv2.IMWRITE_JPEG_QUALITY, 90])


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
    if r.get("pessoa_cortada", 0) > 0.05: bad.append(f"edição cortou {r['pessoa_cortada']*100:.0f}% da pessoa")
    if r.get("nitidez") is not None and r["nitidez"] < 0.35: bad.append(f"rosto borrado ({r['nitidez']:.0%} da nitidez)")
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
    user = [f for ext in ("png", "jpg", "jpeg", "webp") for f in glob.glob(os.path.join(D, "anchors_user", f"{target}*.{ext}"))]
    given = [f if os.path.exists(f) else os.path.join(D, f) for f in args[2:]]   # caminho atual ou relativo ao job
    files = given or sorted(f for f in glob.glob(os.path.join(D, "out", f"anchor_{target}_s*.png")) + user
                               if "_paste" not in f and "_alinhada" not in f)
    if not files:
        raise SystemExit(f"nenhuma âncora para {target}: rode  run_job.py JOB anchor <pod> {target} 11,22,33")
    src_path = ensure_frame(job, target)
    src = cv2.imread(src_path)
    if src is None:
        raise SystemExit(f"{src_path} não existe (o prepare.py extrai; ou rode run_job.py anchor, que extrai na hora)")
    import qa_identity
    refs = [job["character"]["image"]] + ([job["character"]["extra_image"]] if job["character"].get("extra_image") else [])
    ref = qa_identity.ref_embedding_arcface([p if os.path.isabs(p) else os.path.join(D, p) for p in refs])
    ref_emb = ref[0] if ref else None
    rows, imgs = [], {}
    gs_src = face_geom(src)
    for f in files:
        anc = cv2.imread(f)
        if anc is None:
            print(f"  ✗ não abriu {f}"); continue
        anc, al, valid = align(src, anc, person_mask(src))
        if al["metodo"] == "redimensionado" or abs(al.get("escala", 1) - 1) > 0.01 or abs(al.get("tx", 0)) > 1 or abs(al.get("ty", 0)) > 1:
            base, _ = os.path.splitext(f); cv2.imwrite(base + "_alinhada.png", anc)   # o que de fato foi medido/colado
        r, ms, ma = evaluate(src, anc, ref_emb, qa_identity.faces, valid)
        cut = float((ms & ~valid).sum() / max(ms.sum(), 1))
        r["pessoa_cortada"] = cut
        r["arquivo"] = os.path.relpath(f, D)
        r["alinhamento"] = al
        if al["metodo"] == "redimensionado":
            r.setdefault("avisos", []).append("sem pontos de fundo para alinhar: redimensionada com recorte central")
        if cut > 0.01:
            r.setdefault("avisos", []).append(f"a edição cortou {cut*100:.0f}% da pessoa (bordas do quadro): ali fica a pessoa "
                                              "ORIGINAL; peça ao editor bordas em vez de recorte")
        if r.get("nitidez") is not None and r["nitidez"] < 0.6:
            r.setdefault("avisos", []).append(f"rosto com {r['nitidez']:.0%} da nitidez do original: borrado/plastificado")
        if al.get("escala", 1) > 1.05:
            r.setdefault("avisos", []).append(f"âncora ampliada {al['escala']:.2f}x para caber no frame: menos detalhe "
                                              "(peça ao editor a resolução máxima, sem recortar)")
        if "--no-paste" not in flags:
            pasted = paste_back(src, anc, ms, ma, valid=valid)
            pf = os.path.splitext(f)[0] + "_paste.png"; cv2.imwrite(pf, pasted)
            r["colada"] = os.path.relpath(pf, D)
            rp, _, _ = evaluate(src, pasted, ref_emb, qa_identity.faces)
            r["pessoas_colada"] = rp["pessoas"]; r["fundo_psnr_colada"] = rp["fundo_psnr"]
        else:
            pasted = anc
        imgs[r["arquivo"]] = (anc, pasted)
        r["nota"], r["problemas"] = score(r), verdict(r)
        rows.append(r)
    if not rows:
        raise SystemExit("nenhuma variação pôde ser lida")
    rows.sort(key=lambda r: (not r["problemas"], r["nota"]), reverse=True)
    fmt = lambda v, d=2: "—" if v is None else f"{v:.{d}f}"
    print(f"âncoras de {target} (fonte {os.path.relpath(src_path, D)})")
    for r in rows:
        print(f"  {'✓' if not r['problemas'] else '✗'} {r['arquivo']:34s} nota {r['nota']:6.3f} · iou {fmt(r['iou'])} · "
              f"escala {fmt(r.get('rosto_escala'))} · desloc {fmt(r.get('rosto_desloc'))} · boca {fmt(r.get('boca_dif'), 3)} · "
              f"id {fmt(r.get('id_ref'))}/{fmt(r.get('id_src'))} · nitidez {fmt(r.get('nitidez'))} · pessoas {r['pessoas'][0]}"
              + (f"  <-- {', '.join(r['problemas'])}" if r["problemas"] else ""))
        al = r["alinhamento"]
        if al["metodo"] == "alinhado" and (abs(al["escala"] - 1) > 0.01 or abs(al["tx"]) > 1 or abs(al["ty"]) > 1):
            print(f"      alinhada ao frame: escala {al['escala']:.3f} · rotação {al['rot_graus']:+.1f}° · "
                  f"desloc ({al['tx']:+.0f}, {al['ty']:+.0f}) px · {al['inliers']} pontos")
        for w in r.get("avisos", []):
            print(f"      aviso: {w}")
    for r in rows:
        r["correcoes"] = [{"motivo": HINTS[k][0], "pedir_ao_editor": HINTS[k][1]} for k in hints_for(r)]
    sheet_dir = os.path.dirname(rows[0]["arquivo"]) or "out"
    sheet = os.path.join(D, sheet_dir, f"review_{target}.jpg")
    review_sheet(sheet, src, rows, imgs, gs_src)
    print(f"\nfolha de revisão VISUAL (abrir e conferir a checklist do 05-ancora.md): {sheet}")
    best = rows[0]
    fixes = {c["pedir_ao_editor"]: c["motivo"] for r in rows for c in r["correcoes"]}
    if fixes:
        print("\nPara pedir novas variações, mande no MESMO chat do editor (motivo → frase):")
        for en, pt in fixes.items():
            print(f"  - {pt}:\n    {en}")
    if best["problemas"]:
        print("Nenhuma variação passou: gere outras (Qwen: mais seeds; editor externo: novas variações com o mesmo prompt) "
              "ou NÃO use âncora neste shot (05-ancora.md).")
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
