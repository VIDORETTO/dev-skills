# 04: Máscara (SAM 3.1)

## Como funciona na ferramenta oficial

O fluxo de nós é este:

```
CheckpointLoaderSimple(sam3.1_multiplex_fp16)
  → CLIPTextEncode("person")
  → SAM3_Detect(threshold .35, refine 2, individual_masks)
  → H3CharacterSwapSelectSubject(largest | leftmost | rightmost | index)
  → SAM3_VideoTrack(detection .5, max_objects 1)
  → SAM3_TrackToMask
  → H3CharacterSwapRecoverMasks       (redetecta só os frames vazios)
  → H3CharacterSwapExpandMask(expansion_px=64)
  → MaskedRegeneration
```

- **Fora da máscara:** o latente VAE da fonte é preservado (inpaint nativo). Por isso o fundo fica igual ao original.
- **Dentro da máscara:** denoise 1.0. O personagem só pode existir **dentro** da máscara.
- **Frame sem pessoa:** a ferramenta para com o erro "SAM lost the selected person". A solução é dividir o shot.

## O problema do chapéu (caso real, rodada 3)

A máscara nasce da silhueta da **pessoa original** (careca) mais um raio fixo de 64 px. O personagem com deerstalker, cabelo volumoso e capa ocupa mais espaço do que isso.

- **Nos closes:** com a cabeça ocupando ~70% da largura, 64 px é pouco, e o topo e as abas do chapéu passam da borda.
- **O que acontece fora da máscara:** volta o fundo original, então o chapéu ou casaco aparece **cortado**.

## Regra de expansão (proporcional)

- **Fórmula de partida:** `expansion_px = max(64, 0.25 × altura da bbox da cabeça)` no frame de maior close.
- **Para cima:** chapéu alto ou cabelo armado precisam de ainda mais. O nó só expande de forma radial, então se o topo for o problema, o raio radial cobrindo o topo é o que manda.
- **Corpo:** capa, ombreiras e figurino mais largo que a roupa original exigem expansão também nos ombros.
- **Teto:** no máximo 256 px no nó. Expansão grande demais regenera mais fundo, que vai precisar ser reconstruído. Ainda é seguro, mas aumenta o risco de o fundo mudar.
- **Exemplo:** para o caso Sherlock em 736x1344, o recomendado é **128 a 160 px**.

## Revisão obrigatória antes de gerar

- **O que olhar:** o nó 111/112 (`ImageFromBatch` → `PreviewImage`) mostra o overlay verde. Revisar o frame de maior close, o de cabeça mais alta, o de maior giro e o primeiro e o último do shot.
- **Execução parcial:** rodar só até a prévia da máscara (execução parcial no ComfyUI) antes da geração completa.
- **Depois de gerar:** usar `qa_mask.py` (ou o `qa_take.py`, que já o inclui) para medir quanto do personagem gerado cai fora da máscara. No caso real, o frame 200 teve 14,8% fora.
- **Guia de profundidade (`--guide`):** a máscara continua vindo do clipe original; a pintura do guia fica dentro dela ([16](16-guia-profundidade.md)).

## Máscara salva (fluxo do app)

- **Pipeline:** o app gera a máscara, revisa e corrige com pontos positivos e negativos (`H3CharacterSwapRefinePersonMask`), salva em `.npz` e passa para a render com `H3CharacterSwapLoadMask(mask_file, expansion_px)`.
- **Vantagem:** a máscara revisada é reaproveitada em todos os rerolls e segmentos, e o SAM não roda de novo.

## Outras dicas

- **Texto do SAM:** pode ser mais específico que "person" quando há várias pessoas, por exemplo "bald man in dark t-shirt". Ajustar `selection`.
- **Oclusões:** mão no rosto e objetos na frente são o ponto mais frágil. Conferir o frame antes do contato, o de maior cobertura e o primeiro frame limpo depois.
- **Boca mascarada:** o lip sync vem do áudio e do texto, não dos pixels da boca original. Por isso o prompt com diálogo e a voz isolada importam.
