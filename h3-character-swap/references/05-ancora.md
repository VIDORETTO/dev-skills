# 05: Âncora do primeiro frame

> **Atualização de 21/10: escolha as variações com `qa_anchor.py`** (abaixo). Ele reprova exatamente os defeitos que derrubaram a âncora no caso Sherlock (recomposição, escala do rosto, boca diferente, pessoa inventada) e cola o personagem de volta no frame original.
>
> **Atualização da rodada 4: a âncora é OPCIONAL, decidir por teste A/B com a QA.** Neste vídeo (selfie em close-up), a âncora gerada pelo Qwen **piorou** o lip sync (correlação de 0,67 para 0,28). O que resolveu o início foi **descrever o sopro e a respiração no prompt** e testar **várias seeds** (a melhor chegou a 0,75). Os argumentos abaixo continuam valendo para planos médios e abertos, mas não são regra.

## Por que ela é necessária

- **O problema:** sem âncora, a primeira janela de cada shot não tem guia visual no frame 0 (o código descarta a referência `ref_image_1` e o nó de histórico). O modelo precisa "inventar" a transição do careca para o personagem e ainda acertar a boca ao mesmo tempo.
- **Caso real (rodada 3):** a correlação de lip sync nos frames 0–95 do shot A foi de −0,02 / 0,04 / 0,38. Depois da janela 1 ela subiu para 0,7–0,9. O defeito ficou **concentrado no início**.
- **O que o autor diz:** a validação da ferramenta registra que a âncora melhorou a abertura, mas não garante identidade sustentada.
- **O que o app faz:** usa âncora **ligada por padrão** no primeiro segmento (`anchor_mode='shot'`, `use_anchor=True`).

## Como gerar

Faça uma edição de imagem do **frame 0 do shot** usando a referência do personagem. Brief usado pelo app oficial (`h3workbench/anchors.py`):

> Image 1 is the source frame to edit. Image 2 is character identity only: {descrição}. Replace ONLY the selected person with that single character. Match the exact source pose, face angle, gaze, mouth opening, expression, limb placement, scale and occlusions. Preserve all other people, the entire original scene, camera framing, lighting and aspect ratio. Keep the reference identity and costume; do not copy the reference pose or background. One full-aspect edited source frame.

Opções de editor de imagem:
- **O que o app usa:** a ferramenta de imagem do Codex.
- **No ComfyUI do próprio pod:** Qwen-Image-Edit (2509/2511) ou FLUX.1 Kontext, com o frame mais a referência.
- **Serviço externo:** só com a aprovação do usuário.

Regras da âncora:
- **Mesmo tamanho e recorte** do vídeo preparado. O nó redimensiona com `lanczos`.
- **Boca:** a mesma abertura do frame 0 da fonte. A comunidade recomenda que o primeiro frame "já pareça fala".
- **Iluminação:** a da cena (dia nublado, por exemplo), não a de estúdio da referência.
- **Revisão:** se a âncora não parecer um frame real do vídeo, refazer antes de gastar GPU no vídeo. O `qa_anchor.py` faz essa revisão com números.

## Resultados reais com Qwen-Image-Edit 2511 (rodada 4)

- **Grafo:** o do template oficial `image_qwen_image_edit_2511.json`:
  - UNET `qwen_image_edit_2511_fp8mixed` → `ModelSamplingAuraFlow` 3.1 → `CFGNorm` 1;
  - `TextEncodeQwenImageEditPlus`, com image1 = frame e image2 = personagem;
  - `FluxKontextMultiReferenceLatentMethod` = `index_timestep_zero`;
  - KSampler com 40 steps, CFG 3, euler / simple;
  - ~85 s por imagem.
- **Brief do app sozinho:** o Qwen **recompõe a cena**. Afasta a câmera, mostra mais corpo e fecha a boca.
- **Brief rígido de composição:** "keep the exact composition… face fills most of the frame width… do not zoom out… do not add any other person". Com ele, 1 de 3 seeds acertou (a s11), e as outras mudaram o fundo. **Gerar 3 ou mais variações e escolher.**
- **Pessoa parcial na borda** (shot começando com a pessoa entrando em quadro, como o frame 442): o Qwen centralizou o personagem inteiro e **inventou uma segunda pessoa**. **Não usar âncora nesse caso.** O shot C sem âncora teve lip sync de 0,82.

## Na API

- **Nó 309:** `H3CharacterSwapOptionalAnchor`, com `image` igual ao arquivo enviado. Quando a imagem existe, `use_anchor` liga sozinho.
- **Prompt:** incluir "<Picture 2> is the exact first-frame scene and pose anchor."
- **Segmentos de continuação:** o 1º slot é sempre o histórico gerado: "<Picture 2> is the generated boundary from the preceding segment." Uma âncora nova entra no 3º slot (abaixo).

