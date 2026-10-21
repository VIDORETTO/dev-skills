"""Orquestra a geração no ComfyUI do pod a partir de job.json (só stdlib; roda com qualquer python 3.10+).

Comandos:
  <pod> = ID do pod do RunPod ou URL completa de um ComfyUI (ex.: http://127.0.0.1:8188)
  python run_job.py JOB.json check  <pod>                      # nós e modelos presentes?
  python run_job.py JOB.json prompt <seg>                      # imprime o prompt do segmento (sem GPU)
  python run_job.py JOB.json anchor <pod> <shot|seg> 11,22,33  # variações de âncora (Qwen-Image-Edit) -> out/anchor_<id>_s<seed>.png
                                                               #   shot = 1º frame do shot; seg = 1º frame do segmento (âncora no meio do shot)
  python run_job.py JOB.json seg    <pod> <seg> [--seed N] [--anchor f.png] [--expansion PX] [--guide MODO] [--no-turbo]
                                                               # 1 take -> out/<seg>_s<seed>[_guia][_base][_h<origem>].mp4
                                                               #   (+ histórico salvo no pod; _hXXXX = continuação, marca do take anterior usado)
  python run_job.py JOB.json best   <pod> <seg> 11,22,33 [mesmas opções do seg]
                                                               # best-of-N: gera 1 take por seed, roda a QA (qa_take.py) e escolhe o melhor
  python run_job.py JOB.json select <seg> <take>               # marca o take escolhido (ex.: A1_s31337); invalida os seguintes
  python run_job.py JOB.json chain  <pod> <shot> [--seeds 11,22] [opções do seg]
                                                               # gera os segmentos que faltam do shot em sequência (com --seeds: best-of-N em cada)
  python run_job.py JOB.json lipfix <pod> <seg> <t0> <t1> [--steps 20] [--seed N]
                                                               # reparo de boca (LatentSync 1.6, pod criado com make_pod --latentsync)
                                                               #   no trecho t0–t1 s (relativo ao segmento) do take escolhido -> novo take <take>_lf

Opções: --guide depth|mesh|depth_mesh usa o clipe de clips_guide/<modo>/ (make_guide.py) só na geração; o SAM continua
no clipe original. --no-turbo = base sem Turbo, 20 steps res_multistep/simple. A QA do best usa o python do venv local
(env H3_VPY; padrão %LOCALAPPDATA%/Temp/cswap-venv).

Regras embutidas (ver SKILL.md): modo segmento sempre; continuação usa o histórico do take ESCOLHIDO do segmento
anterior e registra de qual take veio (history_from); saída lida SOMENTE do nó 807; user-agent de curl (o proxy do
RunPod devolve 403 ao urllib).
"""
import hashlib, json, os, subprocess, sys, time, uuid, urllib.request, urllib.parse
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import (load_job, save_job, find_segment, take_record, history_ok, vpy, cover_crop_filter, run,
                      HISTORY_FRAMES, FPS)

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(SKILL, "assets", "h3_character_swap.api.json")
UA = {"User-Agent": "curl/8.9.1"}
GUIDES = ("depth", "mesh", "depth_mesh")

JOB_PATH, CMD = sys.argv[1], sys.argv[2]
job = load_job(JOB_PATH)
D = job["_dir"]
os.makedirs(os.path.join(D, "out"), exist_ok=True)


def opt(name, default=None):
    if name in sys.argv:
        return sys.argv[sys.argv.index(name) + 1]
    return default


