# 18: Plano de migração para a ferramenta 0.2.0 / H3 Relay 2.0

> **Status: plano, não executado.** A skill continua fixada no commit validado `0670e4fdf95a`. Este arquivo existe para que a migração seja um trabalho de uma sessão, não uma pesquisa do zero. Mapa feito em 21/10/2026 a partir do `main` da ferramenta (`5f83374`, merge do PR #1 de 17/10) e do `h3-relay` 2.0.0.

## Por que migrar (e por que não ter pressa)

**A favor:**
- O commit fixado vai envelhecer: o ComfyUI muda toda semana e os nós `H3CharacterSwap*` saíram do `main`.
- O Relay 2.0 traz, prontos: **H3 Ultimate 2× Enhance** e **LTX 2× Enhance** (upscale gerativo a partir do latente aceito, sem regerar), **Interpolate** (RIFE 4.26), rerolls por janela que sobrevivem a reinício, e o `Run staged · bounded RAM`.
- Grafo com nós nativos do ComfyUI (loaders, `MiniMaxH3ReferenceToVideo`, `SamplerCustomAdvanced`, `SaveVideo`).

**Contra pressa:**
- A validação oficial diz que a qualidade é praticamente a mesma (diferença média 1,48/255), não idêntica.
- Requer ComfyUI ≥ 0.37.0 (a imagem do RunPod usada tem 0.41.2: ok) e reinstalar ferramenta + Relay **juntos** (o contrato do grafo mudou).
- Os workflows novos usam loop nativo (`StartLoop`/`EndLoop`); o modo "um segmento por chamada" que o `run_job.py` usa passa a ser o `schedule: segment` do `H3RelayWindowPlan`.

## Mapa de nós (commit fixado → `main`)

| Papel | Commit `0670e4f` (ID numérico) | `main` (ID descritivo) | Classe nova |
|---|---|---|---|
| DiT | `1` | `model` | UNETLoader |
| Sigma shift | `2` | `shift` | MiniMaxH3SigmaShift |
| Atenção | `3` | `attention` | ModelAttentionBackend |
| Turbo | `4` | `turbo` | LoraLoaderModelOnly |
| LoRA de swap | `850` | `adapter` | LoraLoaderModelOnly (o JSON de exemplo traz outro arquivo; trocar para `h3_character_swap_v1.5.safetensors`) |
| Text encoder | `6` / `58` | `text` / `text_device` (+ `text_memory`) | CLIPLoader / SelectCLIPDevice / **H3RelayTextMemory** |
| VAEs | `7` / `8` | `video_vae` / `audio_vae` | VAELoader |
| Referência | `9` | `reference` | LoadImage |
| Clipe | `30` | `source` | LoadVideo |
| Preparação | `31` | `prepare` | **H3RelayPrepareSource** (`missing_audio: silence`) |
| SAM | `100`–`107` | `sam`, `subject`, `first_frame`, `detect`, `select`, `track`, `mask`, `recover` | SAM3_* nativos + **H3RelaySelectMask** / **H3RelayRecoverMasks** |
| Expansão | `110` | `expand_mask` | **H3RelayExpandMask** |
| Prévia da máscara | `111`/`112` | `mask_preview` | PreviewImage |
| Âncora | `309` | (entrada do `window`, `resize_anchor`) | — |
| Settings / prompt / seed | `801` | `plan` (seed, `seed_mode`, `seed_overrides`) + `reference_conditioning` (prompt) | **H3RelayWindowPlan** + MiniMaxH3ReferenceToVideo |
| Shot / segmento / histórico | `803` (`segment_mode`, `history_file`, `segment_reference`) | `plan.schedule = segment` + **H3RelayLoadHistory** ligado em `initial_history` | H3RelayWindowPlan / H3RelayLoadHistory |
| Janelas | `805`/`806` | `start` … `end` (loop nativo) com `window`, `history`, `encode_source`, `edit_mask`, `guide`, `sample`, `decode`, `append` | StartLoop/EndLoop, H3RelayWindowInputs, H3RelayApplyHistory, H3RelayApplyEditMask, MiniMaxH3AddGuide, SamplerCustomAdvanced… |
| Saída | `807` (lida pelo ID) | `finish` → `video` → `save` | **H3RelayFinishWindows** (`audio_mode: source`) + CreateVideo + SaveVideo |
| Histórico salvo | `900` (nosso `SaveH3History`) | **H3RelaySaveHistory** (FFV1 16 bits) | — (o nó próprio da skill deixa de ser necessário) |
| Sampler | dentro do `801` | `noise`, `guider`, `sampler`, `schedule` | RandomNoise, CFGGuider (cfg 1), KSamplerSelect (`er_sde`), BasicScheduler (`normal`, 8 steps) |

O app novo (`h3workbench/segment_jobs.py`) mostra como ele mesmo monta o segmento no grafo novo: `805.schedule = 'segment'`, `save_history` = `H3RelaySaveHistory` ligado em `807`, `load_history` = `H3RelayLoadHistory` ligado em `initial_history` de `805`, `803` e `append`, e `history.first_frame_guide = True` nas continuações.

## O que muda no `run_job.py`

1. Novo template (`assets/h3_character_swap_relay2.api.json`, reexportado do `main`) e uma tabela de IDs por versão (`TOOL_VERSION` em `make_pod.py`).
2. `segment_graph()`: escrever em `plan`/`reference_conditioning`/`expand_mask`/`select`/`subject` em vez de `801`/`110`/`104`/`101`; histórico por `H3RelayLoadHistory`/`H3RelaySaveHistory` (FFV1, não mais `.npz` de 213 MB).
3. Saída: ler do nó `save` (ou `finish`), não mais do `807`. Manter a regra "ler pelo ID do nó de saída".
4. `--guide`: o `prepare` novo recebe o clipe; o SAM usa a mesma saída. Será preciso um segundo `H3RelayPrepareSource` para o guia e ligar só `window`/`encode_source` nele, como hoje com os nós 32/33.
5. `segment_reference` (3º slot): mapear para a entrada equivalente do `window`/`reference_conditioning` (no app novo, `ref_images.ref_image_2` ← âncora).
6. `--no-turbo`: desligar `turbo` (ligar `adapter.model` em `attention`) e mudar `schedule.steps`/`sampler`.
7. `make_pod.py`: clonar ferramenta **e** `h3-relay` nos commits do release, juntos; remover o nó `SaveH3History`.

## Gates de aceitação (antes de trocar a receita)

- Mesmo clipe, máscara, prompt, seed e modelos nos dois grafos (o caso Sherlock A1 com seed 31337 é a referência: lip sync 0,75, ΔY do fundo −3).
- `qa_take.py` dos dois lados: nota, lip sync, SyncNet, identidade e máscara sem piora fora do ruído de seed.
- Emendas de continuação sem salto (histórico FFV1 ↔ `.npz`).
- `check` do `run_job.py` atualizado para as classes novas.
- Só então: trocar o commit no `make_pod.py`, atualizar `12-api-comfyui.md` e registrar em `10-falhas.md`.
