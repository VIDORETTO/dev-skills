"""Análise prévia + preparação local (CPU) de um character swap H3.

Uso (no venv da skill, ver references/08-ambiente-local.md):
  python prepare.py --video IMG.MOV --character ref.png --out job_dir [--lang pt] [--res 768]
                    [--no-demucs] [--whisper large-v3] [--target 130] [--max 157] [--presence-stride 2]

Gera em job_dir/:
  source_sdr.mp4        fonte normalizada (SDR BT.709, 24 fps, áudio original)
  vocals.wav            voz isolada (Demucs) — vai SÓ para o condicionamento
  transcript.json       palavras com timestamps (faster-whisper)
  analysis.json         presença por frame, cortes de câmera, energia vocal, eventos não verbais
  clips/<seg>.mp4       clipe de cada segmento (com 18 frames de contexto nos de continuação), áudio = voz isolada
  frames/<id>_0.png     1º frame de cada shot e de cada segmento no canvas exato (âncora opcional, inclusive no meio do shot)
  job.json              rascunho do job (shots, segmentos, diálogos, eventos) — REVISAR antes de gerar
  analysis.md           relatório legível da análise prévia
"""
import argparse, json, os, sys, wave
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import (FPS, HISTORY_FRAMES, canvas_dimensions, cover_crop_filter, window_for, video_info,
                      count_frames, run, save_job)

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True)
ap.add_argument("--character", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--lang", default="pt")
ap.add_argument("--res", default="768", choices=["480", "768"])
ap.add_argument("--no-demucs", action="store_true")
ap.add_argument("--whisper", default="large-v3")
ap.add_argument("--target", type=int, default=130, help="tamanho-alvo do segmento em frames (~5,4 s)")
ap.add_argument("--min", type=int, default=90)
ap.add_argument("--max", type=int, default=157, help="máximo por segmento (janela 158 = 6,6 s)")
ap.add_argument("--presence-stride", type=int, default=2)
ap.add_argument("--presence-on", type=float, default=3.0, help="%% de pixels de pessoa p/ considerar presente")
ap.add_argument("--min-shot", type=int, default=22)
ap.add_argument("--peak-min", type=float, default=15.0, help="trecho só conta como a pessoa-alvo se o pico de presença passar disso (%%) — filtra pedestres/fundo")
ap.add_argument("--min-absence", type=int, default=12, help="ausência mais curta que isso (frames) é falha de detecção, não saída de quadro")
a = ap.parse_args()

OUT = os.path.abspath(a.out)
os.makedirs(os.path.join(OUT, "clips"), exist_ok=True)
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
P = lambda *x: os.path.join(OUT, *x)

# 1. inspeção + normalização ---------------------------------------------------------------------
info = video_info(a.video)
print("fonte:", info, flush=True)
tm = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,") if info["hdr"] else ""
short = "scale='if(gt(iw,ih),-2,1080)':'if(gt(iw,ih),1080,-2)':flags=lanczos"
vf = f"fps={FPS},{tm}format=yuv420p,{short},setsar=1"
run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-map", "0:v:0", "-map", "0:a:0?", "-vf", vf,
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
     "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", P("source_sdr.mp4")])
frames = count_frames(P("source_sdr.mp4"))
sdr = video_info(P("source_sdr.mp4"))
W, H = canvas_dimensions(sdr["width"], sdr["height"], a.res)
print(f"SDR {sdr['width']}x{sdr['height']} · {frames} frames · canvas {a.res} = {W}x{H}", flush=True)

