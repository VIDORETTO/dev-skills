# 05: Âncora do primeiro frame

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
- **Revisão:** se a âncora não parecer um frame real do vídeo, refazer antes de gastar GPU no vídeo.

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
