# 19: LoRA alternativo Alissonerdx Character Swap v1.1

> **Status:** alternativa documentada, **ainda não integrada aos scripts** e sem nenhum teste nesta skill. Pesquisa de 21/10/2026: as fontes primárias (model card e `docs/` no Hugging Face, matérias da comfyui-wiki e da ArtRealm) foram lidas por resumo de busca, porque o ambiente da pesquisa não alcançava esses sites. Pontos que não puderam ser confirmados estão marcados como tal. Revalide no model card antes de montar o grafo.

## Links

| O quê | Link |
|---|---|
| Repositório (model card, LoRAs, docs, workflows) | https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI |
| Arquivo do LoRA v1.1 | https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI/blob/main/loras/minimax_h3_character_swap_v1.1_ref2va_fro.safetensors |
| Guia oficial (prompt `body_swap:`, nós, settings) | https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI/blob/main/docs/character-swap.md |
| Workflow de character swap | https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI/blob/main/workflows/minimax_h3_character_swap_workflow.json |
| Workflow de head swap | https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI/blob/main/workflows/minimax_h3_head_swap_workflow.json |
| Lançamento do v1.1 (comfyui-wiki, 18/10/2026) | https://comfyui-wiki.com/en/news/2026-10-18-h3-character-swap-v1-1 |
| Matéria técnica do v1.1 (ArtRealm) | https://artrealmai.com/article/minimax-h3-character-swap-lora-v1-1-comfyui |
| Lançamento do v1.0 (comfyui-wiki, 13/10/2026) | https://comfyui-wiki.com/en/news/2026-10-13-h3-character-swap-live-wallpaper |
| Post do autor sobre o v1.0 (X) | https://x.com/Alissonerdx/status/2109749038773833731 |

## Linha do tempo

- **13/10/2026, v1.0:** anunciado no r/StableDiffusion junto com um LoRA de "live wallpaper". Arquivo de 620 MB, rank fixo 64. Reclamação principal da comunidade: o personagem trocado **não ficava parecido o bastante** com a referência.
- **18/10/2026, v1.1:** responde a essa reclamação. Arquivo de 80 MB, **extração SVD** da rodada de treino v1.1 com rank dinâmico por camada (de 4 a 34, mediana 7), escolhido por análise de energia. Passa a ser o checkpoint recomendado no model card; o v1.0 fica no repositório para comparação.

## Como funciona (e o que muda em relação ao akatz)

| | akatz v1.5 (padrão da skill) | Alissonerdx v1.1 |
|---|---|---|
| Vídeo-fonte | Referência (`<Video 1>`) + latente preservado fora da máscara | **Guia latente alinhado** (`MiniMaxH3AddGuide`, `frame_idx=0`): ocupa as mesmas posições espaço-temporais da saída |
| Foco declarado | Cena, fala, cortes ("better handling of cuts" na v1.5) | **Semelhança**: rosto, cabelo, corpo e roupa mais próximos da referência e menos deriva ao longo dos frames |
| Prompt | Livre: descrição, `<d>[Língua] …</d>`, `behavior` com tempos | **Fixo**, uma linha com o gatilho `body_swap:`; só muda a lista de atributos (`{details}`, da cabeça aos pés, começando pelo gênero) |
| Strength | 1.0 | 1.0 |
| Turbo / steps | lightx2v 8-step, `er_sde`/`normal`, CFG 1 | **DMD** 8-step (`minimax_h3_dmd_ref2va_8step_turbo_pruned`); não misturar com as settings do akatz |
| Máscara / fundo | SAM 3.1 + expansão; fundo preservado pelo latente | BiRefNet-RMBG; não preserva o fundo do mesmo jeito (anotado na pesquisa de 18/10, não reconfirmado agora) |
| Áudio / lip sync | Áudio de voz isolada no condicionamento + diálogo no prompt | Áudio entra se `with_audio = true` no nó **BFS Shot H3 Conditioning**; a boca segue o movimento do vídeo-guia |
| Segundo passe | (Relay 2.0 tem Ultimate/LTX 2×) | Opcional no workflow: LMS LoRA + upscaler latente do H3 para 1280×704 |
| Workflows | Ferramenta oficial (`akatz-labs/h3-character-swap-tool`) | "Shot Planner" (exige **ComfyUI-BFSNodes ≥ 1.113.0**) ou versão só com nós nativos do ComfyUI |
| Pessoas por cena | Uma (SAM escolhe `largest`/`leftmost`/…) | Uma (troca de vários personagens só prevista para uma futura v2.0) |
| Licença do LoRA | Licença do MiniMax H3 | Própria: uso comercial livre; crédito para empresas acima de US$ 1 M; **proibido oferecer como API/SaaS**. A licença do H3 base continua valendo |

