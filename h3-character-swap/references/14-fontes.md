# 14: Fontes

## Oficiais (prioridade máxima)

- **LoRA (README v1.5, receita testada):** https://huggingface.co/akatz-ai/MiniMax-H3-Character-Swap-LoRA
- **Model card da V1, com treino e limitações:** https://huggingface.co/akatz-ai/MiniMax-H3-Character-Swap-LoRA/blob/a665bb7e3bb9804e487d2925f67744f554c8ad49/README.md
- **Discussões do LoRA:** #9 (5 s / 124 frames é o ponto ideal), #2 (vazamentos e "From the VERY first frame"), #7 (cai muito por volta de 15 s): https://huggingface.co/akatz-ai/MiniMax-H3-Character-Swap-LoRA/discussions
- **Ferramenta oficial (app + nós + workflow):** https://github.com/akatz-labs/h3-character-swap-tool
  - `workflows/README.md`, `workflows/VALIDATION.md` e `workflows/H3 Character Swap.api.json`
  - `h3workbench/media.py` e `segments.py` (templates de prompt) e `anchors.py` (brief da âncora)
  - `worker_nodes/h3_character_swap/` (máscara, histórico, difusão mascarada)
- **h3-relay (janelas e histórico):** https://github.com/akatz-ai/h3-relay, com `docs/windowed-edit.md`
- **Guia oficial de prompt H3 (full-reference):** https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md
- **Guia base (T2VA/I2VA etc.):** `docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md` no mesmo repositório

## Comunidade (útil, mas não oficial; validar antes de adotar)

- **Lip sync com stems isolados, base de 20 steps nos closes, prompt de comportamento da boca:** https://note.com/joh_luck/n/n6c4679754d8f
- **Testar em ~0,2 MP primeiro; 6 ou mais steps melhoram lip sync; cancelar cedo via live preview:** https://note.com/synth_brain/n/nbd4c5297e6f4
- **Contrato de substituição, checklist de pontos críticos e modos de falha:** https://www.seedance.tv/blog/minimax-h3-character-replacement-workflow
- **"Image = identity, Video = performance, Prompt = routing"; ordem de depuração; seeds:** https://www.virse.ai/blog/how-to-replace-a-character-in-video-with-minimax-h3
- **Workflow v1.1 com SAM3 e trechos de 5 s:** https://civitai.com/models/2843905/mini-max-character-replace-with-turbo-lora-4-steps
- **Resumo do LoRA:** https://comfyui-wiki.com/en/news/2026-09-25-h3-character-swap-lora
- **Guias de prompt H3 (terceiros):**
  - https://aireiter.com/blog/minimax-h3-prompt-guide
  - https://www.ambienceai.com/tutorials/minimax-h3-prompting-guide
  - https://www.rundiffusion.com/minimax-h3-prompt-guide
- **Grow mask para personagem maior, cabelo e acessórios (Wan Animate, princípio análogo):** https://www.runcomfy.com/comfyui-workflows/wan-2-2-animate-swap-characters-lip-sync-workflow-comfyui

## Usadas nas melhorias de 21/10/2026

- **Genjutsu-Skill (profundidade + face mesh no lugar da pessoa, rascunho → HD, áudio original):** https://github.com/SaeedAngiz1/Genjutsu-Skill
- **Ferramenta 0.2.0 / Relay 2.0 (PRs de 17/10):** https://github.com/akatz-labs/h3-character-swap-tool/pull/1 · https://github.com/akatz-ai/h3-relay/pull/1 · `docs/toolkit-v2.md`
- **SyncNet oficial (LSE-C/LSE-D):** https://github.com/joonson/syncnet_python (modelo `syncnet_v2` da VGG/Oxford)
- **LatentSync 1.6 (reparo de boca, 512 px, ~18 GB de VRAM):** https://github.com/bytedance/LatentSync · https://huggingface.co/ByteDance/LatentSync-1.6
- **InsightFace / ArcFace (`buffalo_l`):** https://github.com/deepinsight/insightface
- **Depth Anything V2 Small:** https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf · **MiDaS:** https://github.com/isl-org/MiDaS
- **Alissonerdx Character Swap v1.1 (alternativa ao akatz):** https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI · https://comfyui-wiki.com/en/news/2026-10-18-h3-character-swap-v1-1 · https://artrealmai.com/article/minimax-h3-character-swap-lora-v1-1-comfyui · https://comfyui-wiki.com/en/news/2026-10-13-h3-character-swap-live-wallpaper · https://x.com/Alissonerdx/status/2109749038773833731 (detalhes em [19](19-lora-alissonerdx.md))
- **Âncora de frame editado (pesquisa de 21/10):** Viggle-Animate https://viggle.ai/research/viggle-animate-character-replacement-from-a-repainted-frame · Luma Modify https://docs.lumalabs.ai/docs/modify-video · anchor frame method https://invideo.io/blog/anchor-frame-method-ai-video/ · Scenario https://www.scenario.com/blog/keep-shot-swap-character-p-video-replace-scenario · H3 FL2VA/Ref2VA https://www.domoai.app/blog/minimax-h3-reference-to-video · BFS https://huggingface.co/Alissonerdx/BFS-Best-Face-Swap · QIE-2511 Guided Head Swap https://huggingface.co/prithivMLmods/QIE-2511-Guided-Head-Face-Swap
- **Comparação de modelos abertos de lip sync (2026):** https://instavar.com/research/ai-video/open-source-lip-sync-models · **ComplexSync (limites de LatentSync/MuseTalk):** https://arxiv.org/html/2609.29225v1

## Lacunas da pesquisa

- **Reddit e X/Twitter:** as buscas não trouxeram threads úteis sobre H3 character swap. A maior parte do material está no HF, no GitHub, em blogs e no note.com.
- **Mais fontes:** vale repetir a busca periodicamente e acompanhar as discussões do LoRA e as issues da ferramenta.
