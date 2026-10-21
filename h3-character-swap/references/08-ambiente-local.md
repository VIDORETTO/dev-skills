# 08: Ambiente local (CPU) para análise e QA

O `prepare.py`, o `composite.py`, o `make_guide.py` e os scripts `qa_*.py` precisam de um venv com rembg, OpenCV, MediaPipe, Demucs, faster-whisper e InsightFace (o torch já vem com o Demucs). O `run_job.py`, o `make_pod.py` e o `assemble.py` usam só stdlib e ffmpeg.

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
"$V" -m pip install insightface onnxruntime python_speech_features   # qa_identity, qa_syncnet
"$V" -m pip install transformers timm                                 # make_guide (Depth Anything V2 / MiDaS), opcional
```

Na primeira execução, o rembg baixa o `u2net_human_seg` (176 MB), o Whisper large-v3 baixa ~3 GB e o `qa_lipsync.py` baixa o FaceLandmarker (3,7 MB) para `~/.cache/h3swap/`. O `qa_identity.py` baixa o `buffalo_l` (~280 MB) para `~/.insightface/`; o `qa_syncnet.py` baixa o repositório oficial e o `syncnet_v2.model` (~50 MB) para `~/.cache/h3swap/`; o `make_guide.py` baixa o Depth Anything V2 Small (~100 MB) do Hugging Face.

O `run_job.py best` chama o `qa_take.py` com o python do venv: ele procura `H3_VPY`, depois `%LOCALAPPDATA%\Temp\cswap-venv\Scripts\python.exe`.

Se o venv `%LOCALAPPDATA%\Temp\cswap-venv` já existir, reutilize. Foi esta a configuração validada.

## Problemas já vistos

| Sintoma | Correção |
|---|---|
| `ensurepip` falha ao criar o venv | O caminho é longo demais; crie o venv em pasta curta |
| `av.open() got an unexpected keyword 'metadata_errors'` no faster-whisper | Passar as amostras numpy (wav 16 kHz mono), não o caminho. O `prepare.py` já faz isso |
| `mediapipe` sem `solutions` | Versões 1.x usam `mediapipe.tasks` (FaceLandmarker), e os scripts já usam essa API |
| Aviso de symlink do HF no Windows | Inofensivo; defina `HF_HUB_DISABLE_SYMLINKS_WARNING=1` |
| Python com `-I` ignora `PYTHONIOENCODING` | Use `sys.stdout.reconfigure(encoding="utf-8")` |
| Linux sem interface: `libEGL.so.1: cannot open shared object file` no MediaPipe | `apt install libegl1 libgles2` |
| `insightface` não compila no Windows | Use uma versão com wheel pronta (`pip install insightface` recente) ou o Python 3.12 do venv validado |

## Tempos de CPU (22,5 s de vídeo)

- **Demucs:** ~6 s.
- **Whisper large-v3 (int8):** ~1–2 min.
- **rembg (presença com stride 2):** ~2–3 min.
- **QA de lip sync:** ~20 s por vídeo.
- **QA de um take (`qa_take`, sem SyncNet):** ~25–40 s por segmento de 5 s.
- **`composite.py`:** ~1–1,5 s por frame gerado (dois rembg por frame).