## O que dizem os relatos

**Do autor:**
- Sobre o v1.0: "far from perfect, it's just a LoRA, but it can work surprisingly well in some cases". Ele disse que pretende fazer uma versão melhor **junto com o akatz**: vale acompanhar, porque as duas linhas podem convergir.
- O guia chama o LoRA de experimental e "not a guaranteed identity-transfer system"; o repositório descreve os modelos como de pesquisa, não ferramentas prontas.
- **Onde a semelhança afrouxa:** rostos pequenos, oclusão, movimento rápido, ângulos difíceis, mudanças de luz e clipes longos.
- **Dica para lip sync:** o Head Swap LoRA do mesmo repositório (v1.0, rank 32, experimental) usa o mesmo condicionamento por guia, e combinar os dois "may help lip-sync" em alguns clipes. Não verificado por terceiros.
- **Controle de semelhança:** um resumo de busca cita uma opção `source_blur` no nó BFS Shot H3 Conditioning como ajuste de likeness. **Não confirmado** na documentação encontrada; conferir no `docs/character-swap.md`.

**Da imprensa e da comunidade:**
- A cobertura (comfyui-wiki, ArtRealm) confirma o ganho de semelhança em relação ao v1.0 pelas palavras do autor; ninguém publicou medição independente.
- **Nenhuma comparação direta com o akatz v1.5** foi encontrada (nem de lip sync, nem de fundo, nem de identidade). É por isso que a decisão aqui é por A/B com a QA da skill.
- Nenhum relato de usuário específico sobre o v1.1 apareceu nas buscas (Reddit, Hugging Face); o pacote tinha ~117 mil downloads e ~400 curtidas numa das matérias.
- Relato geral sobre swap no H3 (não específico deste LoRA): funciona melhor em planos médios e "struggles greatly with close ups". O caso Sherlock desta skill é close de selfie e passou com o akatz, com limites admitidos.

## Quando compensa trocar

**Compensa testar quando:**
1. O problema é **semelhança**, não boca nem fundo: depois de 3+ seeds e dos ajustes (`behavior`, máscara, `--no-turbo`, referência extra), o `qa_identity.py` mostra `id_ref` baixo, quedas ao longo do segmento ou margem pequena contra a pessoa original, ou o figurino/cabelo sai diferente da referência.
2. O corpo e a roupa aparecem bastante (plano médio ou aberto), já que o v1.1 foi ajustado para rosto, cabelo, corpo e roupa juntos.
3. Há **uma pessoa** na cena e o shot não tem cortes dentro do segmento.
4. O fundo fiel não depende do LoRA: o `composite.py` devolve o fundo original em resolução cheia, então a fraqueza do v1.1 nesse ponto pesa pouco no final.

**Provavelmente não compensa quando:**
1. O problema é **lip sync**: a receita do akatz tem diálogo no prompt, `behavior` com tempos e números reais (0,71–0,82); o v1.1 tem prompt fixo, sem diálogo. Se for testar mesmo assim, teste junto o Head Swap.
2. Há **várias pessoas** e é preciso escolher qual trocar (o SAM com `sam_text`/`selection` faz isso na receita atual).
3. O shot tem **cortes de câmera** dentro do segmento (a v1.5 do akatz declara melhor tratamento de cortes).
4. O uso final é **oferecer a troca como API ou SaaS** (a licença do v1.1 proíbe).
5. Rostos muito pequenos, oclusão forte ou movimento rápido: o próprio autor diz que a semelhança afrouxa nesses casos.

## Como testar

1. Montar o grafo **a partir do `docs/character-swap.md` e do workflow oficial** (de preferência a versão só com nós nativos, para não depender do ComfyUI-BFSNodes), nunca de memória.
2. Baixar no pod: o LoRA v1.1, o turbo DMD e (para o segundo passe) o LMS e o upscaler latente.
3. Mesmo segmento, mesmo clipe com voz isolada, `with_audio = true`, 2–3 seeds dos dois lados.
4. Medir os dois com `qa_take.py` (lip sync MAR e SyncNet, identidade, máscara) e o `composite.py` para comparar o final.
5. Adotar só se ganhar em identidade **sem** perder lip sync. Não empilhar com o v1.5.
6. Registrar o resultado aqui, em `10-falhas.md` (se perder) ou no `SKILL.md` (se ganhar).

Custo estimado do A/B: ~US$ 0,50 (um segmento, poucas seeds) mais o tempo de montar o grafo.
