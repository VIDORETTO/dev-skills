# 15: Fronteira (estado da arte e próximas alavancas)

Pesquisa feita em 18/10/2026, cobrindo os últimos ~3 meses: HF, GitHub, r/StableDiffusion (via agregadores), blogs técnicos e documentação oficial. **Repita esta pesquisa a cada uso relevante**, porque o ecossistema H3 muda semanalmente.

## Veredito: estamos no limite?

| Eixo | Situação | Margem restante |
|---|---|---|
| **Fundo** | Perto do teto. A difusão mascarada preserva o latente da fonte (44 dB; ΔY do fundo ≈ −3, só do VAE) | Pequena: colar pixels originais fora da máscara com borda suave (ganho marginal, risco de halo) |
| **Cor e enquadramento** | Resolvidos (SDR, recorte idêntico, shots `preserve`) | — |
| **Identidade do personagem** | Boa, mas **não no limite** | Média a alta: LoRA alternativo focado em *likeness*, LoRA de identidade treinado, segundo passe |
| **Lip sync** | 0,71–0,82; trechos fracos em fala de "boca pequena" | Média: LoRA de guide alinhado, Head Swap combinado, base sem Turbo, mais seeds |

Consenso da comunidade: **nenhuma** ferramenta, aberta ou comercial, garante lip sync ou identidade. Os resultados são probabilísticos e dependem da seed. A deriva piora com clipes longos, rosto pequeno, oclusão, movimento rápido e proporções muito diferentes.

## Alavancas ainda não testadas (por ordem de custo/benefício)

### 1. Alissonerdx Character Swap **v1.1**, alternativa ao LoRA do akatz (lançado em 13/10/2026)

- **Repositório:** https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI (`loras/minimax_h3_character_swap_v1.1_ref2va_fro.safetensors`, 80 MB, strength 1.0).
- **Diferença técnica:** o vídeo-fonte entra como **guide latente alinhado** (`MiniMaxH3AddGuide`, `frame_idx=0`). Ele ocupa as mesmas posições espaço-temporais da saída, em vez de entrar como `<Video 1>` de referência. Em tese, prende melhor timing, enquadramento e boca.
- **Foco declarado da v1.1:** *likeness* (rosto, cabelo, corpo e roupa mais fiéis à referência).
- **Prompt:** template **fixo** de uma linha começando com `body_swap:`. Só se troca o `{details}` (lista de atributos da cabeça aos pés, começando pelo gênero, gerada por modelo de visão). O template completo está no `docs/character-swap.md` do repositório.
- **Turbo:** 8 steps com o turbo **DMD** `minimax_h3_dmd_ref2va_8step_turbo_pruned` (não o lightx2v).
- **Máscara:** não usa SAM; a máscara vem de BiRefNet-RMBG. **Não preserva o fundo pela máscara como a ferramenta do akatz**: testar o fundo com `qa_color.py`.
- **Licença própria:** uso comercial livre. Empresas com mais de US$ 1 M precisam dar crédito. Proibido oferecer como API ou SaaS.
- **Como testar:** A/B no 1º segmento contra a receita atual, com a mesma seed e o mesmo `qa_lipsync`. Uma combinação a explorar é a máscara SAM do akatz com o guide alinhado do Alissonerdx, mas isso exige grafo próprio.

### 2. Combinar com o **Head Swap** (Alissonerdx `head_swap:`) para o lip sync

O autor diz que as duas coisas juntas "might improve lip-sync in some cases" (não verificado). O Head Swap troca só a cabeça e preserva corpo e roupa da fonte. Sozinho, serve para casos em que só o rosto muda.

### 3. Segundo passe de nitidez e detalhe

- **LMS LoRA** (`minimax_h3_lms_v1.0_r64`): repassa o clipe gerado como guide alinhado com o prompt fixo "Enhance this video with sharp, crisp details while preserving a natural photorealistic appearance." Aumenta a nitidez sem mudar movimento nem sync.
- **Latent upscaler** `h3_upscaler_lms_v0.1` (experimental) ou **H3 Ultimate 2× Enhance** do h3-relay (tiles, 1664x960). Ambos levam a ~1280x704+.
- **Uso:** só depois que o take passou na QA. Custo de ~1 passada extra por segmento.

### 4. LoRA de identidade do personagem treinado (para personagem recorrente)

O ai-toolkit (ostris) treina LoRA para H3 ref2va (rank ~16, validação com guidance 1, porque o modelo é destilado sem CFG). Com 10+ clipes ou imagens consistentes do personagem, a identidade fica muito mais estável. Custa algumas horas de GPU (~US$ 3–8). **Empilhar** com o LoRA de swap não foi verificado: testar com strength 0,5–0,8. Vale a pena só se o mesmo personagem for usado em muitos vídeos.

### 5. Base sem Turbo nos closes críticos

20 steps, `res_multistep`/`simple` (`settings.turbo=false`). A comunidade relata lip sync melhor; o custo por segmento é ~2,5×. Ainda não medido aqui.

### 6. Estrutura em resolução menor

Um relato (virse.ai, ago/2026) diz que 352–416p mantiveram enquadramento e posição **melhor** que 768p no Ref2VA. Isso sugere uma rota estrutura → upscale: gerar em 480p e passar o LMS/upscaler. Não testado.