class Pod:
    def __init__(self, pod):
        # ID do pod do RunPod, ou uma URL completa (ComfyUI local/outro provedor: http://127.0.0.1:8188)
        self.base = pod.rstrip("/") if pod.startswith(("http://", "https://")) else f"https://{pod}-8188.proxy.runpod.net"

    def req(self, path, data=None, headers=None):
        r = urllib.request.Request(self.base + path, data=data, headers={**UA, **(headers or {})})
        with urllib.request.urlopen(r, timeout=600) as resp:
            return resp.read()

    def upload(self, path, name=None):
        name = name or os.path.basename(path)
        b = uuid.uuid4().hex
        body = (f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\n"
                f"Content-Type: application/octet-stream\r\n\r\n").encode() + open(path, "rb").read() + \
               f"\r\n--{b}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{b}--\r\n".encode()
        if len(body) > 95_000_000:
            raise SystemExit(f"{name}: {len(body)/1e6:.0f} MB — o proxy do RunPod limita ~100 MB; recomprima (CRF 20-22)")
        return json.loads(self.req("/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={b}"}))["name"]

    def submit(self, graph):
        res = json.loads(self.req("/prompt", json.dumps({"prompt": graph, "client_id": uuid.uuid4().hex}).encode(),
                                  {"Content-Type": "application/json"}))
        if res.get("node_errors"):
            raise SystemExit("ERRO de validação: " + json.dumps(res["node_errors"], indent=1)[:5000])
        return res["prompt_id"]

    def wait(self, pid, node):
        t0 = time.time()
        while True:
            h = json.loads(self.req(f"/history/{pid}"))
            if pid in h:
                st, outs = h[pid].get("status", {}), h[pid]["outputs"]
                if st.get("status_str") == "error":
                    raise SystemExit("FALHOU: " + json.dumps(st.get("messages", [])[-1:], indent=1)[:6000])
                if node in outs or st.get("completed"):
                    print(f"ok em {time.time() - t0:.0f}s", flush=True)
                    return outs
            time.sleep(8)

    def fetch(self, f, dest):
        q = "/view?" + urllib.parse.urlencode({"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")})
        open(dest, "wb").write(self.req(q))
        print("->", dest, flush=True)


SPEAKER = {
    "target": "The selected character is speaking.",
    "offscreen": "Speech is offscreen; do not make the selected character speak.",
    "other": "Another person is speaking; preserve the selected character's actual mouth performance.",
    "none": "No dialogue; preserve the visible source performance.",
}
GUIDE_TEXT = {
    "depth": "Inside the person region, <Video 1> shows a colored depth map of the source performer instead of their "
             "pixels; use it only for body shape, pose, motion and timing. ",
    "mesh": "<Video 1> has face mesh lines drawn over the source performer's face; use them only for expression, "
            "head pose and lip motion. ",
    "depth_mesh": "Inside the person region, <Video 1> shows a colored depth map of the source performer with face mesh "
                  "lines over the face, instead of their pixels; use the depth only for body shape, pose and motion and "
                  "the mesh only for expression, head pose and lip motion. ",
}


def extra_slot(seg, idx, anchor_override=None):
    """Conteúdo do 3º slot de imagem (segment_reference): âncora no meio do shot (continuação) ou referência extra."""
    if idx and (anchor_override or seg.get("anchor")):
        return "mid_anchor", anchor_override or seg["anchor"]
    extra = job["character"].get("extra_image")
    return ("extra", extra) if extra else (None, None)


def build_prompt(seg, idx, anchor_used, extra_kind=None, guide=None):
    """Rótulos na ordem em que a ferramenta envia as imagens: personagem, [âncora | boundary], [slot extra]."""
    lang = job["settings"].get("language", "Portuguese")
    desc = job["character"]["description"]
    if desc.startswith("PREENCHER"):
        raise SystemExit("Preencha character.description no job.json antes de gerar.")
    n = 2 if (anchor_used or idx) else 1                    # quantas <Picture> já foram usadas
    ctx = ("<Picture 2> is the exact first-frame scene and pose anchor. " if anchor_used and not idx else
           "<Picture 2> is the generated boundary from the preceding segment. Continue its motion and appearance. " if idx else "")
    if extra_kind == "mid_anchor":                          # texto oficial do app (segments.reference_prompt)
        ctx += (f"<Picture {n + 1}> is an additional scene and performance reference for this segment; "
                "preserve continuity with the generated boundary. ")
    elif extra_kind == "extra":
        ctx += (f"<Picture {n + 1}> is an additional identity reference of the same character from <Picture 1> "
                "(face and costume detail); use it only for appearance, not for pose, framing or background. ")
    speech = SPEAKER[seg.get("speaker", "target")] + " "
    if seg.get("speaker", "target") == "target" and seg.get("dialogue"):
        speech = (f"The selected character is speaking in {lang}. Current segment dialogue: <d>[{lang}] {seg['dialogue']}</d> "
                  "Follow source audio timing exactly; mouth shapes follow the syllables of <Audio 1>, lips close or relax during "
                  "silence. Earlier reference dialogue is context only; do not repeat it. ")
    behavior = (seg.get("behavior") or "").strip()
    gtext = GUIDE_TEXT[guide] if guide else ""
    tail = (" Remove all depth colors and mesh lines from the output: the character must look photographic in its own "
            "style. " if guide else " ")
    return (f"From the very first frame, replace only the selected person in <Video 1> with the single character in <Picture 1>: {desc}. "
            f"{ctx}{gtext}Keep the reference identity and costume, complete and uncropped, throughout. "
            "Match source posture, gaze, blinks, facial emotion, mouth movement, breathing, head movement and camera movement. "
            f"{speech}{behavior + ' ' if behavior else ''}"
            "<Audio 1> and source video determine exact timing. Do not repeat earlier dialogue or invent words, gestures, people or "
            "camera cuts. Adapt lighting to the lighting of <Video 1>. Retain the scene outside the person region."
            f"{tail}Output the raw decoded generation.")