## Âncora no meio do shot (continuações) — experimental

A ferramenta fixada aceita uma imagem extra nas continuações (`803.segment_reference` → `ref_image_2` → `<Picture 3>`); o app oficial usa isso com o texto "<Picture 3> is an additional scene and performance reference for this segment; preserve continuity with the generated boundary." Serve para **segurar a identidade num shot longo** quando ela deriva nos segmentos finais.

```bash
python S/run_job.py JOB/job.json anchor <pod> A3 11,22,33          # 1º frame do SEGMENTO A3 editado pelo Qwen
python S/run_job.py JOB/job.json seg <pod> A3 --anchor out/anchor_A3_s22.png
```

Ou grave `"anchor": "out/anchor_A3_s22.png"` no segmento A3 do `job.json` para o `chain` usar sozinho. O `prepare.py` já extrai `frames/<seg>_0.png` de cada segmento (jobs antigos: o `run_job` extrai na hora).

- **Mesmas regras da âncora de 1º frame:** mesma boca, mesma luz, sem pessoa parcial na borda. Gere 3 variações e escolha.
- **O slot é um só:** se o segmento tem âncora no meio, a `character.extra_image` não entra nele.
- **Decida por A/B com a QA** (identidade ArcFace e lip sync): no caso Sherlock, a âncora de 1º frame **piorou** o lip sync em close.

<a id="quem-faz-a-âncora"></a>

## Quem faz a âncora: o usuário ou a IA

A escolha é do usuário e acontece **na Fase A, antes de criar o pod** (a opção do Qwen muda o pod: `--qwen`).

**Pergunta modelo** (adapte aos shots do vídeo):

> Recomendo âncora de 1º frame no shot A (plano médio, personagem bem diferente). No shot C não: a pessoa entra pela borda. Como prefere?
> 1. **Você faz** no Nano Banana (Gemini) ou no GPT Image (ChatGPT). Eu preparo o frame, a imagem do personagem e o prompt, e explico o passo a passo. Sem custo de GPU; os frames vão para o Google/OpenAI.
> 2. **Eu faço** com o Qwen-Image-Edit no pod: automático, ~85 s por variação (~US$ 0,06 cada), mas o pod baixa ~31 GB a mais.
> 3. **Sem âncora**, o padrão validado.

| | Usuário (Nano Banana / GPT Image) | IA (Qwen-Image-Edit 2511 no pod) |
|---|---|---|
| Custo | Nenhum de GPU (plano do editor) | ~US$ 0,06 por variação + pod maior |
| Trabalho do usuário | Gerar 2–4 variações e devolver | Nenhum |
| Privacidade | Frames enviados ao Google/OpenAI | Fica no pod |
| Formato | Pode voltar em outra proporção (GPT Image: 2:3); a skill alinha | Mesmo tamanho do canvas |
| Pessoas reais | O editor pode recusar | Sem filtro |
| Histórico nesta skill | Não testado com gerações reais | 1 de 3 seeds usável no caso Sherlock |

### Se o usuário fizer

1. `python S/anchor_kit.py JOB/job.json A` → `JOB/anchor_kit/` com `A_frame.png` (o frame no recorte do vídeo final, na resolução da fonte), `personagem.*`, `PROMPT_A.txt` e `COMO_FAZER.md`.
2. Mostre ao usuário o `COMO_FAZER.md` e o prompt, em resumo: anexar **o frame e depois o personagem**, colar o prompt sem mudar, gerar 2–4 variações, descartar as que reenquadraram, mudaram a boca ou cortaram a pessoa, baixar em PNG na resolução máxima e **não recortar**.
3. **Espere as imagens.** Elas voltam em `JOB/anchors_user/A_v1.png`, `A_v2.png`… ou anexadas no chat (salve-as nessa pasta com esses nomes).
4. `VPY S/qa_anchor.py JOB/job.json A --set`: alinha cada imagem ao frame original (ORB no fundo; corrige o 2:3 do GPT Image e reenquadres leves), mede, cola de volta e grava a melhor. Mostre a tabela e a imagem colada ao usuário.
5. Se nenhuma passar: o usuário gera outras com o mesmo prompt, ou o shot segue sem âncora.

O prompt pede ao editor bordas em vez de recorte quando ele não conseguir manter a proporção. Se mesmo assim cortar parte da pessoa, o `qa_anchor` reprova (> 5% da pessoa fora): naquela faixa ficaria a pessoa original.

