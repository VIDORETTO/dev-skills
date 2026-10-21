"""QA completa de UM take, com nota única (usada pelo best-of-N do run_job.py).

Uso (venv): python qa_take.py JOB.json <seg> <take> [--json saida.json] [--no-syncnet] [--no-identity] [--no-mask]

Monta sozinho a referência do segmento (fonte SDR no canvas, mesmos frames) e o áudio do trecho (voz isolada) e roda:
  lip sync MAR contra a fonte (qa_lipsync) · SyncNet contra o áudio (qa_syncnet, se houver torch) ·
  identidade ArcFace contra a referência e contra a fonte (qa_identity) · recorte da máscara (qa_mask).

Nota = corr_MAR + 0,5·min(LSE-C/8, 1) + (id_ref − id_fonte) − 0,05·max(0, %fora_máscara − 2)
(termos ausentes ficam de fora). Serve para ORDENAR takes do mesmo segmento, não como nota absoluta.
A escolha automática não substitui assistir com som: confira o vencedor.
"""
import json, os, subprocess, sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h3common import load_job, find_segment, cover_crop_filter, FPS, HISTORY_FRAMES


def ensure_refs(job, shot, idx, seg):
    D = job["_dir"]
    ref = os.path.join(D, "out", f"ref_{seg['id']}.mp4")
    wav = os.path.join(D, "out", f"ref_{seg['id']}.wav")
    if not os.path.exists(ref):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(D, job["source"]["sdr"]), "-vf",
                        f"trim=start_frame={seg['start']}:end_frame={seg['end']},setpts=PTS-STARTPTS,"
                        f"{cover_crop_filter(job['canvas']['width'], job['canvas']['height'])}",
                        "-an", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", ref], check=True)
    if not os.path.exists(wav):
        ctx = HISTORY_FRAMES if idx else 0             # clipe de continuação começa 18 frames antes
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(D, seg["clip"]), "-vn", "-af",
                        f"atrim=start={ctx / FPS}:end={(ctx + seg['end'] - seg['start']) / FPS},asetpts=PTS-STARTPTS",
                        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav], check=True)
    return ref, wav


def score(q):
    s = 0.0
    if q.get("lipsync_corr") is not None: s += q["lipsync_corr"]
    if q.get("syncnet_conf") is not None: s += 0.5 * min(max(q["syncnet_conf"], 0) / 8, 1)
    if q.get("identity_ref") is not None:
        s += q["identity_ref"] - (q["identity_src"] if q.get("identity_src") is not None else 0)
    if q.get("mask_outside_max") is not None: s -= 0.05 * max(0, q["mask_outside_max"] - 2)
    return round(s, 4)


def main():
    args = sys.argv[1:]
    out_json = None
    if "--json" in args:
        i = args.index("--json"); out_json = args[i + 1]; del args[i:i + 2]
    job = load_job(args[0]); D = job["_dir"]
    shot, idx, seg = find_segment(job, args[1])
    take = args[2]
    gen = os.path.join(D, "out", f"{take}.mp4")
    ref, wav = ensure_refs(job, shot, idx, seg)
    q = {"take": take, "seg": seg["id"]}

    import qa_lipsync
    lip = qa_lipsync.compare(qa_lipsync.mar_series(ref), qa_lipsync.mar_series(gen))
    q.update(lipsync_corr=lip["corr"], lipsync_amp=lip["amp_ratio"], lipsync_lag=lip["lag"],
             lipsync_weak=[w for w in lip["windows"] if w["corr"] is not None and w["corr"] < 0.4])
    print(f"[lip] corr {lip['corr']} · amp {lip['amp_ratio']} · atraso {lip['lag']}", flush=True)

    if "--no-syncnet" not in args and seg.get("speaker", "target") == "target":
        try:
            import qa_syncnet
            sn = qa_syncnet.measure(gen, wav)
            base_path = os.path.join(D, "out", f"ref_{seg['id']}.sync.json")
            if os.path.exists(base_path):
                base = json.load(open(base_path, encoding="utf-8"))
            else:
                base = qa_syncnet.measure(ref, wav)
                json.dump(base, open(base_path, "w", encoding="utf-8"))
            q.update(syncnet_conf=sn["lse_c"], syncnet_dist=sn["lse_d"], syncnet_offset=sn["offset"],
                     syncnet_src_conf=base["lse_c"], syncnet_weak=[w for w in sn["windows"] if w["conf"] < 1.5])
            print(f"[sync] LSE-C {sn['lse_c']:.2f} (fonte {base['lse_c']:.2f}) · offset {sn['offset']}", flush=True)
        except (ImportError, SystemExit, OSError) as e:  # sem torch, sem rosto ou sem rede: segue sem esse termo
            print(f"[sync] pulado: {e}", flush=True)

    if "--no-identity" not in args:
        try:
            import qa_identity
            refs = [job["character"]["image"]] + ([job["character"]["extra_image"]] if job["character"].get("extra_image") else [])
            refs = [p if os.path.isabs(p) else os.path.join(D, p) for p in refs]
            ident = qa_identity.measure(refs, gen, ref, step=6, backend=job["settings"].get("identity_backend", "arcface"), quiet=True)
            q.update(identity_ref=ident["id_ref_mean"], identity_src=ident["id_src_mean"], identity_p10=ident["id_ref_p10"],
                     identity_backend=ident["backend"])
            print(f"[id] ref {ident['id_ref_mean']} · fonte {ident['id_src_mean']} · backend {ident['backend']}", flush=True)
        except ImportError as e:
            print(f"[id] pulado: {e}", flush=True)

    if "--no-mask" not in args:
        import qa_mask
        m = qa_mask.check(ref, gen, os.path.join(D, "out", f"{take}.mask.jpg"), int(job["settings"].get("expansion_px", 144)), quiet=True)
        q.update(mask_outside_max=m["outside_max"], mask_worst_frame=m["worst"]["frame"] if m["worst"] else None)
        print(f"[máscara] pior {m['outside_max']}% fora", flush=True)

    q["score"] = score(q)
    print(f"NOTA {take}: {q['score']}")
    if out_json:
        json.dump(q, open(out_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