def segment_graph(seg, idx, clip, char, anchor, seed, expansion, take, prompt, guide_clip=None, extra=None, turbo=True):
    s = job["settings"]
    g = json.load(open(TEMPLATE, encoding="utf8"))
    g["30"]["inputs"]["file"] = clip
    g["9"]["inputs"]["image"] = char
    g["31"]["inputs"]["resolution"] = job["canvas"]["resolution"]
    g["58"]["inputs"]["device"] = "default"                 # ComfyUI 0.41.2 só tem default/cpu
    g["850"]["inputs"]["lora_name"] = s.get("lora", "h3_character_swap_v1.5.safetensors")
    g["101"]["inputs"]["text"] = s.get("sam_text", "person")
    g["104"]["inputs"]["selection"] = s.get("selection", "largest")
    g["110"]["inputs"]["expansion_px"] = int(expansion)
    g["801"]["inputs"].update({"prompt": prompt, "seed": int(seed), "steps": int(s.get("steps", 8))})
    if not turbo:                                           # base sem Turbo (closes difíceis)
        g["850"]["inputs"]["model"] = ["3", 0]
        g["801"]["inputs"].update({"steps": int(s.get("base_steps", 20)), "sampler_name": "res_multistep", "scheduler": "simple"})
    g["807"]["inputs"]["filename_prefix"] = f"take-{take}"
    g["803"]["inputs"]["segment_mode"] = True               # 1 passada por segmento (prompt próprio)
    g["309"]["inputs"]["image"] = anchor or "(none)"
    if idx:                                                 # continuação: histórico do take escolhido anterior
        g["803"]["inputs"].update({"use_anchor": True, "history_file": seg["_history_file"]})
        g["803"]["inputs"].pop("anchor", None)
    if extra:                                               # 3º slot: âncora no meio do shot ou referência extra
        g["310"] = {"class_type": "LoadImage", "inputs": {"image": extra}}
        g["803"]["inputs"]["segment_reference"] = ["310", 0]
    if guide_clip:                                          # guia (profundidade/mesh) só para a geração; SAM no original
        g["32"] = {"class_type": "LoadVideo", "inputs": {"file": guide_clip}}
        g["33"] = {"class_type": "H3CharacterSwapPrepareVideo", "inputs": {**g["31"]["inputs"], "video": ["32", 0]}}
        g["803"]["inputs"].update({"source_video": ["32", 0], "source": ["33", 0], "source_audio": ["33", 1]})
    g["900"] = {"class_type": "SaveH3History", "inputs": {"frames": ["807", 0], "filename": f"hist_{take}.npz", "count": HISTORY_FRAMES}}
    return g


