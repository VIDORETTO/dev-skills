"""Orquestra a geração no ComfyUI do pod a partir de job.json (só stdlib; roda com qualquer python 3.10+).

Comandos:
  python run_job.py JOB.json check  <pod>                      # nós e modelos presentes?
  python run_job.py JOB.json prompt <seg>                      # imprime o prompt do segmento (sem GPU)
  python run_job.py JOB.json anchor <pod> <shot> 11,22,33      # variações de âncora (Qwen-Image-Edit) -> out/anchor_<shot>_s<seed>.png
  python run_job.py JOB.json seg    <pod> <seg> [--seed N] [--anchor arquivo.png] [--expansion PX]
                                                               # 1 take -> out/<seg>_s<seed>.mp4 (+ histórico salvo no pod)
  python run_job.py JOB.json select <seg> <take>               # marca o take escolhido (ex.: A1_s31337)
  python run_job.py JOB.json chain  <pod> <shot>               # gera os segmentos restantes do shot em sequência

Regras embutidas (ver SKILL.md): modo segmento sempre; continuação usa o histórico do take ESCOLHIDO do segmento
anterior; saída lida SOMENTE do nó 807; user-agent de curl (o proxy do RunPod devolve 403 ao urllib).
"""
import json, os, sys, time, uuid, urllib.request, urllib.parse
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, save_job, find_segment, HISTORY_FRAMES

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL, "assets", "h3_character_swap.api.json")
UA = {"User-Agent": "curl/8.9.1"}

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
        self.base = f"https://{pod}-8188.proxy.runpod.net"

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


def build_prompt(seg, idx, anchor_used):
    lang = job["settings"].get("language", "Portuguese")
    desc = job["character"]["description"]
    if desc.startswith("PREENCHER"):
        raise SystemExit("Preencha character.description no job.json antes de gerar.")
    ctx = ("<Picture 2> is the exact first-frame scene and pose anchor. " if anchor_used else
           "<Picture 2> is the generated boundary from the preceding segment. Continue its motion and appearance. " if idx else "")
    speech = SPEAKER[seg.get("speaker", "target")] + " "
    if seg.get("speaker", "target") == "target" and seg.get("dialogue"):
        speech = (f"The selected character is speaking in {lang}. Current segment dialogue: <d>[{lang}] {seg['dialogue']}</d> "
                  "Follow source audio timing exactly; mouth shapes follow the syllables of <Audio 1>, lips close or relax during "
                  "silence. Earlier reference dialogue is context only; do not repeat it. ")
    behavior = (seg.get("behavior") or "").strip()
    return (f"From the very first frame, replace only the selected person in <Video 1> with the single character in <Picture 1>: {desc}. "
            f"{ctx}Keep the reference identity and costume, complete and uncropped, throughout. "
            "Match source posture, gaze, blinks, facial emotion, mouth movement, breathing, head movement and camera movement. "
            f"{speech}{behavior + ' ' if behavior else ''}"
            "<Audio 1> and source video determine exact timing. Do not repeat earlier dialogue or invent words, gestures, people or "
            "camera cuts. Adapt lighting to the lighting of <Video 1>. Retain the scene outside the person region. "
            "Output the raw decoded generation.")


def segment_graph(seg, idx, clip, char, anchor, seed, expansion, take):
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
    g["801"]["inputs"].update({"prompt": build_prompt(seg, idx, bool(anchor)), "seed": int(seed),
                               "steps": int(s.get("steps", 8))})
    if not s.get("turbo", True):                            # base sem Turbo (teste p/ closes difíceis)
        g["850"]["inputs"]["model"] = ["3", 0]
        g["801"]["inputs"].update({"steps": int(s.get("steps", 20)), "sampler_name": "res_multistep", "scheduler": "simple"})
    g["807"]["inputs"]["filename_prefix"] = f"take-{take}"
    g["803"]["inputs"]["segment_mode"] = True               # 1 passada por segmento (prompt próprio)
    g["309"]["inputs"]["image"] = anchor or "(none)"
    if idx:                                                 # continuação: histórico do take escolhido anterior
        g["803"]["inputs"].update({"use_anchor": True, "history_file": seg["_history_file"]})
        g["803"]["inputs"].pop("anchor", None)
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