## Escolha automática das variações: `qa_anchor.py`

```bash
python S/run_job.py JOB/job.json anchor <pod> A 11,22,33,44,55     # 5 variações (~85 s cada)
VPY S/qa_anchor.py JOB/job.json A --set                            # mede, cola de volta e grava a melhor em A1.anchor
python S/run_job.py JOB/job.json best <pod> A1 11,22,33 --anchor out/anchor_A_s22_paste.png   # A/B contra o best sem âncora
```

| Medida | O que pega | Reprova |
|---|---|---|
| Silhueta (IoU fonte × âncora) | Recomposição, zoom, deslocamento | < 0,5 |
| Escala do rosto | O Qwen "afasta a câmera" | fora de 0,8–1,25 |
| Deslocamento do rosto | Rosto fora do lugar | > 0,35 largura de rosto |
| Diferença de abertura da boca (MAR) | Boca fechada/aberta diferente do frame 0 (o que derrubou o lip sync no Sherlock) | entra na nota (peso 3) |
| Identidade ArcFace × referência e × pessoa original | Troca que não aconteceu ou rosto misturado | id fonte > 0,5 ou margem < 0,1 |
| Rostos detectados | Pessoa inventada | mais rostos que a fonte (depois da colagem) |
| Fundo (PSNR) | Cena alterada | informativo; a versão colada tem o fundo da fonte |

**Colagem (`_paste.png`, padrão):** o personagem da âncora é colado sobre o frame ORIGINAL dentro de uma máscara suave (pessoa da fonte ∪ personagem da âncora). O fundo volta a ser o da fonte, e pessoas inventadas **longe** da original somem. Pessoa inventada encostada na original não dá para separar: a variação é reprovada.

**Teste feito na skill (CPU, frames reais):** cinco variações sintéticas de um frame. O frame sem troca, o personagem com outro enquadramento, o frame "afastado" (zoom 0,7, como o Qwen fazia) e o frame com uma pessoa extra foram reprovados pelos motivos certos; o rosto do personagem na posição e escala da fonte venceu (nota 1,64; identidade 0,91 × fonte −0,15).

**Ainda vale o A/B:** passar no `qa_anchor` garante que a âncora é um frame plausível do vídeo; não garante que o H3 vá sincronizar melhor com ela. Compare `best` com e sem âncora pelo `qa_take.py`.

## Pesquisa (21/10/2026): a técnica e quando ela compensa

**A técnica é comum.** Editar o 1º frame com um editor de imagem e propagar pelo vídeo é o núcleo de vários fluxos: o Viggle-Animate (character replacement a partir de um frame repintado, editado com gpt-image), o Luma Modify (o 1º frame é "optional but preferred") e o modo FL2VA do próprio H3. O consenso das fontes: **quanto mais a âncora respeitar a composição do frame original, mais estável fica a troca**; uma âncora com outra geometria força a performance a "viver" num quadro diferente. Nenhuma fonte trouxe medição de qualidade para o H3 com âncora; a evidência medida é a do caso Sherlock (piorou em close quando a âncora estava desalinhada).

**Quando compensa:** plano médio ou aberto; personagem muito diferente da pessoa original (o modelo não precisa "inventar" a transição no frame 0); início de shot com lip sync fraco que nenhuma seed resolve; e só com uma variação aprovada no `qa_anchor`.

**Quando não compensa:** pessoa entrando pela borda no frame 0; close de selfie em que as seeds sem âncora já passam; quando nenhuma variação passa no `qa_anchor`.

**Editores melhores para close (não testados aqui):** o Qwen-Image-Edit "puro" tende a recompor. LoRAs de troca de cabeça para o Qwen-Image-Edit 2511 preservam a composição por construção, porque mexem só na cabeça:
- **BFS – Best Face Swap** (Alissonerdx): versões Face/Head para Qwen-Image-Edit 2509/2511 (`bfs_head_v5_2511_original.safetensors`), com a ordem das imagens mudando por versão (Head V3–V5: imagem 1 = corpo, imagem 2 = rosto). O Face V1 troca só o rosto e mantém cabelo, luz e fundo do alvo.
- **QIE-2511-Guided-Head-Face-Swap** (prithivMLmods): transfere cabeça e identidade preservando luz, pose, composição e geometria do alvo; melhor em retratos fechados.

Eles trocam a **cabeça**, não o figurino: para personagem com roupa muito diferente (caso Sherlock), use-os para o rosto e deixe o corpo para o H3, ou siga com o Qwen + `qa_anchor`. Para adotar um deles: montar o grafo a partir do model card, gerar as variações e passar pelo `qa_anchor` como qualquer outra.