def anchor_graph(frame, char, seed):
    desc = job["character"]["description"]
    brief = (f"Image 1 is the source frame to edit. Image 2 is character identity only: {desc}. "
             "Keep the exact composition of image 1 unchanged: same camera framing, crop, face size, position and tilt. "
             "Replace ONLY the selected person in image 1 with that single character. Match the exact source pose, face angle, gaze, "
             "mouth opening and lip shape, expression, head position, scale and any crop at the frame edge. Preserve the entire original "
             "scene, background and lighting. Keep the reference identity and costume; do not copy the reference pose, studio lighting or "
             "background. Do not zoom out, do not add any other person. Photorealistic video frame.")
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_edit_2511_fp8mixed.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.1}},
        "3": {"class_type": "CFGNorm", "inputs": {"model": ["2", 0], "strength": 1.0}},
        "4": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "6": {"class_type": "LoadImage", "inputs": {"image": frame}},
        "7": {"class_type": "LoadImage", "inputs": {"image": char}},
        "8": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["4", 0], "vae": ["5", 0], "image1": ["6", 0], "image2": ["7", 0], "prompt": brief}},
        "9": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["4", 0], "vae": ["5", 0], "image1": ["6", 0], "image2": ["7", 0], "prompt": ""}},
        "10": {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["8", 0], "reference_latents_method": "index_timestep_zero"}},
        "11": {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["9", 0], "reference_latents_method": "index_timestep_zero"}},
        "12": {"class_type": "VAEEncode", "inputs": {"pixels": ["6", 0], "vae": ["5", 0]}},
        "13": {"class_type": "KSampler", "inputs": {"model": ["3", 0], "positive": ["10", 0], "negative": ["11", 0], "latent_image": ["12", 0],
                                                     "seed": seed, "steps": 40, "cfg": 3.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["5", 0]}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["14", 0], "filename_prefix": "anchor"}},
    }


def local_path(p):
    return p if os.path.isabs(p) else os.path.join(D, p)


def seg_frame(seg_or_shot_id):
    """1º frame do shot ou do segmento, no canvas exato (gera na hora se o prepare antigo não extraiu)."""
    path = os.path.join(D, "frames", f"{seg_or_shot_id}_0.png")
    if not os.path.exists(path):
        try:
            start = find_segment(job, seg_or_shot_id)[2]["start"]
        except SystemExit:
            start = next(s for s in job["shots"] if s["id"] == seg_or_shot_id)["start"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(D, job["source"]["sdr"]), "-vf",
             f"select='eq(n\\,{start})',{cover_crop_filter(job['canvas']['width'], job['canvas']['height'])}",
             "-fps_mode", "passthrough", "-frames:v", "1", path])
    return path


def invalidate_after(shot, idx):
    """O histórico mudou: segmentos seguintes cujo take escolhido veio de outro histórico perdem a seleção."""
    for j in range(idx + 1, len(shot["segments"])):
        if not history_ok(shot, j):
            seg = shot["segments"][j]
            print(f"  {seg['id']}: take {seg['selected_take']} foi gerado com outro histórico -> desmarcado (regerar)")
            seg["selected_take"] = None


