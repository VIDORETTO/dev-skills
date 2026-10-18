---
name: h3-character-swap
description: Troca de personagem em vídeo (character swap / character replacement / substituir pessoa no vídeo) com MiniMax H3 + LoRA akatz-ai Character Swap v1.5 no ComfyUI, rodando em GPU alugada no RunPod. Cobre a análise prévia local (HDR→SDR, transcrição Whisper, voz isolada Demucs, detecção de presença/shots, segmentação nas pausas), o deploy do pod já pronto, a geração por segmentos com máscara SAM 3.1 e histórico, o QA objetivo de lip sync/máscara/cor e a montagem final com o áudio original. Use SEMPRE que o usuário quiser trocar/substituir uma pessoa de um vídeo por um personagem de imagem de referência, falar de MiniMax H3, ref2va, akatz, h3-relay, h3-character-swap-tool, lip sync de swap, ou rodar ComfyUI de vídeo no RunPod — mesmo que não diga "skill" nem "LoRA".
---

# H3 Character Swap (MiniMax H3 + akatz LoRA v1.5)

Substitui a pessoa de um vídeo-fonte por um personagem dado em imagem. O personagem mantém a performance (pose, fala, timing e câmera), a cena fica intacta e o áudio original é preservado. A receita foi validada em 4 rodadas reais; a última foi avaliada pelo usuário como "ficou perfeito". O histórico completo está em [references/11-caso-sherlock.md](references/11-caso-sherlock.md).

O fluxo é longo e caro em GPU, e cada regra abaixo existe porque a sua ausência já estragou um resultado real. Siga a ordem: **análise local grátis → aprovação do usuário → GPU curta → QA com números → montagem → desligar tudo.**

## Regras de ouro (e por quê)

1. **Converter HDR para SDR antes de tudo.** Vídeo de celular costuma ser HLG/PQ. O H3 recebe isso como SDR lavado, "corrige" e devolve cores e contraste errados.
2. **Pessoa fora de quadro = shot `preserve` (vídeo original).** Sem pessoa, o modelo inventa o personagem na cena vazia, e a ferramenta oficial chega a recusar o shot ("split the source shot").
3. **Usar a ferramenta oficial com máscara SAM** (`akatz-labs/h3-character-swap-tool`). Fora da máscara o latente da fonte é preservado e o fundo fica idêntico (~44 dB). Os workflows sem máscara regeneram o quadro inteiro.
4. **Máscara proporcional ao figurino** (`expansion_px` de 128 a 160 para chapéu, cabelo volumoso ou capa). O padrão de 64 px corta o que passa da silhueta original, e o fundo original "apaga" o chapéu.
5. **Prompt por segmento** com o diálogo transcrito em `<d>[Língua] …</d>` **e as ações não verbais com tempo** (sopro, respiração, pausa, riso). O lip sync do H3 é dirigido pelo texto + áudio. Descrever o sopro do usuário levou a correlação de 0,41 a 0,67.
6. **Voz isolada (Demucs) no condicionamento, áudio original na entrega.** Ruído confunde a boca. Trocar o áudio depois (remux) nunca conserta lip sync.
7. **Segmentos de ~4–6,5 s**, cortados nas pausas e encadeados por 18 frames de histórico. Acima de ~10 s o LoRA perde identidade e lip sync (palavra do próprio autor). O ponto ideal é 124 frames.
8. **Âncora de 1º frame é opcional; decida por A/B.** Em close de selfie, a âncora do Qwen derrubou o lip sync de 0,67 para 0,28. Com a pessoa parcial na borda, ela inventou uma segunda pessoa.
9. **Seeds variam muito** (0,58 contra 0,75 com o mesmo prompt). Teste 2–3 seeds no 1º segmento de cada shot e escolha pela QA.
10. **Medir antes de entregar:** `qa_lipsync.py`, `qa_mask.py` e `qa_color.py`. Grades de frames esconderam o lip sync ruim, e a medição o revelou.
11. **Ler a saída só do nó 807 (pelo ID).** O history do ComfyUI também lista o vídeo de entrada, e isso já produziu um falso "não trocou".
12. **Ferramenta fixada no commit validado** (`0670e4fdf95a`). Em 17/10/2026 o `main` virou "Relay 2.0" e removeu os nós que a skill usa; o `make_pod.py` já faz o checkout certo. Antes de um trabalho grande, pesquise novidades (HF akatz-ai / Alissonerdx, GitHub, r/StableDiffusion), porque o ecossistema muda toda semana.
13. **Dinheiro:** estimar o custo e pedir o OK **antes** de criar o pod; desligar o pod ao terminar e confirmar com `list-pods` e `list-network-volumes` vazios. Não deixe nenhuma cobrança parada (sem volume persistente por padrão).

## Fluxo

