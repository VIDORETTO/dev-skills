# 03: Prompt

## Princípio (consenso das fontes)

> A imagem define a identidade. O vídeo define a performance. O prompt faz o roteamento e as restrições.

- **Descrever bem o personagem.** O prompt genérico "replace the person" teve desempenho ruim na validação oficial e preservou a identidade original.
- **Não redescrever o movimento** que o vídeo já mostra. Isso cria mais uma camada de interpretação.
- **Não exagerar nas instruções de expressão.** O model card da V1 diz que isso às vezes anula a troca.
- **O diálogo entra no prompt.** É o que dirige o lip sync. O formato oficial da MiniMax usa `<d>[Language] …</d>`, com IDs de falante `(S1)`. Sem isso, a boca fica genérica.

## Template validado pelo app oficial (por segmento)

Montado por `h3workbench/media.py` e `segments.py`:

```
Replace only the selected person in <Video 1> with the single character in <Picture 1>: {DESCRIÇÃO DO PERSONAGEM}.
<Picture 2> is the exact first-frame scene and pose anchor.            ← 1º segmento, com âncora
  ou: <Picture 2> is the generated boundary from the preceding segment. Continue its motion and appearance.   ← continuação
Keep the reference identity and costume throughout. Match source posture, gaze, blinks, facial emotion, mouth movement, hand contacts and camera movement.
The selected character is speaking.                                    ← target | offscreen | other | none
Current segment dialogue: "{PALAVRAS DO SEGMENTO}". Follow source audio timing. Earlier reference dialogue is context only; do not repeat it.
<Audio 1> and source video determine exact timing. Do not repeat earlier dialogue or invent words, gestures, people or camera cuts. Retain the scene outside the person region. Output the raw decoded generation.
```

### Rótulos das imagens (a ordem é a do envio)

A ferramenta envia as imagens nesta ordem e rotula `<Picture N>` só as que existem: personagem, [âncora do 1º frame **ou** boundary gerado], [slot extra]. O `run_job.py` numera sozinho:

| Situação | `<Picture 1>` | `<Picture 2>` | `<Picture 3>` |
|---|---|---|---|
| 1º segmento, sem âncora | personagem | referência extra (se houver) | — |
| 1º segmento, com âncora | personagem | âncora | referência extra (se houver) |
| Continuação | personagem | boundary gerado | âncora no meio do shot **ou** referência extra |

- **Referência extra** (`character.extra_image`): "an additional identity reference of the same character from <Picture 1> (face and costume detail); use it only for appearance". Use um close nítido do rosto ou a folha do figurino. Teste por A/B.
- **Guia de profundidade/face mesh** (`--guide`): o prompt ganha a explicação do guia e "Remove all depth colors and mesh lines from the output" ([16](16-guia-profundidade.md)).
- Confira sempre com `run_job.py JOB prompt <seg> [--guide MODO]`.

Frases de "quem fala":

| Modo | Frase |
|---|---|
| `target` | "The selected character is speaking." |
| `offscreen` | "Speech is offscreen; do not make the selected character speak." |
| `other` | "Another person is speaking; preserve the selected character's actual mouth performance." |
| `none` | "No dialogue; preserve the visible source performance." |

## Formato oficial MiniMax H3 (modo full-reference)

Fonte: `MiniMaxAI/MiniMax-H3/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`. São seis seções, nesta ordem:

`subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`

- **`summary`:** para swap mantendo o áudio, começar com `[video editing + reference generation + audio reuse] The target video is an edited version of <Video 1>.`
- **Marcadores visuais:** `fully_preserved`, `partially_preserved`, `attribute_transfer` e `weak_reference`.
- **Marcadores de áudio:** `fully_copy`, `partially_copy`, `reference` e `weak_reference`. Se o áudio de origem fica, use `<Audio 1>: fully_copy`.
- **Fala:** `<Subject 1> (S1) says, <d>[Portuguese] texto exato </d>`. Trechos ininteligíveis viram `[unclear]`. Não colocar `(Sx)` em `retention_analysis`.
- **Tamanho:** `detailed_description` em edição escala com a complexidade da fonte. Descrever composição, posição, luz, ação e câmera.
- **Pausas:** depois da fala, escrever "closes his lips". Em silêncio, boca fechada ou relaxada.

O workflow adaptativo do akatz (h3-relay) já usa essa estrutura. Veja o texto em `job2/akatz_prompt.txt`.

## Dicas de lip sync da comunidade

- **Comportamento da boca:** descrever o comportamento, não só o texto. Falar só quando há voz audível, acompanhar o início das frases, as sílabas e as respirações, e fechar os lábios no silêncio.
- **Primeiro frame:** já deve parecer fala, com a boca entreaberta no meio de uma palavra. Isso vale para a âncora, ver [05](05-ancora.md).
- **Início dos shots:** o diálogo tende a se concentrar no começo do shot. Dar uma ação a cada trecho.
- **Close:** "locked camera, no head turns while speaking" protege o lip sync quando a câmera é livre (relato da comunidade).
- **Fórum do LoRA:** "From the VERY first frame, replace <Subject 2> in <Video 1> with <Subject 1> in <Picture 1>". Assim, nos sigmas altos o modelo não precisa disputar identidades.

## Template de descrição do personagem (exemplo validado)

`job3/prompt.txt` descreve:
- idade aparente, pele, formato do rosto, maçãs, nariz, olhos, sobrancelhas e barba;
- cabelo (cor, volume, comprimento, costeletas);
- cada peça de roupa com cor, padrão e material;
- "Keep … exactly as in <Picture 1> in every frame and from every angle".

## Armadilhas

- **Referências sem uso:** não definir papéis para referências que não estão conectadas.
- **Prompt único em shot longo:** um único prompt com a fala inteira de um shot de 15 s faz cada janela receber o diálogo todo. Usar prompt **por segmento** (modo segmento da ferramenta, ver [06](06-parametros.md)).
- **Contradições:** não pedir "preserve outfit" e trocar a roupa ao mesmo tempo.
