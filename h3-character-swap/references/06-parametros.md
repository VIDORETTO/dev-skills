# 06: Parâmetros

## Modelos (validados em 17/10/2026)

| Papel | Arquivo | Repositório |
|---|---|---|
| DiT | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` (21 GB) | Comfy-Org/MiniMax-H3 |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` (15,7 GB) | Comfy-Org/MiniMax-H3 |
| VAE de vídeo | `minimax_h3_video_vae_fp16.safetensors` | Comfy-Org/MiniMax-H3 |
| VAE de áudio | `minimax_h3_audio_vae_fp32.safetensors` | Comfy-Org/MiniMax-H3 |
| Turbo | `minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16.safetensors` | lightx2v/Minimax-h3-Turbo |
| Swap | `h3_character_swap_v1.5.safetensors` (strength 1.0, **não empilhar** com a v1) | akatz-ai/MiniMax-H3-Character-Swap-LoRA |
| SAM | `sam3.1_multiplex_fp16.safetensors` em `checkpoints/` | Comfy-Org/sam3.1 |

- **Text encoder:** usar o oficial `nvfp4_awq`. O "heretic" do template não é o da receita.
- **Licença:** MiniMax H3 Community License, que exclui EUA, UE, Reino Unido e Coreia do Sul da concessão territorial padrão.

## Sampler (receita oficial testada)

- **Base:** 8 steps, CFG 1, `er_sde`, scheduler `normal` (a ferramenta) ou `simple` (o h3-relay), sigma shift 12/3 e atenção comfy kitchen.
- **Turbo e base:**
  - O Turbo 8-step é a receita do autor.
  - A comunidade relata que **para closes com lip sync visível a versão base com ~20 steps (sem Turbo) sincroniza melhor**, e que Turbo de 4 steps perde precisão.
  - Recomendação: usar Turbo 8 para iterar. Se a QA de lip sync reprovar um close, renderizar esse segmento sem Turbo, com 20 steps, `res_multistep` e `simple`.
  - Na ferramenta, para tirar o Turbo: remover o nó 4 da cadeia, ligando `850.model` a `["3",0]`, e mudar o nó 801 para `steps 20`.

## Janelas, histórico e duração

- **Janela:** 124 frames (5,17 s) é o "sweet spot" segundo o próprio autor no fórum. O máximo prático fica entre 5 e 10 s; com 15 s, o LoRA "almost completely loses its effectiveness".
- **Histórico:** 18 frames por padrão; também aceita 35, 52 e 69. Mais histórico aumenta a continuidade, mas reduz o trecho novo.
- **Grade de frames do H3:** `17n+5`.
- **Prompt por segmento:** a ferramenta aceita `segment_mode=True` no nó 803, com `history_file` apontando para um `.npz` (float32 RGB, com 1 ou 18, 35… frames). Assim cada segmento roda separado com o seu diálogo. A saída de cada segmento inclui `continuation_master` (MKV rgb48le), de onde se extraem os últimos 18 frames para o segmento seguinte. É o mecanismo usado pelo app.

## Resolução

- **Presets:** `480` (~0,5 MP) para prévia, `768` (~1 MP, 736x1344 em vídeo vertical) para o final. O LoRA foi treinado com edições de área 1024 (1344x768).
- **Prévia:** a comunidade testa em ~0,2 MP para validar movimento e lip sync antes de subir.
- **Referência:** a ferramenta reduz a referência para a área da geração (`ref_image_size='match'`). Uma referência pequena (recorte de 270 px) deixa o rosto "plastificado".

## Seeds

- **Variação:** o resultado depende muito da seed. O fórum relata "4 gerações, 1 perfeita".
- **Método:** usar seed fixa por segmento e dar reroll **só** no segmento reprovado na QA. Os anteriores ficam como estão; os posteriores são refeitos porque dependem do histórico.
- **Vazamento:** detalhes do personagem original "vazando" (mãos, dentes, acessórios) às vezes se resolvem só trocando a seed.

## Memória (RTX PRO 6000, 96 GB)

- **Sem `--highvram`:** com essa flag, deu OOM em 768p com janela de 124.
- **Flags da ferramenta:** `--reserve-vram 0 --disable-dynamic-vram --enable-triton-backend --cache-classic`.
- **Pico observado:** ~76 GB durante a amostragem.
