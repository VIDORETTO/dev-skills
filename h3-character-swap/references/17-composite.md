# 17: Final em resolução cheia (`composite.py`)

## Por quê

O H3 entrega o **canvas** (736x1344 no preset 768) inteiro decodificado pelo VAE. A ferramenta nunca cola o resultado sobre o RGB da fonte (no código: `body_composited: False`, "decoded generation, never pasted onto source RGB"). Consequências no `final.mp4` do `assemble.py`:

- resolução final de 736x1344, mesmo com a fonte em 1080p ou 4K;
- o fundo inteiro passa pelo VAE (ΔY ≈ −3 e perda de detalhe fino), mesmo sendo "preservado" no latente;
- os shots `preserve` saem recortados no aspecto do canvas.

Kling e Genjutsu entregam 1080p. O `composite.py` fecha essa diferença sem GPU.

## O que ele faz

```bash
VPY S/composite.py JOB/job.json JOB/final_full.mp4 [--mask union|expanded] [--margin 32] [--feather 12] [--takes-dir out] [--debug-mask]
```

1. **Plate** = `source_sdr.mp4` (fonte SDR a 24 fps, 1080 no lado menor), quadro inteiro.
2. Para cada frame gerado: calcula a posição exata do canvas dentro do plate (inverso do `scale+crop` da preparação; conferido contra o ffmpeg com erro ≤ 0,5 px da fonte) e amplia o take para lá (Lanczos).
3. **Máscara** (no canvas):
   - `union` (padrão): pessoa da fonte ∪ personagem gerado (rembg), dilatados por `--margin` px. Pega chapéu, capa e o que o personagem tem a mais que a pessoa original.
   - `expanded`: pessoa da fonte dilatada por `settings.expansion_px` (a região inteira que o H3 regenerou) ∪ personagem. Mais seguro para sombras e reflexos do personagem; devolve menos fundo original.
4. **Estabilização no tempo:** máscara = máximo de t−1, t, t+1, para a borda não "piscar".
5. **Borda suave:** blur gaussiano de `--feather` px. Como `margin` > `feather`, o personagem fica 100% opaco e a transição cai sobre o fundo regenerado, que já é quase igual à fonte.
6. Shots `preserve`: o plate puro.
7. Áudio original completo; confere a contagem de frames contra a fonte.

## Leituras e cuidados

- **Fundo:** fora da máscara é a fonte (só a recompressão: ~40 dB no teste, igual a um shot `preserve`). `qa_color.py` deve dar ΔY ≈ 0.
- **`--debug-mask`:** grava `final_full_alpha.mp4`. Revise os giros rápidos e os frames de entrada/saída de quadro.
- **Halo:** se aparecer uma "aura" de fundo levemente diferente em volta do personagem, aumente `--feather` (transição mais longa) ou use `--mask expanded`.
- **Personagem cortado:** se o rembg perder parte do figurino (aba de chapéu fina, objeto na mão), use `--mask expanded`.
- **Tempo:** dois rembg por frame gerado na CPU (~1–1,5 s/frame em 736x1344). Um vídeo de 22 s leva ~10–15 min.
- **Recusa:** se algum take escolhido tiver contagem de frames errada ou tiver vindo de outro histórico, ele para antes de começar.

## Upscale do personagem

Hoje o personagem é ampliado com Lanczos (×1,47 de 736 para 1080). Um passe gerativo (LMS LoRA, H3 Ultimate 2× Enhance ou LTX 2× do Relay 2.0; ver [15-fronteira.md](15-fronteira.md)) daria mais detalhe. O `composite.py` já aceita isso: gere os takes ampliados (qualquer resolução com o aspecto do canvas), salve com o mesmo nome numa pasta e passe `--takes-dir`. A máscara continua sendo calculada no canvas.