`S` = `scripts/` desta skill. `VPY` = python do venv local, que tem rembg, mediapipe, demucs e faster-whisper (setup em [references/08-ambiente-local.md](references/08-ambiente-local.md); reutilize `%LOCALAPPDATA%\Temp\cswap-venv` se já existir). Os demais scripts usam só stdlib.

### Fase A: análise prévia local (CPU, grátis)

```bash
VPY S/prepare.py --video <video> --character <ref.png> --out <JOB> --lang pt --res 768
```

Ele gera `JOB/analysis.md`, `job.json` (rascunho), `clips/` (já com a voz isolada e os 18 frames de contexto nas continuações) e `frames/`. Depois, siga [references/00-analise-previa.md](references/00-analise-previa.md):

- **Revisar os shots:** `generate` contra `preserve`, e os cortes de câmera.
- **Revisar a transcrição:** o Whisper varia entre execuções e já omitiu palavras.
- **Rotular os ⚠️ sons vocais sem palavra:** sopro, respiração, riso. **Pergunte ao usuário** se não estiver claro; ele conhece o próprio vídeo.
- **Preencher `character.description`:** rosto, cabelo e cada peça de roupa. Veja exemplos em [references/13-exemplos.md](references/13-exemplos.md).
- **Escrever `behavior` em cada segmento:** ações com tempos relativos.
- **Ajustar `settings.expansion_px`.**
- **Conferir os prompts:** `python S/run_job.py JOB/job.json prompt <seg>`.
- **Relatório prévio:** apresente ao usuário o plano, os riscos e a estimativa de custo (modelo em [00-analise-previa.md](references/00-analise-previa.md)) e **espere o OK**.

### Fase B: GPU (RunPod)

1. **Criar o pod:** `python S/make_pod.py [--qwen]` gera o JSON. Passe-o para a ferramenta MCP `create-pod` (leia antes o guia `runpod-mcp` via `read-guide`, se ainda não leu). Informe o preço/h devolvido; a RTX PRO 6000 custa US$ 2,49/h. Detalhes e armadilhas em [references/07-runpod.md](references/07-runpod.md).
2. **Esperar o pod:** polling de `https://<pod>-8188.proxy.runpod.net/system_stats` (com user-agent de curl), depois `python S/run_job.py JOB/job.json check <pod>`.
3. **Primeiro segmento de cada shot, 2–3 seeds:** `python S/run_job.py JOB/job.json seg <pod> A1 --seed <N>`. Shots independentes podem ir para a fila junto.
4. **QA de cada take** ([references/09-qa.md](references/09-qa.md)) e `select <seg> <take>` no melhor.
5. **Encadear o resto:** `python S/run_job.py JOB/job.json chain <pod> <shot>`, com QA por segmento. Segmento reprovado: `seg … --seed`, `select` e regerar os seguintes, porque eles dependem do histórico.
6. **Montar:** `python S/assemble.py JOB/job.json JOB/final.mp4`. Saem também o `final_ref.mp4` e o QA completo contra ele.
7. **Desligar:** `delete-pod`, depois `list-pods` e `list-network-volumes`. Avise que está zerado.

### Fase C: entrega

Envie o `final.mp4` e reporte **com números**: lip sync por shot e janelas fracas, máscara, cor do fundo, frames iguais à fonte, custo e estado do RunPod. Seja honesto sobre o que ficou abaixo do ideal e por quê (modelo em [13-exemplos.md](references/13-exemplos.md)). Registre lições novas em `references/10-falhas.md`.

## Decisões rápidas

| Situação | Decisão |
|---|---|
| Close de selfie, fala | Sem âncora; `behavior` detalhado; 2–3 seeds no 1º segmento |
| Plano médio ou aberto, personagem bem diferente | Testar âncora (`make_pod --qwen`, `run_job anchor`, 3 seeds); usar só se a QA melhorar |
| Pessoa entra ou sai pela borda no 1º frame do shot | Nunca usar âncora nesse shot |
| Chapéu, cabelo armado, capa | `expansion_px` de 144–160; conferir com `qa_mask.py` |
| Várias pessoas na cena | `sam_text` específico ("bald man in dark t-shirt"), `selection` (`largest`, `leftmost`, `rightmost`, `index`) |
| Corte de câmera | Um shot por corte (o prepare detecta) |
| Close com boca "pequena" que sai exagerada | Mais seeds e "small, barely opened lip movements" no `behavior`. É limite conhecido do LoRA: avise o usuário |
| Vazamento do original (mãos, dentes, acessórios) | Trocar a seed (dica do fórum); "From the very first frame…" já está no prompt |
| Iteração barata | `--res 480` no prepare (≈ metade do custo); final em 768 |
| O usuário quer mais fidelidade do que a receita atual dá | Ler [15-fronteira.md](references/15-fronteira.md) e propor um A/B barato (1º segmento): LoRA Alissonerdx v1.1 de guide alinhado, segundo passe LMS, base sem Turbo |
| O personagem novo é menor ou mais estreito que a pessoa original | A silhueta original pode sobrar: usar antes o Person Remover LoRA (backplate) e depois inserir o personagem ([15-fronteira.md](references/15-fronteira.md)) |
| Lip sync ainda ruim num close difícil | Testar `settings.turbo=false` (20 steps `res_multistep`): a comunidade relata sincronia melhor. Ainda não validado aqui |

