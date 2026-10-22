"""Utilitários compartilhados pelos scripts da skill h3-character-swap (só stdlib)."""
import json, math, os, subprocess

FPS = 24
PIXEL_BUDGETS = {"480": 500_000, "768": 1_000_000}
HISTORY_FRAMES = 18                     # 17 passados + 1 boundary (padrão oficial)
WINDOWS = tuple(range(22, 363, 17))     # grade H3: 17n+5
HDR_TRANSFERS = {"arib-std-b67", "smpte2084"}


def canvas_dimensions(width, height, resolution):
    """Réplica de h3_character_swap/video.py: canvas mais próximo do ideal, grade de 32 px, dentro do orçamento."""
    budget = PIXEL_BUDGETS[resolution]
    if width * height <= budget and width % 32 == 0 and height % 32 == 0:
        return int(width), int(height)
    ratio = width / height
    iw, ih = math.sqrt(budget * ratio), math.sqrt(budget / ratio)
    cands = []
    for w in range(32, min(16384, budget // 32) + 1, 32):
        max_h = min(16384, budget // w // 32 * 32)
        for h in {max(32, min(max_h, int(ih // 32) * 32)), max(32, min(max_h, math.ceil(ih / 32) * 32))}:
            cands.append((math.log(w / iw) ** 2 + math.log(h / ih) ** 2, -(w * h), w, h))
    _, _, w, h = min(cands)
    return w, h


def cover_crop_filter(w, h):
    """Mesmo scale+crop da preparação oficial (escala para cobrir, recorte central)."""
    return (f"scale=w='ceil(max({w},{h}*dar)-1e-6)':h='ceil(max({h},{w}/dar)-1e-6)':flags=lanczos,"
            f"setsar=1,crop=w={w}:h={h}")


def plate_region(src_w, src_h, w, h):
    """Onde o canvas (w x h) cai no quadro da fonte (src_w x src_h), invertendo o cover_crop_filter.
    Devolve (escala fonte->canvas, x0, y0) em pixels da fonte: canvas_px = (fonte_px - x0) * escala."""
    s = max(w / src_w, h / src_h)
    sw, sh = math.ceil(max(w, h * src_w / src_h) - 1e-6), math.ceil(max(h, w * src_h / src_w) - 1e-6)
    return s, ((sw - w) // 2) / s, ((sh - h) // 2) / s


def item_start(job, item_id):
    """Frame inicial de um shot ou de um segmento."""
    for shot in job["shots"]:
        if shot["id"] == item_id:
            return shot["start"]
        for seg in shot.get("segments", []):
            if seg["id"] == item_id:
                return seg["start"]
    raise SystemExit(f"{item_id} não é shot nem segmento do job")


def ensure_frame(job, item_id, full_res=False):
    """1º frame do shot/segmento no recorte do canvas. full_res=False: frames/<id>_0.png no tamanho do canvas
    (é o que o H3 recebe). full_res=True: mesmo recorte na escala da fonte (anchor_kit/<id>_frame.png, para editores
    de imagem externos trabalharem com mais pixels). Extrai na hora se não existir."""
    D, W, H = job["_dir"], job["canvas"]["width"], job["canvas"]["height"]
    src = os.path.join(D, job["source"]["sdr"])
    path = os.path.join(D, "anchor_kit", f"{item_id}_frame.png") if full_res else os.path.join(D, "frames", f"{item_id}_0.png")
    if os.path.exists(path):
        return path
    if full_res:
        info = video_info(src)
        s, _, _ = plate_region(info["width"], info["height"], W, H)
        W, H = int(round(W / s / 2) * 2), int(round(H / s / 2) * 2)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
         f"select='eq(n\\,{item_start(job, item_id)})',{cover_crop_filter(W, H)}",
         "-fps_mode", "passthrough", "-frames:v", "1", path])
    return path


def take_record(seg, take):
    return next((t for t in seg.get("takes", []) if t["take"] == take), None)


def history_ok(shot, idx):
    """O take escolhido do segmento idx foi gerado a partir do take escolhido do segmento anterior?"""
    if idx == 0:
        return True
    seg, prev = shot["segments"][idx], shot["segments"][idx - 1]
    rec = take_record(seg, seg.get("selected_take"))
    # takes antigos (antes do campo history_from) não têm a informação: não dá para provar, aceita
    return rec is None or "history_from" not in rec or rec["history_from"] == prev.get("selected_take")


def vpy():
    """Python do venv local (QA e análise). Ordem: env H3_VPY, venv padrão do Windows, python atual."""
    if os.environ.get("H3_VPY"):
        return os.environ["H3_VPY"]
    win = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "cswap-venv", "Scripts", "python.exe")
    import sys
    return win if os.path.exists(win) else sys.executable


def window_for(target, history):
    """Menor janela 17n+5 que comporta o alvo (+1 boundary se houver histórico)."""
    need = target + (1 if history else 0)
    return next(v for v in WINDOWS if v >= need and v > history)


def ffprobe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def video_info(path):
    d = ffprobe(path)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    rot = next((s.get("rotation", 0) for s in v.get("side_data_list", []) if "rotation" in s), 0)
    w, h = v["width"], v["height"]
    if round(rot) % 180 == 90:
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    return {"width": w, "height": h, "fps": float(num) / float(den or 1) if float(den or 1) else 0.0,
            "duration": float(d["format"].get("duration", 0)), "transfer": v.get("color_transfer", ""),
            "primaries": v.get("color_primaries", ""), "pix_fmt": v.get("pix_fmt", ""),
            "hdr": v.get("color_transfer", "") in HDR_TRANSFERS,
            "has_audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def count_frames(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return int(out.strip().strip(","))


def run(cmd):
    print("$", " ".join(str(c) for c in cmd)[:300], flush=True)
    subprocess.run(cmd, check=True)


def load_job(path):
    with open(path, encoding="utf-8") as f:
        job = json.load(f)
    job["_dir"] = os.path.dirname(os.path.abspath(path))
    return job


def save_job(job, path):
    data = {k: v for k, v in job.items() if not k.startswith("_")}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def segments(job):
    for shot in job["shots"]:
        if shot["mode"] == "generate":
            for i, seg in enumerate(shot["segments"]):
                yield shot, i, seg


def find_segment(job, seg_id):
    for shot, i, seg in segments(job):
        if seg["id"] == seg_id:
            return shot, i, seg
    raise SystemExit(f"segmento {seg_id} não existe no job")