## Backlog de experimentos (pendentes; o usuário optou por não rodar em 18/10/2026)

Ao retomar, comece pelo item 1. São todos testes A/B **no 1º segmento** (~5 s), com a mesma seed, medidos por `qa_lipsync.py`, `qa_color.py` e `qa_mask.py` contra a receita atual (referência: A1 com correlação 0,75 e fundo ΔY ≈ −3).

1. **Alissonerdx Character Swap v1.1** (guide alinhado + turbo DMD + template `body_swap:`): ~US$ 0,50.
2. **Item 1 + Head Swap** combinados, para o lip sync: ~US$ 0,50.
3. **Segundo passe LMS** sobre o melhor take: ~US$ 0,30.
4. **Base sem Turbo** (20 steps) num close: ~US$ 0,50.
5. **480p mais upscale** (estrutura contra detalhe): ~US$ 0,40.

Registre os resultados em `10-falhas.md` (se piorar) ou promova para a receita principal no `SKILL.md` (se melhorar).

## Novidades oficiais de 17/10/2026

- **h3-character-swap-tool 0.2.0 / "Relay 2.0":** o `main` migrou para os nós nativos do h3-relay 2.0 (IDs descritivos, `H3RelayLoadHistory`/`SaveHistory`, histórico em FFV1 16 bits) e **removeu `worker_nodes/h3_character_swap`**. Segundo a validação oficial, a qualidade é praticamente a mesma (diferença média de 1,48/255; não é idêntica). **A skill fixa o commit `0670e4fdf95a`**, a versão validada. Migrar só se houver motivo, revalidando grafo e IDs.
- **Person Remover LoRA V1** (akatz): remove a pessoa e reconstrói o fundo, com SAM, uma 1ª frame limpa, janelas de 22 e 12 steps. **Caso de uso na skill:** quando o personagem novo é **menor ou mais estreito** que a pessoa original, sobra silhueta original visível ao redor. A solução é remover a pessoa primeiro (backplate limpo) e depois inserir o personagem.

## Concorrentes (para contexto e recomendação honesta)

| Ferramenta | Pontos | Limites |
|---|---|---|
| **Runway Aleph 2.0** (comercial) | Substituição de personagem em até 30 s, multi-shot | **Não faz lip sync** (a própria Runway manda refazer com Act-Two); pago |
| **Kling O1 Video Edit** (comercial) | Edição de footage em 1080p, 3–10 s | Sem teste independente de lip sync ou fundo |
| **Wan 2.2/2.6 Animate** (aberto) | Replace com relighting LoRA; relatos de rosto mais natural em close e fala | Pose e esqueleto; o rosto degrada em baixa resolução |
| **SCAIL-2** (aberto, Apache 2.0, Wan2.1) | Sem esqueleto, multi-personagem, uso comercial | Microexpressões menos detalhadas; segmentos manuais de 81 frames |
| **Higgsfield Recast** (comercial) | Swap + dublagem + lip sync automático | Só relatos de blog |

Para trocar o personagem **mantendo fundo e fala do próprio vídeo**, nada encontrado supera de forma comprovada o pipeline H3 com máscara desta skill. As alternativas abertas mais promissoras para A/B são o **Wan Animate** e o **SCAIL-2** (licença comercial mais simples).

## Fontes (acessadas em 18/10/2026)

- Alissonerdx, pacote H3: https://huggingface.co/Alissonerdx/Minimax-H3-ComfyUI (docs `character-swap.md`, `head-swap.md`, `lms.md`, `latent-upscaler.md`)
- Notícia de lançamento e thread do Reddit: https://comfyui-wiki.com/en/news/2026-10-13-h3-character-swap-live-wallpaper · https://www.reddit.com/r/StableDiffusion/comments/1x4jh3c/
- akatz Person Remover: https://huggingface.co/akatz-ai/MiniMax-H3-Person-Remover-LoRA
- Ferramenta 0.2.0 e validação: https://github.com/akatz-labs/h3-character-swap-tool (`release/toolkit-v2-validation.md`)
- Workflow Relay V2 no LoRA: https://huggingface.co/akatz-ai/MiniMax-H3-Character-Swap-LoRA (`examples/H3-Character-Swap-Relay-V2.json`)
- Ref2V, swap, limites e dicas (ago/2026): https://www.virse.ai/blog/minimax-h3-motion-transfer
- Treino de LoRA H3 (ai-toolkit): https://www.runcomfy.com/trainer/ai-toolkit/minimax-h3-lora-training · https://www.youtube.com/watch?v=x-gORSUOybk
- SCAIL-2: https://docs.comfy.org/tutorials/video/zai/scail2 · https://huggingface.co/zai-org/SCAIL-2 · comparação com Wan Animate: https://docs.dreamerland.ai/video/wan2.2-video/character-animation/wan-animate-vs-scail2
- Runway (Aleph não faz lip sync): https://help.runwayml.com/hc/en-us/articles/41748090660499-Creating-Multi-Character-Dialogues-with-Act-Two
- Kling O1 Video Edit: https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-kling