def run_segment(pod, seg_id, seed=None, anchor=None, expansion=None, guide=None, turbo=None, suffix=""):
    shot, idx, seg = find_segment(job, seg_id)
    s = job["settings"]
    seed = int(seed or seg["seed"])
    guide = guide or s.get("guide")
    turbo = s.get("turbo", True) if turbo is None else turbo
    tags = (f"_{guide}" if guide else "") + ("" if turbo else "_base") + suffix
    history_from = None
    if idx:
        prev = shot["segments"][idx - 1]
        if not prev.get("selected_take"):
            raise SystemExit(f"Escolha antes o take de {prev['id']} (comando select) — a continuação usa o histórico dele.")
        if not history_ok(shot, idx - 1):
            raise SystemExit(f"O take escolhido de {prev['id']} veio de outro histórico: regere {prev['id']} antes.")
        history_from = prev["selected_take"]
        # a mesma seed com outro histórico é OUTRO take: o nome leva uma marca curta da origem (não sobrescreve)
        tags += "_h" + hashlib.sha1(history_from.encode()).hexdigest()[:4]
        seg["_history_file"] = f"hist_{history_from}.npz"
        mid_anchor = anchor                                 # --anchor numa continuação = âncora no meio do shot
        anchor = None                                       # o 1º slot de âncora é o boundary gerado
    else:
        mid_anchor = None
        anchor = anchor or (seg.get("anchor") if s.get("use_anchor") else None)
    take = f"{seg_id}_s{seed}{tags}"
    kind, extra = extra_slot(seg, idx, mid_anchor)
    prompt = build_prompt(seg, idx, bool(anchor), kind, guide)
    print("PROMPT:", prompt, "\n", flush=True)
    char = pod.upload(job["character"]["image"], "character" + os.path.splitext(job["character"]["image"])[1])
    clip = pod.upload(os.path.join(D, seg["clip"]))
    gclip = None
    if guide:
        gpath = os.path.join(D, "clips_guide", guide, os.path.basename(seg["clip"]))
        if not os.path.exists(gpath):
            raise SystemExit(f"{gpath} não existe: rode antes  VPY S/make_guide.py JOB/job.json --mode {guide}")
        gclip = pod.upload(gpath, f"guide_{guide}_{os.path.basename(seg['clip'])}")
    anc = pod.upload(local_path(anchor)) if anchor else None
    ext = pod.upload(local_path(extra), f"extra_{seg_id}{os.path.splitext(extra)[1]}") if extra else None
    outs = pod.wait(pod.submit(segment_graph(seg, idx, clip, char, anc, seed,
                                             expansion or s.get("expansion_px", 144), take, prompt, gclip, ext, turbo)), "807")
    if "107" in outs: print("máscara:", outs["107"].get("text"), flush=True)
    rep = outs["807"]["h3_character_swap"][0]                # SOMENTE o nó 807 (o history também lista a entrada!)
    exp = seg["end"] - seg["start"]
    print(f"frames entregues: {rep.get('delivered_frames')} (esperado {exp}) · histórico {rep.get('history_frames')}", flush=True)
    dest = os.path.join(D, "out", f"{take}.mp4")
    pod.fetch(rep["output"], dest)
    print("histórico salvo no pod:", outs.get("900", {}).get("text"), flush=True)
    seg.pop("_history_file", None)
    seg["takes"] = [t for t in seg.get("takes", []) if t["take"] != take] + [{
        "take": take, "seed": seed, "anchor": anchor, "extra": extra, "extra_kind": kind, "guide": guide,
        "turbo": turbo, "history_from": history_from, "file": f"out/{take}.mp4"}]
    if not seg.get("selected_take") or not history_ok(shot, idx):
        seg["selected_take"] = take
        invalidate_after(shot, idx)
    save_job(job, JOB_PATH)
    return take


def qa_take(seg, take):
    """Roda qa_take.py (venv) e devolve o JSON com lip sync, identidade, máscara e nota."""
    out = os.path.join(D, "out", f"{take}.qa.json")
    cmd = [vpy(), os.path.join(S, "qa_take.py"), JOB_PATH, seg["id"], take, "--json", out]
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd)
    if r.returncode or not os.path.exists(out):
        print(f"  QA de {take} falhou (código {r.returncode}); ele fica fora da escolha automática", flush=True)
        return None
    return json.load(open(out, encoding="utf-8"))


def best_of(pod, seg_id, seeds, **kw):
    shot, idx, seg = find_segment(job, seg_id)
    results = []
    for sd in seeds:
        take = run_segment(pod, seg_id, sd, **kw)
        q = qa_take(seg, take)
        rec = take_record(seg, take)
        if q:
            rec["qa"] = {k: q.get(k) for k in ("score", "lipsync_corr", "syncnet_conf", "identity_ref", "identity_src",
                                                "mask_outside_max")}
        results.append((q["score"] if q else float("-inf"), take, q))
    results.sort(key=lambda r: r[0], reverse=True)
    print(f"\nbest-of-{len(seeds)} · {seg_id}")
    f = lambda v, d=2: "—" if v is None else f"{v:.{d}f}"
    for sc, take, q in results:
        q = q or {}
        print(f"  {take:28s} nota {sc:6.3f} · lip {f(q.get('lipsync_corr'))} · sync {f(q.get('syncnet_conf'))} · "
              f"id ref {f(q.get('identity_ref'))} / fonte {f(q.get('identity_src'))} · máscara fora {f(q.get('mask_outside_max'), 1)}%")
    if results and results[0][0] > float("-inf"):
        seg["selected_take"] = results[0][1]
        invalidate_after(shot, idx)
        print(f"-> escolhido {results[0][1]} (confira a revisão visual com som antes de seguir)")
    save_job(job, JOB_PATH)
    return seg["selected_take"]


