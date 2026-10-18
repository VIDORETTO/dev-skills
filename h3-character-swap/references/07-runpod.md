# 07: RunPod (deploy rápido, barato e sem cobrança parada)

## Criar o pod

```bash
python scripts/make_pod.py           # só H3 + SAM (~45 GB, disco de 150 GB)
python scripts/make_pod.py --qwen    # + Qwen-Image-Edit 2511 para âncoras (~76 GB, disco de 180 GB)
```

A saída é o `body` da ferramenta MCP `create-pod`. Antes de criar, leia o guia `runpod-mcp` (`read-guide`) se ainda não leu nesta sessão. Informe ao usuário o preço/h que o create devolver: a RTX PRO 6000 é cobrada a **US$ 2,49/h**, não os US$ 1,69 que aparecem na tabela de capacidade.

- **Template:** `bii5d425kp` ("OneClick - ComfyUI - MiniMax H3 Uncensored - CU13", imagem `huchukato/comfyui-qwenvl-runpod:cu13-mmh3`, ComfyUI 0.41.2 com SAM3 nativo).
- **GPU padrão:** `NVIDIA RTX PRO 6000 Blackwell Server Edition` (96 GB), `minCudaVersion 13.0`, cloud SECURE. Na falta dela, use H100/H200 (80+ GB). A RTX 5090 (32 GB) não comporta 768p.
- **Sem volume:** o boot baixa os modelos a ~1 GB/s (~20–60 s). Volume de rede só faz sentido se o usuário pedir uso recorrente. Ele custa armazenamento parado e exige saldo ≥ US$ 5.

## O que o boot do `make_pod.py` resolve

| Armadilha (já aconteceu) | Correção embutida |
|---|---|
| `HF_TOKEN="token here"` do template quebra downloads | `env HF_TOKEN=""` e `os.environ.pop` |
| O template baixa 89 GB em paralelo se não achar a pasta de modelos | `MODEL_VOLUME_PATH=/workspace/mymodels` |
| O ComfyUI sobe antes do `extra_model_paths.yaml` e as listas ficam vazias (corrida) | yaml próprio mais `--extra-model-paths-config` via `sed` no entrypoint |
| OOM em 96 GB (768p, 124+ frames) | `sed` remove `--highvram` |
| Nós da ferramenta oficial ausentes | clona `akatz-labs/h3-character-swap-tool` e copia `worker_nodes/h3_character_swap` para `/opt/comfyui-baked/custom_nodes` (o entrypoint copia para o workspace) |
| O histórico entre segmentos (~213 MB `.npz`) não passa no upload do proxy | nó próprio `SaveH3History` grava em `input/` **no pod** |
| OOM no download com `HF_XET_HIGH_PERFORMANCE` em máquina com pouca RAM | não usar; a máquina GPU tem RAM de sobra |

## Depois de criar

1. Fazer polling de `https://<podId>-8188.proxy.runpod.net/system_stats` até responder 200. Usar user-agent de curl: o proxy devolve **403** ao urllib.
2. Rodar `python scripts/run_job.py JOB/job.json check <podId>`. Ele confere nós, listas de modelos e argv.
3. Logs: a ferramenta `stream-pod-logs` com `source: container`. Use `since` para não estourar o limite. A saída é grande e o `tail` alto estoura.

## API do ComfyUI pelo proxy

- **Upload:** `POST /upload/image` (também serve para vídeo), limite de **~100 MB**. Recomprimir com CRF 20–22 se passar.
- **Fila:** `POST /prompt`, depois `GET /history/{id}`, depois `GET /view?filename&subfolder&type`.
- **Saída:** ler **somente o nó de saída pelo ID** (807 na ferramenta). O history também lista o `LoadVideo`, a entrada, e isso já gerou um falso "não trocou".
- **Cancelar:** `POST /interrupt` (o atual) e `POST /queue {"clear": true}` (os pendentes).
- **Sem reboot:** o ComfyUI-Manager desta imagem não expõe reboot (`/manager/reboot` dá 404). Para reiniciar, recrie o pod.

## Encerrar

- **Ao terminar:** `delete-pod` no pod criado, depois `list-pods` e `list-network-volumes`, e informe que está zerado.
- **Revisão do usuário:** se ele ainda for revisar e talvez pedir reroll, pergunte antes de desligar. O padrão é **desligar**: recriar custa ~3 min.
- **Escopo:** só apague recursos criados nesta conversa ou nomeados pelo usuário.

## Custos reais registrados (17/10/2026)

| Rodada | Tempo de pod | Custo |
|---|---|---|
| 2 (relay, 5 janelas) | ~25 min | ~US$ 1,00 |
| 3 (ferramenta, 2 shots) | ~25 min | ~US$ 1,00 |
| 4 (segmentos, âncoras, 9 takes de teste) | ~80 min | ~US$ 3,30 |
