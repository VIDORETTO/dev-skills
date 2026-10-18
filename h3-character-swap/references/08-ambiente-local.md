# 08: Ambiente local (CPU) para análise e QA

O `prepare.py` e os scripts `qa_*.py` precisam de um venv com rembg, OpenCV, MediaPipe, Demucs e faster-whisper. O `run_job.py`, o `make_pod.py` e o `assemble.py` usam só stdlib e ffmpeg.

## Requisitos

- **ffmpeg e ffprobe no PATH:** precisam do build *full*, com `zscale` (libzimg) para o tone mapping de HDR. No Windows, o `winget install Gyan.FFmpeg` serve.
- **Python 3.12:** o mediapipe e o torch-cpu podem não ter wheels para 3.14.

## Criar o venv (Windows / Git Bash)

```bash
PY312="$LOCALAPPDATA/Programs/Python/Python312/python.exe"
"$PY312" -m venv "$LOCALAPPDATA/Temp/cswap-venv"     # use caminho CURTO (venv em caminho longo falha no ensurepip)
V="$LOCALAPPDATA/Temp/cswap-venv/Scripts/python.exe"
"$V" -m pip install "rembg[cpu]" opencv-python-headless mediapipe scipy soundfile
"$V" -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
"$V" -m pip install demucs faster-whisper
```

Na primeira execução, o rembg baixa o `u2net_human_seg` (176 MB), o Whisper large-v3 baixa ~3 GB e o `qa_lipsync.py` baixa o FaceLandmarker (3,7 MB) para `~/.cache/h3swap/`.

Se o venv `%LOCALAPPDATA%\Temp\cswap-venv` já existir, reutilize. Foi esta a configuração validada.

## Problemas já vistos

| Sintoma | Correção |
|---|---|
| `ensurepip` falha ao criar o venv | O caminho é longo demais; crie o venv em pasta curta |
| `av.open() got an unexpected keyword 'metadata_errors'` no faster-whisper | Passar as amostras numpy (wav 16 kHz mono), não o caminho. O `prepare.py` já faz isso |
| `mediapipe` sem `solutions` | Versões 1.x usam `mediapipe.tasks` (FaceLandmarker), e os scripts já usam essa API |
| Aviso de symlink do HF no Windows | Inofensivo; defina `HF_HUB_DISABLE_SYMLINKS_WARNING=1` |
| Python com `-I` ignora `PYTHONIOENCODING` | Use `sys.stdout.reconfigure(encoding="utf-8")` |

## Tempos de CPU (22,5 s de vídeo)

- **Demucs:** ~6 s.
- **Whisper large-v3 (int8):** ~1–2 min.
- **rembg (presença com stride 2):** ~2–3 min.
- **QA de lip sync:** ~20 s por vídeo.