LATENTSYNC_FPS = 25  # o LatentSync só aceita 25 fps: o trecho é reetiquetado 24->25 (e o áudio acelerado 25/24)


def lipfix(pod, seg_id, t0, t1, steps, seed):
    shot, idx, seg = find_segment(job, seg_id)
    take = seg.get("selected_take")
    if not take:
        raise SystemExit(f"{seg_id} não tem take escolhido")
    src = os.path.join(D, "out", f"{take}.mp4")
    n = seg["end"] - seg["start"]
    margin = 6                                                  # frames extras de cada lado para a transição
    a, b = max(0, round(t0 * FPS) - margin), min(n, round(t1 * FPS) + margin)
    if b - a < 16:
        raise SystemExit("trecho curto demais (mínimo ~0,7 s)")
    work = os.path.join(D, "out", "lipfix")
    os.makedirs(work, exist_ok=True)
    win_v, win_a = os.path.join(work, f"{take}_{a}_{b}.mp4"), os.path.join(work, f"{take}_{a}_{b}.wav")
    # vídeo: mesmos frames, carimbados a 25 fps (1 frame -> 1 frame); áudio: voz isolada do trecho acelerada 25/24
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
         f"trim=start_frame={a}:end_frame={b},setpts=(N)/({LATENTSYNC_FPS}*TB)", "-r", str(LATENTSYNC_FPS), "-an",
         "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", win_v])
    clip = os.path.join(D, seg["clip"])
    ctx = HISTORY_FRAMES if idx else 0                          # o clipe de continuação traz 18 frames de contexto antes
    run(["ffmpeg", "-v", "error", "-y", "-i", clip, "-vn", "-af",
         f"atrim=start={(ctx + a) / FPS}:end={(ctx + b) / FPS},asetpts=PTS-STARTPTS,atempo={LATENTSYNC_FPS / FPS}",
         "-ac", "1", "-ar", "16000", win_a])
    v, au = pod.upload(win_v), pod.upload(win_a)
    g = {"1": {"class_type": "H3LatentSyncWindow", "inputs": {"video": v, "audio": au, "steps": int(steps),
                                                               "guidance": 1.5, "seed": int(seed),
                                                               "filename_prefix": f"lipfix-{take}"}}}
    outs = pod.wait(pod.submit(g), "1")
    fixed = os.path.join(work, f"{take}_{a}_{b}_ls.mp4")
    pod.fetch(outs["1"]["video"][0], fixed)
    new = f"{take}_lf{a}"
    dest = os.path.join(D, "out", f"{new}.mp4")
    fade = margin / FPS
    dur = (b - a) / FPS
    # devolve o trecho para 24 fps 1:1 e funde com o take (rampa de alpha nas margens); áudio do take original
    run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", fixed, "-filter_complex",
         f"[1:v]setpts=N/({FPS}*TB)+{a / FPS}/TB,format=yuva420p,"
         f"fade=t=in:st={a / FPS}:d={fade}:alpha=1,fade=t=out:st={a / FPS + dur - fade}:d={fade}:alpha=1[f];"
         f"[0:v][f]overlay=eof_action=pass:format=auto,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-c:a", "copy", dest])
    rec = dict(take_record(seg, take) or {}, take=new, file=f"out/{new}.mp4", lipfix={"from": take, "frames": [a, b],
                                                                                        "steps": steps, "seed": seed})
    seg["takes"] = [t for t in seg.get("takes", []) if t["take"] != new] + [rec]
    save_job(job, JOB_PATH)
    print(f"novo take {new} (o original continua escolhido). Rode a QA e, se melhorar:  select {seg_id} {new}")


def common_kw():
    return {"anchor": opt("--anchor"), "expansion": opt("--expansion"), "guide": opt("--guide"),
            "turbo": False if "--no-turbo" in sys.argv else None}


if opt("--guide") and opt("--guide") not in GUIDES:
    raise SystemExit(f"--guide deve ser um de {GUIDES}")

