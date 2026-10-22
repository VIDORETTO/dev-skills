---
name: h3-character-swap
description: Troca de personagem em vídeo (character swap / character replacement / substituir pessoa no vídeo) com MiniMax H3 + LoRA akatz-ai Character Swap v1.5 no ComfyUI, rodando em GPU alugada no RunPod. Cobre a análise prévia local (HDR→SDR, transcrição Whisper, voz isolada Demucs, detecção de presença/shots, segmentação nas pausas), o deploy do pod já pronto, a geração por segmentos com máscara SAM 3.1 e histórico, best-of-N por seeds com QA objetiva (lip sync MAR e SyncNet, identidade ArcFace, máscara, cor), reparo de boca opcional (LatentSync), a montagem com o áudio original e o final em resolução cheia sobre o vídeo original. Use SEMPRE que o usuário quiser trocar/substituir uma pessoa de um vídeo por um personagem de imagem de referência, falar de MiniMax H3, ref2va, akatz, h3-relay, h3-character-swap-tool, lip sync de swap, ou rodar ComfyUI de vídeo no RunPod — mesmo que não diga "skill" nem "LoRA".
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
8. **Âncora de 1º frame é opcional; decida por A/B.** Só vale âncora gerada por um editor de verdade (Qwen no pod ou Nano Banana/GPT Image pelo usuário); **nunca fabrique âncora por código** (colar rosto, montagem), nem para testar a QA: o usuário pediu frames e referências reais e boas. Em close de selfie, a âncora do Qwen derrubou o lip sync de 0,67 para 0,28. Com a pessoa parcial na borda, ela inventou uma segunda pessoa. Se for usar, escolha a variação com `qa_anchor.py`, que reprova esses defeitos e cola o personagem de volta no frame original.
9. **Seeds variam muito** (0,58 contra 0,75 com o mesmo prompt). Teste 2–3 seeds no 1º segmento de cada shot e escolha pela QA.
10. **Medir antes de entregar:** `qa_take.py` (lip sync MAR + SyncNet, identidade ArcFace, máscara) por take e `qa_color.py` no final. Grades de frames esconderam o lip sync ruim, e a medição o revelou. A identidade se mede contra a referência **e** contra a pessoa original: margem pequena = vazamento.
11. **Ler a saída só do nó 807 (pelo ID).** O history do ComfyUI também lista o vídeo de entrada, e isso já produziu um falso "não trocou".
12. **Ferramenta fixada no commit validado** (`0670e4fdf95a`). Em 17/10/2026 o `main` virou "Relay 2.0" e removeu os nós que a skill usa; o `make_pod.py` já faz o checkout certo. Antes de um trabalho grande, pesquise novidades (HF akatz-ai / Alissonerdx, GitHub, r/StableDiffusion), porque o ecossistema muda toda semana.
13. **Histórico amarrado ao take.** Cada continuação registra de qual take do segmento anterior saiu (`history_from`, e o nome ganha `_hXXXX`). Trocar o take de um segmento desmarca os seguintes que vieram de outro histórico; `chain` regera só esses, e `assemble`/`composite` recusam montar emenda errada.
14. **Entregar em resolução cheia:** depois de aprovar os takes, `composite.py` cola o personagem sobre o vídeo original (fundo idêntico à fonte, quadro inteiro nos shots `preserve`). O `assemble.py` continua sendo o final de QA no canvas.
15. **Dinheiro:** estimar o custo e pedir o OK **antes** de criar o pod; desligar o pod ao terminar e confirmar com `list-pods` e `list-network-volumes` vazios. Não deixe nenhuma cobrança parada (sem volume persistente por padrão).

## Fluxo

