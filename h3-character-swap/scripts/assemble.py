"""Monta o vídeo final a partir do job.json: takes escolhidos dos shots `generate` + vídeo original (mesmo recorte)
nos shots `preserve` + áudio ORIGINAL completo.

Uso:  python assemble.py JOB.json [saida.mp4]
Também gera <saida>_ref.mp4: a fonte SDR no mesmo canvas (para QA lado a lado e qa_lipsync.py).
Este é o final no CANVAS (736x1344 no preset 768). Para o final em resolução cheia, com o fundo original, use
composite.py depois de aprovar os takes.
"""
import os, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, cover_crop_filter, count_frames, run, history_ok, FPS

job = load_job(sys.argv[1])
D = job["_dir"]
out = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, "final.mp4"))
W, H = job["canvas"]["width"], job["canvas"]["height"]
src = os.path.join(D, job["source"]["sdr"])
parts, problems = [], []
for shot in job["shots"]:
    n = shot["end"] - shot["start"]
    if shot["mode"] == "preserve":
        p = os.path.join(D, "out", f"preserve_{shot['id']}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
             f"trim=start_frame={shot['start']}:end_frame={shot['end']},setpts=PTS-STARTPTS,{cover_crop_filter(W, H)}",
             "-an", "-c:v", "libx264", "-crf", "12", "-preset", "slow", "-pix_fmt", "yuv420p", p])
        parts.append(p)
    else:
        for i, seg in enumerate(shot["segments"]):
            t = seg.get("selected_take")
            if t and not history_ok(shot, i):
                problems.append(f"{seg['id']}: o take {t} foi gerado com o histórico de outro take do segmento anterior "
                                "(rode chain para regerar)")
            f = os.path.join(D, "out", f"{t}.mp4") if t else None
            if not f or not os.path.exists(f):
                problems.append(f"{seg['id']}: sem take escolhido/gerado")
                continue
            got, exp = count_frames(f), seg["end"] - seg["start"]
            if got != exp:
                problems.append(f"{seg['id']}: {got} frames (esperado {exp})")
            parts.append(f)
if problems:
    raise SystemExit("Não dá para montar:\n- " + "\n- ".join(problems))
inputs = sum((["-i", p] for p in parts), [])
chain = "".join(f"[{i}:v]setpts=PTS-STARTPTS,setsar=1,fps={FPS},scale={W}:{H}[v{i}];" for i in range(len(parts)))
chain += "".join(f"[v{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[v]"
run(["ffmpeg", "-v", "error", "-y", *inputs, "-i", src, "-filter_complex", chain, "-map", "[v]", "-map", f"{len(parts)}:a:0?",
     "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", out])
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", cover_crop_filter(W, H), "-an", "-c:v", "libx264", "-crf", "14",
     "-pix_fmt", "yuv420p", out.replace(".mp4", "_ref.mp4")])
total = count_frames(out)
print(f"final: {out} · {total} frames (fonte {job['source']['frames']}) {'OK' if total == job['source']['frames'] else '<-- DIVERGE'}")