if CMD == "prompt":
    shot, idx, seg = find_segment(job, sys.argv[3])
    use = bool(seg.get("anchor")) and job["settings"].get("use_anchor") and not idx
    print(build_prompt(seg, idx, use, extra_slot(seg, idx)[0], opt("--guide") or job["settings"].get("guide")))
elif CMD == "check":
    pod = Pod(sys.argv[3])
    info = json.loads(pod.req("/object_info"))
    need = ["H3CharacterSwapController", "H3CharacterSwapAssemble", "SAM3_Detect", "SAM3_VideoTrack", "SaveH3History",
            "MiniMaxH3SigmaShift", "H3CharacterSwapPrepareVideo", "LoadImage"]
    print({n: n in info for n in need})
    print("LatentSync (opcional, make_pod --latentsync):", "H3LatentSyncWindow" in info)
    for node, field in [("UNETLoader", "unet_name"), ("CLIPLoader", "clip_name"), ("LoraLoaderModelOnly", "lora_name"),
                        ("VAELoader", "vae_name"), ("CheckpointLoaderSimple", "ckpt_name")]:
        print(node, info[node]["input"]["required"][field][0])
    print("argv:", json.loads(pod.req("/system_stats"))["system"].get("argv"))
elif CMD == "anchor":
    pod, target, seeds = Pod(sys.argv[3]), sys.argv[4], [int(s) for s in sys.argv[5].split(",")]
    char = pod.upload(job["character"]["image"])
    frame = pod.upload(seg_frame(target), f"frame_{target}.png")
    pids = [(s, pod.submit(anchor_graph(frame, char, s))) for s in seeds]
    for s, pid in pids:
        outs = pod.wait(pid, "15")
        pod.fetch(outs["15"]["images"][0], os.path.join(D, "out", f"anchor_{target}_s{s}.png"))
elif CMD == "seg":
    run_segment(Pod(sys.argv[3]), sys.argv[4], opt("--seed"), **common_kw())
elif CMD == "best":
    best_of(Pod(sys.argv[3]), sys.argv[4], [int(s) for s in sys.argv[5].split(",")], **common_kw())
elif CMD == "select":
    shot, idx, seg = find_segment(job, sys.argv[3])
    if not take_record(seg, sys.argv[4]) and not os.path.exists(os.path.join(D, "out", sys.argv[4] + ".mp4")):
        raise SystemExit(f"take {sys.argv[4]} não existe em {seg['id']}")
    seg["selected_take"] = sys.argv[4]
    if not history_ok(shot, idx):
        print(f"ATENÇÃO: {sys.argv[4]} foi gerado com um histórico que não é o take escolhido de "
              f"{shot['segments'][idx - 1]['id']}; a emenda pode saltar.")
    invalidate_after(shot, idx)
    save_job(job, JOB_PATH)
    print(f"{seg['id']} -> {sys.argv[4]}. Rode  chain <pod> {shot['id']}  para regerar o que foi desmarcado.")
elif CMD == "chain":
    pod, shot_id = Pod(sys.argv[3]), sys.argv[4]
    shot = next(s for s in job["shots"] if s["id"] == shot_id)
    seeds = [int(x) for x in opt("--seeds").split(",")] if opt("--seeds") else None
    for i, seg in enumerate(shot["segments"]):
        t = seg.get("selected_take")
        if t and os.path.exists(os.path.join(D, "out", t + ".mp4")) and history_ok(shot, i):
            print(f"{seg['id']}: já tem take {t} — pulando", flush=True)
            continue
        if t and not history_ok(shot, i):
            print(f"{seg['id']}: take {t} veio de outro histórico — regerando", flush=True)
            seg["selected_take"] = None
        kw = common_kw()
        kw.pop("anchor")                                    # âncora por segmento vem do job.json (seg.anchor)
        if seeds:
            best_of(pod, seg["id"], seeds, **kw)
        else:
            run_segment(pod, seg["id"], **kw)
elif CMD == "lipfix":
    lipfix(Pod(sys.argv[3]), sys.argv[4], float(sys.argv[5]), float(sys.argv[6]), int(opt("--steps", 20)),
           int(opt("--seed", 1247)))
else:
    raise SystemExit(__doc__)