`S` = `scripts/` desta skill. `VPY` = python do venv local, que tem rembg, mediapipe, demucs, faster-whisper, insightface e (para SyncNet/guia) torch (setup em [references/08-ambiente-local.md](references/08-ambiente-local.md); reutilize `%LOCALAPPDATA%\Temp\cswap-venv` se já existir). Os demais scripts usam só stdlib.

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
- **Âncora de 1º frame: pergunte ao usuário quem faz, ANTES do pod** ([05-ancora.md](references/05-ancora.md#quem-faz-a-âncora)). Diga em quais shots você recomenda âncora e em quais não (pessoa entrando pela borda, close de selfie que já funciona sem). Ofereça as três opções:
  1. **O usuário faz** no Nano Banana (Gemini) ou no GPT Image (ChatGPT). Sem custo de GPU; os frames vão para o Google/OpenAI.
     - **Descreva cada frame antes:** abra `frames/<id>_0.png` e grave em `anchor_notes` (no shot ou no segmento do `job.json`), em inglês, onde a pessoa está, pose, mãos, pernas, cabeça, olhar, expressão, estado da boca, objetos da cena e luz ([13-exemplos.md](references/13-exemplos.md#anchor_notes)). O prompt específico do frame foi o que funcionou nos testes reais; sem ele o `anchor_kit` avisa.
     - **Entregue tudo pronto na conversa:** rode `python S/anchor_kit.py JOB/job.json <shots>` e, na mesma resposta, **envie como arquivo** cada frame a editar (`anchor_kit/<id>_frame.png`) e a imagem do personagem (pelo mecanismo de envio de arquivos do host; sem ele, dê os caminhos absolutos) e **cole o prompt completo** de cada shot num bloco de código. O texto está no `anchor_kit/ENTREGA.md` (o script também imprime). Resuma o `COMO_FAZER.md` em 3–4 linhas: ordem dos anexos, 2–4 variações, PNG sem recortar.
     - **Espere as imagens editadas** (anexadas no chat ou em `JOB/anchors_user/`; salve as anexadas lá como `<id>_v1.png`, `<id>_v2.png`…).
     - **Confira a qualidade antes de aceitar:** `VPY S/qa_anchor.py JOB/job.json <id>` e **abra a folha `review_<id>.jpg`** e confira a checklist visual do [05-ancora.md](references/05-ancora.md#revisão-da-âncora-devolvida). Os números não veem costura, mãos, cabelo da pessoa original sobrando nem luz errada.
     - **Responda ao usuário com o veredito de cada variação:** aprovada (rode `--set` e mostre a `_paste.png` escolhida) ou refazer, com o motivo e a frase pronta para ele colar no mesmo chat do editor (o `qa_anchor` imprime as frases dos problemas medidos; para os visuais, use as do 05-ancora). Só siga para o pod com uma âncora aprovada ou com a decisão de seguir sem âncora.
  2. **A IA faz com o Qwen** no pod: o pod sai com `make_pod.py --qwen` (mais ~31 GB de download e disco de 180 GB) e as variações são geradas na Fase B (~85 s cada).
  3. **Sem âncora:** o padrão validado (caso Sherlock).
- **Relatório prévio:** apresente ao usuário o plano, os riscos e a estimativa de custo (modelo em [00-analise-previa.md](references/00-analise-previa.md)) e **espere o OK**.

### Fase B: GPU (RunPod)

1. **Criar o pod:** `python S/make_pod.py [--qwen]` gera o JSON (`--qwen` só se o usuário escolheu a âncora feita pela IA). Passe-o para a ferramenta MCP `create-pod` (leia antes o guia `runpod-mcp` via `read-guide`, se ainda não leu). Informe o preço/h devolvido; a RTX PRO 6000 custa US$ 2,49/h. Detalhes e armadilhas em [references/07-runpod.md](references/07-runpod.md).
2. **Esperar o pod:** polling de `https://<pod>-8188.proxy.runpod.net/system_stats` (com user-agent de curl), depois `python S/run_job.py JOB/job.json check <pod>`.
3. **Âncora pela IA (se escolhida):** `run_job.py anchor <pod> <shot> 11,22,33`, depois `VPY S/qa_anchor.py JOB/job.json <shot> --set` e a mesma revisão visual da folha `review_<shot>.jpg`. Âncora do usuário já chega aprovada da Fase A.
4. **Primeiro segmento de cada shot, best-of-N:** `python S/run_job.py JOB/job.json best <pod> A1 11,22,33`. Gera um take por seed, roda `qa_take.py` (no venv: `H3_VPY`) e seleciona a maior nota. Shots independentes podem ir para a fila junto.
5. **Conferir o vencedor** com som e com os números ([references/09-qa.md](references/09-qa.md)); trocar com `select <seg> <take>` se discordar.
6. **Encadear o resto:** `python S/run_job.py JOB/job.json chain <pod> <shot> [--seeds 11,22]` (com `--seeds`, best-of-N em cada segmento). Segmento reprovado: `best`/`seg … --seed` e `select`; o `chain` seguinte regera só o que dependia dele.
7. **Janela de boca ruim que nenhuma seed resolve** (pod com `--latentsync`): `run_job.py lipfix <pod> <seg> <t0> <t1>` gera um take `_lf` com só aquele trecho refeito pelo LatentSync 1.6; QA e `select` se melhorar ([09-qa.md](references/09-qa.md)).
8. **Montar para QA:** `python S/assemble.py JOB/job.json JOB/final.mp4`. Saem também o `final_ref.mp4` e o QA completo contra ele.
9. **Desligar:** `delete-pod`, depois `list-pods` e `list-network-volumes`. Avise que está zerado.
10. **Final em resolução cheia (CPU):** `VPY S/composite.py JOB/job.json JOB/final_full.mp4 [--debug-mask]` ([17-composite.md](references/17-composite.md)).

### Fase C: entrega

Envie o `final_full.mp4` (e o `final.mp4` de canvas, se útil) e reporte **com números**: lip sync por shot e janelas fracas (MAR e SyncNet), identidade (ArcFace contra referência e contra a fonte), máscara, cor do fundo, frames iguais à fonte, custo e estado do RunPod. Seja honesto sobre o que ficou abaixo do ideal e por quê (modelo em [13-exemplos.md](references/13-exemplos.md)). Registre lições novas em `references/10-falhas.md`.

## Decisões rápidas

| Situação | Decisão |
|---|---|
| Close de selfie, fala | Sem âncora; `behavior` detalhado; 2–3 seeds no 1º segmento |
| Plano médio ou aberto, personagem bem diferente | Testar âncora: perguntar ao usuário se ele faz (Nano Banana/GPT Image, `anchor_kit.py`) ou se a IA faz (Qwen, `make_pod --qwen` + `run_job anchor`); escolher com `qa_anchor.py --set`; usar só se a QA do vídeo melhorar |
| Pessoa entra ou sai pela borda no 1º frame do shot | Nunca usar âncora nesse shot |
| Chapéu, cabelo armado, capa | `expansion_px` de 144–160; conferir com `qa_mask.py` |
| Várias pessoas na cena | `sam_text` específico ("bald man in dark t-shirt"), `selection` (`largest`, `leftmost`, `rightmost`, `index`) |
| Corte de câmera | Um shot por corte (o prepare detecta) |
| Close com boca "pequena" que sai exagerada | Mais seeds e "small, barely opened lip movements" no `behavior`. É limite conhecido do LoRA: avise o usuário |
| Vazamento do original (mãos, dentes, acessórios) | Trocar a seed (dica do fórum); "From the very first frame…" já está no prompt |
| Iteração barata | `--res 480` no prepare (≈ metade do custo); final em 768 |
| O usuário quer mais fidelidade do que a receita atual dá | Ler [15-fronteira.md](references/15-fronteira.md) e propor um A/B barato (1º segmento): LoRA Alissonerdx v1.1 de guide alinhado, segundo passe LMS, base sem Turbo |
| O personagem novo é menor ou mais estreito que a pessoa original | A silhueta original pode sobrar: usar antes o Person Remover LoRA (backplate) e depois inserir o personagem ([15-fronteira.md](references/15-fronteira.md)) |
| Lip sync ainda ruim num close difícil | `best ... --no-turbo` (base, 20 steps `res_multistep`): a comunidade relata sincronia melhor. Ainda não validado aqui |
| Uma janela de 1–2 s reprovada e o resto bom | `lipfix` só nesse trecho (pod `--latentsync`); comparar pela QA. Experimental |
| Rosto original vazando (margem de identidade baixa) ou boca pequena da fonte imitada | A/B com guia de profundidade/face mesh: `make_guide.py --mode depth_mesh` e `best ... --guide depth_mesh` ([16-guia-profundidade.md](references/16-guia-profundidade.md)). Experimental |
| Identidade fraca em giros/close | `character.extra_image` = close nítido do rosto (vira `<Picture 2>`/`<Picture 3>`); comparar pela QA |
| Identidade derivando no meio de um shot longo | Âncora no meio do shot: `run_job anchor <pod> A3 11,22,33` e `seg … A3 --anchor out/anchor_A3_s22.png` (ou `seg.anchor` no job) ([05-ancora.md](references/05-ancora.md)) |
| Personagem cartoon/3D (ArcFace não acha rosto) | `settings.identity_backend = "dino"` |
| Mesmo com 3+ seeds e os ajustes acima, identidade fraca ou personagem pouco parecido com a referência | Propor ao usuário um A/B com o **LoRA alternativo Alissonerdx v1.1** (guide alinhado, foco em semelhança). Não é troca de arquivo: outro grafo e outro prompt, ainda não integrados aos scripts ([19-lora-alissonerdx.md](references/19-lora-alissonerdx.md): links, relatos e quando compensa) |

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
| [15-fronteira.md](references/15-fronteira.md) | **Estado da arte e alavancas** (o que já virou ferramenta aqui e o que falta testar: Alissonerdx v1.1 de guide alinhado, Head Swap, segundo passe LMS/upscale, LoRA de identidade, Person Remover), concorrentes. Leia quando o usuário quiser mais qualidade do que a receita atual entrega |
| [16-guia-profundidade.md](references/16-guia-profundidade.md) | Técnica do Genjutsu (profundidade + face mesh no lugar da pessoa) adaptada ao H3: quando testar, riscos, comandos |
| [17-composite.md](references/17-composite.md) | Final em resolução cheia sobre o vídeo original: máscara, parâmetros, upscale, limites |
| [18-migracao-relay2.md](references/18-migracao-relay2.md) | Plano para migrar do commit fixado para a ferramenta 0.2.0 / Relay 2.0 (mapa de nós, o que muda no `run_job.py`, gates) |
| [19-lora-alissonerdx.md](references/19-lora-alissonerdx.md) | LoRA alternativo Alissonerdx v1.1: links, diferenças, relatos, quando compensa trocar e como testar |

## Scripts

| Script | Python | Função |
|---|---|---|
| `prepare.py` | venv | Análise prévia completa: SDR, Demucs, Whisper, eventos não verbais, presença com histerese e filtro de pico, cortes, shots, segmentos, clipes, frames, `job.json`, `analysis.md` |
| `make_pod.py` | qualquer | JSON do `create-pod` com o boot à prova das armadilhas conhecidas (`--qwen` âncoras, `--latentsync` reparo de boca); download que falha para o boot |
| `run_job.py` | qualquer | `check`, `prompt`, `anchor`, `seg`, `best`, `select`, `chain`, `lipfix` contra o ComfyUI do pod (ou qualquer ComfyUI por URL) |
| `assemble.py` | qualquer | Final no canvas = takes escolhidos + trechos `preserve` + áudio original; gera `_ref.mp4` para QA; recusa emenda com histórico errado |
| `composite.py` | venv | **Final em resolução cheia**: personagem colado sobre o vídeo original com máscara suave e estável no tempo |
| `make_guide.py` | venv | Clipes-guia (profundidade colorida e/ou face mesh no lugar da pessoa) para o A/B do `--guide` |
| `qa_take.py` | venv | QA completa de um take com nota única (usada pelo `best`) |
| `anchor_kit.py` | qualquer | Pacote para o usuário fazer a âncora no Nano Banana / GPT Image: frame, personagem, prompt pronto e passo a passo |
| `qa_anchor.py` | venv | Alinha ao frame original as âncoras do Qwen ou do usuário (outro tamanho/proporção), mede as variações de âncora (composição, escala do rosto, boca, identidade, pessoa extra), cola o personagem de volta no frame original e escolhe a melhor |
| `qa_lipsync.py` | venv | Correlação da boca com a FONTE por segundo, atraso e amplitude |
| `qa_syncnet.py` | venv + torch | Sincronia da boca com o ÁUDIO (SyncNet: LSE-C/LSE-D, offset, janelas) |
| `qa_identity.py` | venv | Identidade ArcFace contra a referência e contra a pessoa original (vazamento); `dino` para personagem estilizado |
| `qa_mask.py` | venv | % do personagem fora da máscara (recorte de chapéu ou cabelo) |
| `qa_color.py` | venv | Cor e brilho **do fundo** contra a fonte |
| `h3common.py` | — | Canvas idêntico ao da ferramenta, janelas `17n+5`, mapeamento canvas→fonte, histórico dos takes, ffprobe |

Assets: `assets/h3_character_swap.api.json` (grafo oficial), `assets/prompt_relay_estruturado_akatz.txt` (prompt estruturado do autor, para o fluxo h3-relay) e `assets/transcript_exemplo.json`.

## Limites honestos (diga ao usuário quando aplicável)

- **O LoRA v1.5 é experimental:** identidade, timing, expressões, oclusões e cortes podem desviar.
- **Lip sync bom, não perfeito.** No caso real ficou em 0,71–0,82, com trechos de 0,2 onde o original quase não abre a boca.
- **Recursos marcados como experimentais** (guia de profundidade, `lipfix`, referência extra, âncora no meio do shot, SyncNet na nota) foram testados quanto ao fluxo e ao grafo, mas ainda **não numa geração real em GPU**. Trate o primeiro uso como A/B e registre o resultado em `10-falhas.md` ou `15-fronteira.md`.
- **Licença:** MiniMax H3 Community License, com restrições territoriais (EUA, UE, Reino Unido e Coreia ficam fora da concessão padrão) e de uso comercial. Mencione se o uso parecer comercial.
- **Pessoas reais:** trocar a identidade de alguém em vídeo pode enganar. Se o personagem for uma pessoa real identificável, ou houver risco de deepfake enganoso, confirme o consentimento e o propósito antes.
