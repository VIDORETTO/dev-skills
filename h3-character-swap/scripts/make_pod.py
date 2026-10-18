"""Gera o JSON `body` para a ferramenta MCP `create-pod` do RunPod (pod pronto para character swap H3).

Uso:  python make_pod.py [--qwen] [--disk 180] [--name h3-swap] [--gpu "NVIDIA RTX PRO 6000 Blackwell Server Edition"]
      --qwen  inclui Qwen-Image-Edit 2511 (+text encoder +VAE) para gerar âncoras de 1º frame

O boot embutido resolve TODAS as armadilhas já vividas (ver references/06-runpod.md):
  - baixa só os modelos da receita para /workspace/mymodels (~45 GB, ou ~76 GB com --qwen) em ~1 min
  - HF_TOKEN vazio (o template injeta "token here", que quebra downloads)
  - MODEL_VOLUME_PATH=/workspace/mymodels (senão o template baixa +89 GB em paralelo)
  - extra_model_paths.yaml próprio + --extra-model-paths-config (evita a corrida que deixa as listas de modelos vazias)
  - remove --highvram (OOM em 96 GB com 768p/124 frames)
  - instala os nós oficiais akatz-labs/h3-character-swap-tool + nó SaveH3History (histórico entre segmentos)
"""
import argparse, json
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ap = argparse.ArgumentParser()
ap.add_argument("--qwen", action="store_true")
ap.add_argument("--disk", type=int, default=0)
ap.add_argument("--name", default="h3-swap")
ap.add_argument("--gpu", default="NVIDIA RTX PRO 6000 Blackwell Server Edition")
a = ap.parse_args()

# Versão VALIDADA da ferramenta (grafo, IDs 801/803/807, modo segmento). Em 17/10/2026 o main migrou para
# "Relay 2.0" e removeu worker_nodes/h3_character_swap — NÃO trocar o commit sem revalidar (ver references/12-api-comfyui.md).
TOOL_COMMIT = "0670e4fdf95a"

MODELS = [
    ("vae", "Comfy-Org/MiniMax-H3", "vae/minimax_h3_video_vae_fp16.safetensors"),
    ("vae", "Comfy-Org/MiniMax-H3", "vae/minimax_h3_audio_vae_fp32.safetensors"),
    ("loras", "akatz-ai/MiniMax-H3-Character-Swap-LoRA", "h3_character_swap_v1.5.safetensors"),
    ("loras", "lightx2v/Minimax-h3-Turbo", "minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors"),
    ("checkpoints", "Comfy-Org/sam3.1", "checkpoints/sam3.1_multiplex_fp16.safetensors"),
    ("text_encoders", "Comfy-Org/MiniMax-H3", "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"),
    ("diffusion_models", "Comfy-Org/MiniMax-H3", "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors"),
]
if a.qwen:
    MODELS += [
        ("vae", "Comfy-Org/Qwen-Image_ComfyUI", "split_files/vae/qwen_image_vae.safetensors"),
        ("text_encoders", "Comfy-Org/Qwen-Image_ComfyUI", "split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"),
        ("diffusion_models", "Comfy-Org/Qwen-Image-Edit_ComfyUI", "split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors"),
    ]
items = ",\n".join(f"({s!r},{r!r},{p!r})" for s, r, p in MODELS)

download = f"""python3 - <<'PYEOF'
import os, shutil, time
os.environ.pop('HF_TOKEN', None)
from huggingface_hub import hf_hub_download
ROOT='/workspace/mymodels'
ITEMS=[
{items}
]
t=time.time()
for sub,repo,path in ITEMS:
    dest=os.path.join(ROOT,sub,os.path.basename(path)); os.makedirs(os.path.dirname(dest),exist_ok=True)
    if os.path.exists(dest): continue
    for a in range(3):
        try:
            got=hf_hub_download(repo,path,local_dir=os.path.join(ROOT,'.tmp')); shutil.move(got,dest); print('SEED ok',dest,round(time.time()-t),'s',flush=True); break
        except Exception as e: print('SEED retry',path,e,flush=True)
shutil.rmtree(os.path.join(ROOT,'.tmp'),ignore_errors=True)
open('/workspace/my_extra_paths.yaml','w').write('mine:\\n  base_path: /workspace/mymodels\\n  diffusion_models: diffusion_models\\n  text_encoders: text_encoders\\n  loras: loras\\n  vae: vae\\n  checkpoints: checkpoints\\n')
print('SEED_DONE',flush=True)
PYEOF"""

node = """mkdir -p /opt/comfyui-baked/custom_nodes/h3_hist_save && cat > /opt/comfyui-baked/custom_nodes/h3_hist_save/__init__.py <<'NODEEOF'
import os, numpy as np, folder_paths
class SaveH3History:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'frames': ('IMAGE',), 'filename': ('STRING', {'default': 'hist.npz'}), 'count': ('INT', {'default': 18, 'min': 1, 'max': 341})}}
    RETURN_TYPES = ()
    FUNCTION = 'save'
    OUTPUT_NODE = True
    CATEGORY = 'H3 Character Swap/custom'
    def save(self, frames, filename, count):
        p = os.path.join(folder_paths.get_input_directory(), os.path.basename(filename))
        a = frames[-count:].clamp(0, 1).float().cpu().numpy().astype(np.float32)
        np.savez(p, frames=a)
        return {'ui': {'text': [f'{p} {list(a.shape)}']}}
NODE_CLASS_MAPPINGS = {'SaveH3History': SaveH3History}
NODEEOF
echo HIST_NODE_OK"""

cmd = "\n".join([
    "pip install -q huggingface_hub hf_xet scipy opencv-python-headless >/tmp/pip.log 2>&1; echo PIP_DONE $?",
    download,
    f"if [ ! -d /opt/comfyui-baked/custom_nodes/h3_character_swap ]; then git clone https://github.com/akatz-labs/h3-character-swap-tool /tmp/swaptool && git -C /tmp/swaptool checkout -q {TOOL_COMMIT} && cp -r /tmp/swaptool/worker_nodes/h3_character_swap /opt/comfyui-baked/custom_nodes/h3_character_swap && echo TOOL_NODES_OK; fi",
    node,
    "sed -i 's/--highvram //; s#--force-fp16#--force-fp16 --extra-model-paths-config /workspace/my_extra_paths.yaml#' /usr/local/bin/custom-entrypoint.sh && grep -n 'extra-model-paths' /usr/local/bin/custom-entrypoint.sh",
    "exec /usr/local/bin/custom-entrypoint.sh",
])

body = {
    "name": a.name,
    "templateId": "bii5d425kp",  # OneClick - ComfyUI - MiniMax H3 Uncensored - CU13 (huchukato cu13-mmh3, ComfyUI 0.41.2 c/ SAM3 nativo)
    "cloud": "SECURE",
    "gpu": {"id": a.gpu, "count": 1, "minCudaVersion": "13.0"},
    "disk": a.disk or (180 if a.qwen else 150),
    "env": {"HF_TOKEN": "", "MODEL_VOLUME_PATH": "/workspace/mymodels"},
    "entrypoint": ["/bin/bash", "-c"],
    "cmd": [cmd],
}
print(json.dumps(body, ensure_ascii=False))
