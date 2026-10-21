# 12: API do workflow oficial (nós, IDs, modo segmento)

O grafo-base está em `assets/h3_character_swap.api.json`, exportado de `akatz-labs/h3-character-swap-tool/workflows/H3 Character Swap.api.json` no **commit `0670e4fdf95a`**.

> Desde 17/10/2026 o `main` usa o "Relay 2.0", com IDs descritivos (`source`, `reference`, `reference_conditioning`, `plan`, `select`, `expand_mask`, `finish`, `save`) e nós `H3RelayLoadHistory`/`H3RelaySaveHistory`. Esta tabela vale **só** para o commit fixado. Para migrar, reexporte o grafo e atualize o `run_job.py` (ver [15-fronteira.md](15-fronteira.md)).

## Nós (ID → papel → o que o `run_job.py` ajusta)

| ID | Classe | Papel | Ajuste |
|---|---|---|---|
| 1 | UNETLoader | `minimax_h3_ref2va_pruned_int8_convrot` | — |
| 2 | MiniMaxH3SigmaShift | shift vídeo 12 / áudio 3 | — |
| 3 | ModelAttentionBackend | comfy kitchen attention | — |
| 4 | LoraLoaderModelOnly | Turbo 8-step 768p | removido da cadeia se `turbo=false` (850 passa a ligar em 3) |
| 850 | LoraLoaderModelOnly | **swap LoRA** | `h3_character_swap_v1.5.safetensors` (o template vem com a v1) |
| 6 / 58 | CLIPLoader / SelectCLIPDevice | TE `nvfp4_awq` | device `default` (0.41.2 não tem `gpu:0`) |
| 7 / 8 | VAELoader | VAE de vídeo fp16 / áudio fp32 | — |
| 9 | LoadImage | referência do personagem | arquivo enviado |
| 30 | LoadVideo | clipe do segmento | arquivo enviado (áudio = voz isolada) |
| 31 | H3CharacterSwapPrepareVideo | 24 fps, canvas 480/768, recorte central | resolução do job |
| 100–107 | SAM 3.1 | detecta, seleciona, rastreia, recupera frames vazios | 101 texto do SAM, 104 seleção |
| 110 | H3CharacterSwapExpandMask | expansão radial | **`expansion_px`** (144 para figurino volumoso) |
| 111/112 | prévia da máscara | overlay verde | revisar se houver dúvida |
| 309 | H3CharacterSwapOptionalAnchor | âncora do 1º frame | `(none)` por padrão |
| 801 | H3CharacterSwapSettings | prompt, seed, audio_guide, steps, cfg, sampler `er_sde`, scheduler `normal` | prompt do segmento, seed |
| 803 | H3CharacterSwapShot | prepara o shot | **`segment_mode=True`**; continuação: `use_anchor=True`, `history_file` |
| 805 | H3CharacterSwapWindowPlan | janelas (ignoradas em modo segmento) | — |
| 806 | H3CharacterSwapController | executa as passadas | — |
| 807 | H3CharacterSwapAssemble | salva o MP4 com áudio | **ler a saída daqui**: `outputs["807"]["h3_character_swap"][0]["output"]`; result[0] = frames gerados |
| 900 | SaveH3History (nosso) | grava os últimos 18 frames em `input/hist_<take>.npz` | adicionado pelo `run_job.py` |
| 310 | LoadImage | 3º slot (`803.segment_reference`): âncora no meio do shot ou referência extra | adicionado pelo `run_job.py` quando há |
| 32 / 33 | LoadVideo / H3CharacterSwapPrepareVideo | clipe-guia (`--guide`): só `803.source_video`, `803.source`, `803.source_audio` apontam para eles; SAM segue no 31 | adicionados pelo `run_job.py` com `--guide` |
| 1 | H3LatentSyncWindow (nosso, `make_pod --latentsync`) | grafo à parte do `lipfix`: roda o LatentSync 1.6 num arquivo de `input/` e salva em `output/` | `outputs["1"]["video"][0]` |

## Modo segmento (prompt por segmento, como o app oficial)

- **`plan_segment(source_frames, h)`:** o clipe do segmento traz **h frames de contexto da fonte** antes do alvo. A janela é o menor `17n+5 ≥ alvo + 1`.
- **`history_file`:** um `.npz` com a chave `frames`, float32 [N, H, W, 3] em [0,1], com N = 1 ou 18, 35…. São os últimos frames **gerados** do segmento anterior. Ele passa a ser o estado inicial do relay, e a montagem descarta o prefixo.
- **Continuação:** sem âncora. `use_anchor=True` faz a "Picture 2" virar o boundary gerado. O prompt deve dizer: "<Picture 2> is the generated boundary from the preceding segment."
- **Áudio guia:** com `audio_guide=true` (padrão), o áudio do clipe entra como `ref_audio` e como guia do frame 0. Por isso o clipe leva a **voz isolada**.
- **Memória:** `activation_memory_gib` 17 é uma estimativa de colocação, não um limite.

## Referências (ordem de rótulos no prompt)

Por dentro (`relay/passes.py`): `ref_image_0` = personagem, `ref_image_1` = âncora/boundary (removido quando `use_anchor` é falso), `ref_image_2` = `segment_reference`, `ref_video_0` = clipe. O tokenizer numera na ordem, pulando os ausentes (`sampling.py`): por isso o slot extra vira `<Picture 2>` no 1º segmento sem âncora. Só o 1º frame de cada imagem conta (um lote de imagens no nó 9 **não** vira várias referências).

| Rótulo | Conteúdo |
|---|---|
| `<Picture 1>` | personagem |
| `<Picture 2>` | âncora (1º segmento com âncora), boundary gerado (continuação) ou, sem nenhum dos dois, o slot extra |
| `<Picture 3>` | slot extra quando há âncora/boundary |
| `<Video 1>` | clipe-fonte (ou o clipe-guia, com `--guide`) |
| `<Audio 1>` | áudio do clipe |

## Nome dos takes e histórico

`<seg>_s<seed>[_<guia>][_base][_h<4 hex>]`: `_base` = sem Turbo; `_hXXXX` = continuação, com os 4 primeiros hex do SHA-1 do take anterior usado. O `job.json` guarda em cada take `history_from`, `guide`, `turbo`, `anchor`, `extra` e, depois do `best`, o resumo `qa`. Takes do `lipfix` acrescentam `_lf<frame>`.

## ComfyUI fora do RunPod

Em todos os comandos, `<pod>` pode ser uma URL completa (`http://127.0.0.1:8188`) em vez do ID do pod.

## Alternativas avaliadas

- **`H3RelayWindowedEdit` (h3-relay):** janelas automáticas, mas **sem máscara** (regera o fundo inteiro) e com **prompt único** para todas as janelas. Bom fallback sem SAM.
- **Workflow nativo `MiniMaxH3ReferenceToVideo` simples:** uma passada só, sem histórico e sem máscara. Só para testes muito curtos.