def run_segment(pod, seg_id, seed=None, anchor=None, expansion=None):
    shot, idx, seg = find_segment(job, seg_id)
    seed = int(seed or seg["seed"])
    take = f"{seg_id}_s{seed}"
    if idx:
        prev = shot["segments"][idx - 1]
        if not prev.get("selected_take"):
            raise SystemExit(f"Escolha antes o take de {prev['id']} (comando select) — a continuação usa o histórico dele.")
        seg["_history_file"] = f"hist_{prev['selected_take']}.npz"
        anchor = None                                       # continuação nunca usa âncora
    anchor = anchor or (seg.get("anchor") if job["settings"].get("use_anchor") else None)
    print("PROMPT:", build_prompt(seg, idx, bool(anchor)), "\n", flush=True)
    char = pod.upload(job["character"]["image"], "character" + os.path.splitext(job["character"]["image"])[1])
    clip = pod.upload(os.path.join(D, seg["clip"]))
    anc = pod.upload(os.path.join(D, anchor) if not os.path.isabs(anchor) else anchor) if anchor else None
    outs = pod.wait(pod.submit(segment_graph(seg, idx, clip, char, anc, seed,
                                             expansion or job["settings"].get("expansion_px", 144), take)), "807")
    if "107" in outs: print("máscara:", outs["107"].get("text"), flush=True)
    rep = outs["807"]["h3_character_swap"][0]                # SOMENTE o nó 807 (o history também lista a entrada!)
    exp = seg["end"] - seg["start"]
    print(f"frames entregues: {rep.get('delivered_frames')} (esperado {exp}) · histórico {rep.get('history_frames')}", flush=True)
    dest = os.path.join(D, "out", f"{take}.mp4")
    pod.fetch(rep["output"], dest)
    print("histórico salvo no pod:", outs.get("900", {}).get("text"), flush=True)
    seg.pop("_history_file", None)
    seg.setdefault("takes", []).append({"take": take, "seed": seed, "anchor": anchor, "file": f"out/{take}.mp4"})
    if not seg.get("selected_take"):
        seg["selected_take"] = take
    save_job(job, JOB_PATH)
    return take


if CMD == "prompt":
    shot, idx, seg = find_segment(job, sys.argv[3])
    print(build_prompt(seg, idx, bool(seg.get("anchor")) and job["settings"].get("use_anchor") and not idx))
elif CMD == "check":
    pod = Pod(sys.argv[3])
    info = json.loads(pod.req("/object_info"))
    need = ["H3CharacterSwapController", "H3CharacterSwapAssemble", "SAM3_Detect", "SAM3_VideoTrack", "SaveH3History", "MiniMaxH3SigmaShift"]
    print({n: n in info for n in need})
    for node, field in [("UNETLoader", "unet_name"), ("CLIPLoader", "clip_name"), ("LoraLoaderModelOnly", "lora_name"),
                        ("VAELoader", "vae_name"), ("CheckpointLoaderSimple", "ckpt_name")]:
        print(node, info[node]["input"]["required"][field][0])
    print("argv:", json.loads(pod.req("/system_stats"))["system"].get("argv"))
elif CMD == "anchor":
    pod, shot_id, seeds = Pod(sys.argv[3]), sys.argv[4], [int(s) for s in sys.argv[5].split(",")]
    char = pod.upload(job["character"]["image"])
    frame = pod.upload(os.path.join(D, "frames", f"{shot_id}_0.png"))
    pids = [(s, pod.submit(anchor_graph(frame, char, s))) for s in seeds]
    for s, pid in pids:
        outs = pod.wait(pid, "15")
        pod.fetch(outs["15"]["images"][0], os.path.join(D, "out", f"anchor_{shot_id}_s{s}.png"))
elif CMD == "seg":
    run_segment(Pod(sys.argv[3]), sys.argv[4], opt("--seed"), opt("--anchor"), opt("--expansion"))
elif CMD == "select":
    shot, idx, seg = find_segment(job, sys.argv[3])
    seg["selected_take"] = sys.argv[4]
    save_job(job, JOB_PATH)
    print(f"{seg['id']} -> {sys.argv[4]}. Atenção: segmentos seguintes do shot precisam ser (re)gerados com este histórico.")
elif CMD == "chain":
    pod, shot_id = Pod(sys.argv[3]), sys.argv[4]
    shot = next(s for s in job["shots"] if s["id"] == shot_id)
    for seg in shot["segments"]:
        if seg.get("selected_take") and os.path.exists(os.path.join(D, "out", seg["selected_take"] + ".mp4")):
            print(f"{seg['id']}: já tem take {seg['selected_take']} — pulando", flush=True)
            continue
        run_segment(pod, seg["id"])
else:
    raise SystemExit(__doc__)