# 2. áudio: voz isolada + transcrição + energia ---------------------------------------------------
has_audio = info["has_audio"]
words, rms, events = [], [], []
if has_audio:
    run(["ffmpeg", "-v", "error", "-y", "-i", P("source_sdr.mp4"), "-vn", "-ac", "2", "-ar", "44100", "-c:a", "pcm_s16le", P("full_audio.wav")])
    if not a.no_demucs:
        run([sys.executable, "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs", "-o", P("demucs"), P("full_audio.wav")])
        run(["ffmpeg", "-v", "error", "-y", "-i", P("demucs", "htdemucs", "full_audio", "vocals.wav"), "-c:a", "pcm_s16le", P("vocals.wav")])
    else:
        run(["ffmpeg", "-v", "error", "-y", "-i", P("full_audio.wav"), "-c:a", "pcm_s16le", P("vocals.wav")])
    run(["ffmpeg", "-v", "error", "-y", "-i", P("vocals.wav"), "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", P("vocals16k.wav")])
    with wave.open(P("vocals16k.wav"), "rb") as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    from faster_whisper import WhisperModel
    model = WhisperModel(a.whisper, device="cpu", compute_type="int8")
    segs, winfo = model.transcribe(x, language=a.lang, beam_size=5, word_timestamps=True, vad_filter=False,
                                   condition_on_previous_text=False)
    for s in segs:
        words += [{"word": wd.word.strip(), "start": round(wd.start, 3), "end": round(wd.end, 3), "p": round(wd.probability, 2)}
                  for wd in (s.words or [])]
    json.dump({"language": winfo.language, "words": words}, open(P("transcript.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hop = 4000  # 0,25 s a 16 kHz
    rms = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]
    thr = max(0.015, float(np.percentile(rms, 60)) * 0.5)
    # energia vocal sem palavra sobreposta = evento não verbal (sopro, respiração forte, riso, tosse...)
    speech = lambda t0, t1: any(wd["start"] < t1 and wd["end"] > t0 for wd in words)
    cur = None
    for i, e in enumerate(rms):
        t0, t1 = i * 0.25, (i + 1) * 0.25
        if e > thr and not speech(t0 - 0.1, t1 + 0.1):
            cur = [t0, t1] if cur is None else [cur[0], t1]
        elif cur:
            if cur[1] - cur[0] >= 0.5: events.append({"t0": cur[0], "t1": cur[1], "type": "vocal_nonspeech", "label": "?"})
            cur = None
    if cur and cur[1] - cur[0] >= 0.5: events.append({"t0": cur[0], "t1": cur[1], "type": "vocal_nonspeech", "label": "?"})

# 3. presença de pessoa por frame + cortes de câmera ----------------------------------------------
import cv2
from rembg import new_session, remove
sess = new_session("u2net_human_seg")
cap = cv2.VideoCapture(P("source_sdr.mp4"))
presence, n = [], 0
while True:
    ok, f = cap.read()
    if not ok: break
    if n % a.presence_stride == 0:
        g = cv2.resize(f, (360, int(360 * f.shape[0] / f.shape[1])))
        presence.append(float((np.asarray(remove(g, session=sess, only_mask=True)) > 127).mean() * 100))
    else:
        presence.append(None)
    n += 1
for i, v in enumerate(presence):  # preenche frames pulados com o vizinho anterior
    if v is None: presence[i] = presence[i - 1]
cuts = []
sc = __import__("subprocess").run(["ffmpeg", "-v", "info", "-i", P("source_sdr.mp4"), "-vf", "select='gt(scene,0.45)',showinfo", "-f", "null", "-"],
                                  capture_output=True, text=True).stderr
for line in sc.splitlines():
    if "pts_time:" in line:
        t = float(line.split("pts_time:")[1].split()[0]); cuts.append(round(t * FPS))

# 4. shots: generate (pessoa presente o tempo todo) x preserve (sem pessoa) -----------------------
present = [p >= a.presence_on for p in presence]
def runs(flags, value):
    i = 0
    while i < len(flags):
        if flags[i] == value:
            j = i
            while j < len(flags) and flags[j] == value: j += 1
            yield i, j
            i = j
        else:
            i += 1
# 1) trechos "presentes" cujo pico é baixo são pessoas pequenas no fundo / falso positivo -> ausência
for i, j in list(runs(present, True)):
    if max(presence[i:j]) < a.peak_min:
        for k in range(i, j): present[k] = False
# 2) histerese: ausências curtas (balanço de câmera, motion blur, rosto muito perto) são falhas de detecção.
# O SAM da ferramenta oficial recupera esses frames; só ausência sustentada vira shot `preserve`.
i = 0
while i < len(present):
    if not present[i]:
        j = i
        while j < len(present) and not present[j]: j += 1
        if j - i < a.min_absence and i > 0 and j < len(present):
            for k in range(i, j): present[k] = True
        i = j
    else:
        i += 1
bounds = sorted(set([0, len(present)] + [c for c in cuts if 0 < c < len(present)] +
                    [i for i in range(1, len(present)) if present[i] != present[i - 1]]))
raw = []
for s, e in zip(bounds, bounds[1:]):
    mode = "generate" if all(present[s:e]) else "preserve"
    raw.append([s, e, mode])
merged = []
for s, e, m in raw:  # shot de geração curto demais vira preserve; junta preserves vizinhos
    if m == "generate" and e - s < a.min_shot: m = "preserve"
    if merged and merged[-1][2] == m and m == "preserve": merged[-1][1] = e
    else: merged.append([s, e, m])

# 5. segmentos dentro de cada shot generate, cortando em pausas da fala ---------------------------
spoken = np.zeros(len(present), bool)
for wd in words:
    spoken[int(wd["start"] * FPS):int(np.ceil(wd["end"] * FPS))] = True

def split(s, e):
    out, cur = [], s
    while e - cur > a.max:
        lo, hi = cur + a.min, min(cur + a.max, e - a.min)
        if lo > hi:  # resto entre max e max+min: não cabem dois segmentos >= min; corta perto do meio
            lo, hi = cur + (e - cur) // 2 - 12, cur + (e - cur) // 2 + 12
        cand = range(lo, hi + 1)
        best = min(cand, key=lambda f: (spoken[f], abs((f - cur) - a.target)))
        out.append((cur, best)); cur = best
    out.append((cur, e))
    return out

def words_in(s, e):
    return [wd for wd in words if s / FPS <= (wd["start"] + wd["end"]) / 2 < e / FPS]

shots, letters = [], iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
for s, e, m in merged:
    sid = next(letters)
    shot = {"id": sid, "mode": m, "start": s, "end": e}
    if m == "generate":
        shot["segments"] = []
        for k, (ss, se) in enumerate(split(s, e)):
            wl = words_in(ss, se)
            ev = [dict(x, t0=round(x["t0"] - ss / FPS, 2), t1=round(x["t1"] - ss / FPS, 2)) for x in events
                  if ss / FPS <= x["t0"] < se / FPS]
            seg = {"id": f"{sid}{k + 1}", "start": ss, "end": se, "history": 0 if k == 0 else HISTORY_FRAMES,
                   "window": window_for(se - ss, 0 if k == 0 else HISTORY_FRAMES),
                   "dialogue": " ".join(w["word"] for w in wl).strip(),
                   "words": [dict(w, rel_start=round(w["start"] - ss / FPS, 2)) for w in wl],
                   "speaker": "target" if wl else "none", "nonverbal": ev, "behavior": "",
                   "anchor": None, "seed": 904239 + len(shots) * 100 + k, "selected_take": None,
                   "clip": f"clips/{sid}{k + 1}.mp4"}
            # clipe: continuação leva 18 frames de contexto da fonte antes do início
            c0 = ss - (HISTORY_FRAMES if k else 0)
            run(["ffmpeg", "-v", "error", "-y", "-i", P("source_sdr.mp4"), "-i", P("vocals.wav") if has_audio else P("source_sdr.mp4"),
                 "-map", "0:v:0", "-map", "1:a:0" if has_audio else "0:a:0?",
                 "-vf", f"trim=start_frame={c0}:end_frame={se},setpts=PTS-STARTPTS",
                 "-af", f"atrim=start={c0 / FPS}:end={se / FPS},asetpts=PTS-STARTPTS",
                 "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
                 "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                 "-c:a", "aac", "-b:a", "192k", P(seg["clip"])])
            shot["segments"].append(seg)
        for fid, f0 in [(sid, s)] + [(g["id"], g["start"]) for g in shot["segments"][1:]]:
            run(["ffmpeg", "-v", "error", "-y", "-i", P("source_sdr.mp4"), "-vf", f"select='eq(n\\,{f0})',{cover_crop_filter(W, H)}",
                 "-fps_mode", "passthrough", "-frames:v", "1", P("frames", f"{fid}_0.png")])
    shots.append(shot)

job = {"source": {"original": os.path.abspath(a.video), "sdr": "source_sdr.mp4", "vocals": "vocals.wav" if has_audio else None,
                  "frames": frames, "fps": FPS, "hdr_converted": info["hdr"], "original_transfer": info["transfer"]},
       "canvas": {"resolution": a.res, "width": W, "height": H},
       "character": {"image": os.path.abspath(a.character), "extra_image": None,
                     "description": "PREENCHER: rosto, pele, cabelo, proporções, cada peça de roupa"},
       "settings": {"expansion_px": 144, "lora": "h3_character_swap_v1.5.safetensors", "turbo": True, "steps": 8,
                    "base_steps": 20, "sam_text": "person", "selection": "largest", "language": "Portuguese",
                    "use_anchor": False, "guide": None, "identity_backend": "arcface"},
       "shots": shots}
save_job(job, P("job.json"))
json.dump({"presence": presence, "cuts": cuts, "rms_025s": rms, "events": events}, open(P("analysis.json"), "w"), indent=0)

# 6. relatório ------------------------------------------------------------------------------------
L = [f"# Análise prévia — {os.path.basename(a.video)}", "",
     f"- Fonte: {info['width']}x{info['height']} · {info['fps']:.2f} fps · {info['duration']:.2f} s · transfer `{info['transfer']}` "
     f"→ **{'HDR convertido para SDR' if info['hdr'] else 'SDR'}**",
     f"- Normalizado: {frames} frames a 24 fps · canvas {a.res}: **{W}x{H}**",
     f"- Áudio: {'voz isolada (Demucs) + ' if has_audio and not a.no_demucs else ''}{'transcrição ' + str(len(words)) + ' palavras' if has_audio else 'SEM áudio'}",
     f"- Cortes de câmera detectados: {cuts or 'nenhum'}", "", "## Shots", "",
     "| Shot | Frames | Tempo | Modo | Segmentos |", "|---|---|---|---|---|"]
for sh in shots:
    segs = ", ".join(f"{g['id']} ({g['end'] - g['start']}f, janela {g['window']})" for g in sh.get("segments", [])) or "— (vídeo original)"
    L.append(f"| {sh['id']} | {sh['start']}–{sh['end'] - 1} | {sh['start'] / FPS:.2f}–{sh['end'] / FPS:.2f}s | {sh['mode']} | {segs} |")
L += ["", "## Segmentos (revisar diálogo, falante e comportamento não verbal)", ""]
for sh, i, g in ((sh, i, g) for sh in shots for i, g in enumerate(sh.get("segments", []))):
    L.append(f"### {g['id']} · frames {g['start']}–{g['end'] - 1} ({(g['end'] - g['start']) / FPS:.2f}s) · histórico {g['history']}")
    L.append(f"- Diálogo: \"{g['dialogue']}\"")
    L.append(f"- Falante: `{g['speaker']}`")
    for ev in g["nonverbal"]:
        L.append(f"- ⚠️ Som vocal sem palavra em {ev['t0']:.2f}–{ev['t1']:.2f}s (relativo): sopro? respiração? riso? → descrever em `behavior`")
    pres = presence[g["start"]:g["end"]]
    L.append(f"- Presença da pessoa: mín {min(pres):.1f}% · média {np.mean(pres):.1f}%")
    L.append("")
L += ["## Pendências antes de gerar", "",
      "1. Preencher `character.description` no job.json (descrição física e de figurino detalhada).",
      "2. Para cada segmento: conferir `dialogue`, `speaker` (target/offscreen/other/none) e escrever `behavior` com tempos "
      "(sopro, respiração, pausas, giros de câmera, entrada/saída de quadro).",
      "3. Ajustar `settings.expansion_px` ao volume do personagem (chapéu/cabelo/capa: 128–160).",
      "4. Conferir os shots `preserve` (trechos sem a pessoa ficam com o vídeo original).",
      "5. Opcional: `character.extra_image` = 2ª referência do MESMO personagem (close nítido do rosto ou folha do figurino).", ""]
open(P("analysis.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