## Mapa das referências (leia quando precisar)

| Arquivo | Quando ler |
|---|---|
| [00-analise-previa.md](references/00-analise-previa.md) | **Sempre**, na fase A: checklist, perguntas, estimativa e relatório prévio |
| [01-pipeline.md](references/01-pipeline.md) | Passo a passo com comandos, gates e prioridade de correções |
| [02-preprocessamento.md](references/02-preprocessamento.md) | HDR, fps, shots, voz isolada, transcrição (detalhes e comandos ffmpeg) |
| [03-prompt.md](references/03-prompt.md) | Formato oficial H3 (seis seções, `<d>`, falantes), template do app, armadilhas |
| [04-mascara.md](references/04-mascara.md) | SAM 3.1, expansão, revisão e correção da máscara |
| [05-ancora.md](references/05-ancora.md) | Âncora com Qwen-Image-Edit 2511: quando usar e quando evitar |
| [06-parametros.md](references/06-parametros.md) | Modelos, sampler, Turbo e base, janelas, seeds, resolução, memória |
| [07-runpod.md](references/07-runpod.md) | Deploy, boot, API pelo proxy, custos, encerrar |
| [08-ambiente-local.md](references/08-ambiente-local.md) | Venv local e problemas conhecidos |
| [09-qa.md](references/09-qa.md) | Como medir e interpretar lip sync, máscara, cor e emendas |
| [10-falhas.md](references/10-falhas.md) | Todo defeito já visto, com causa e correção. Consulte antes de improvisar |
| [11-caso-sherlock.md](references/11-caso-sherlock.md) | Caso real completo com números por rodada |
| [12-api-comfyui.md](references/12-api-comfyui.md) | IDs dos nós do grafo oficial, modo segmento, histórico, saídas |
| [13-exemplos.md](references/13-exemplos.md) | Descrições de personagem, `behavior`, prompt montado, `job.json`, relatórios |
| [14-fontes.md](references/14-fontes.md) | Fontes oficiais e da comunidade |
| [15-fronteira.md](references/15-fronteira.md) | **Estado da arte e alavancas não testadas** (LoRA Alissonerdx v1.1 de guide alinhado, Head Swap, segundo passe LMS/upscale, LoRA de identidade, Person Remover), concorrentes e o refactor Relay 2.0. Leia quando o usuário quiser mais qualidade do que a receita atual entrega |

## Scripts

| Script | Python | Função |
|---|---|---|
| `prepare.py` | venv | Análise prévia completa: SDR, Demucs, Whisper, eventos não verbais, presença com histerese e filtro de pico, cortes, shots, segmentos, clipes, frames, `job.json`, `analysis.md` |
| `make_pod.py` | qualquer | JSON do `create-pod` com o boot à prova das armadilhas conhecidas |
| `run_job.py` | qualquer | `check`, `prompt`, `anchor`, `seg`, `select`, `chain` contra o ComfyUI do pod |
| `assemble.py` | qualquer | Final = takes escolhidos + trechos `preserve` + áudio original; gera `_ref.mp4` para QA |
| `qa_lipsync.py` | venv | Correlação da boca por segundo, atraso e amplitude |
| `qa_mask.py` | venv | % do personagem fora da máscara (recorte de chapéu ou cabelo) |
| `qa_color.py` | venv | Cor e brilho **do fundo** contra a fonte |
| `h3common.py` | — | Canvas idêntico ao da ferramenta, janelas `17n+5`, ffprobe |

Assets: `assets/h3_character_swap.api.json` (grafo oficial), `assets/prompt_relay_estruturado_akatz.txt` (prompt estruturado do autor, para o fluxo h3-relay) e `assets/transcript_exemplo.json`.

## Limites honestos (diga ao usuário quando aplicável)

- **O LoRA v1.5 é experimental:** identidade, timing, expressões, oclusões e cortes podem desviar.
- **Lip sync bom, não perfeito.** No caso real ficou em 0,71–0,82, com trechos de 0,2 onde o original quase não abre a boca.
- **Licença:** MiniMax H3 Community License, com restrições territoriais (EUA, UE, Reino Unido e Coreia ficam fora da concessão padrão) e de uso comercial. Mencione se o uso parecer comercial.
- **Pessoas reais:** trocar a identidade de alguém em vídeo pode enganar. Se o personagem for uma pessoa real identificável, ou houver risco de deepfake enganoso, confirme o consentimento e o propósito antes.
