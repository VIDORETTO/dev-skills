# 02: Pré-processamento

> O `scripts/prepare.py` automatiza tudo deste arquivo:
> - HDR para SDR, Demucs, Whisper e eventos não verbais pela energia;
> - presença com histerese (`--min-absence 12`) e filtro de pico (`--peak-min 15`);
> - cortes de câmera (`scene > 0.45`), segmentação nas pausas e clipes.
>
> Os comandos abaixo são a referência do que ele faz e servem para ajustes manuais.

## HDR para SDR (obrigatório para vídeo de iPhone e Android modernos)

Detectar pelo `color_transfer`:
- `arib-std-b67` indica HLG.
- `smpte2084` indica PQ / HDR10.

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer,color_primaries,color_space,pix_fmt -of default=nw=1 entrada.MOV
```

Conversão validada (HLG para SDR BT.709, 24 fps, 1080x1920):

```bash
ffmpeg -i entrada.MOV -map 0:v:0 -map 0:a:0 -vf "fps=24,zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1080:1920:flags=lanczos,setsar=1" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:v libx264 -crf 21 -preset slow -c:a aac -b:a 192k -movflags +faststart source_sdr.mp4
```

- **Por que isso importa:** sem tone mapping, o H3 recebe o sinal HLG como se fosse SDR (lavado). Ele "corrige" e devolve um vídeo escuro e contrastado. No caso real, o Y médio caiu de 148 para 115.
- **`npl=203`:** é o nível de referência do HDR. Se o resultado ficar escuro, subir para 300 a 400.
- **Upload:** o proxy do RunPod limita o upload a ~100 MB. Usar CRF de 20 a 22 em 1080p.

## Frame rate e orientação

- **Frame rate:** 24 fps CFR. A ferramenta reamostra, mas converter antes deixa as contas de frame exatas.
- **Orientação:** o ffmpeg aplica a rotação do metadado (`rotation -90` do iPhone) automaticamente ao reencodar.

## Detecção de presença e divisão em shots

- Rodar `presence.py` (rembg u2net_human_seg) em 360x640: o resultado é a % de pixels de pessoa por frame.
- **Shot `generate`:** só onde a pessoa está presente de forma contínua. A ferramenta oficial **recusa** frames sem a pessoa: "SAM lost the selected person… split the source shot".
- **Shot `preserve`:** onde a pessoa sai (presença ≈ 0), fica o vídeo original. O app oficial tem os modos "Replace character" e "Keep original" por shot.
- **Onde cortar:**
  - na saída, logo depois do último frame com pessoa visível (no caso real, até 371, com 6,5% de presença no último);
  - na volta, no primeiro frame com presença acima de ~3% (442).
- **Montagem do trecho `preserve`:** aplicar o mesmo recorte da preparação. Para 1080x1920 no preset 768, o recorte é `scale=-2:1344,crop=736:1344`. O alinhamento foi conferido: 44 dB de PSNR fora da máscara.
- **Cortes de câmera:** um shot por corte. Corte seco vira zoom ou reposicionamento lento dentro de uma janela.

Cortar shots com áudio sincronizado:

```bash
ffmpeg -i source_sdr.mp4 -vf "trim=start_frame=A:end_frame=B,setpts=PTS-STARTPTS" -af "atrim=start=A/24:end=B/24,asetpts=PTS-STARTPTS" ... shot.mp4
```

## Isolamento de voz (recomendação da comunidade)

- **Por quê:** o condicionamento por áudio funciona melhor com a voz limpa; ruído de rua e vento confundem o lip sync. Um relato (note.com) diz que, com a mixagem completa, o modelo não sabe a que reagir, e que isolar a voz melhora boca e mandíbula.
- **Ferramentas:** Demucs `htdemucs` (`--two-stems vocals`) ou MelBand-Roformer.
- **Como aplicar:** remuxar o **vídeo de entrada do ComfyUI com a faixa de voz isolada**, que é o que vai para o condicionamento e o guia. Na montagem final, usar o **áudio original completo**.
- **Timeline:** o stem deve sair exatamente da mesma timeline (mesmo `trim`). Mover um clipe com lip sync no tempo quebra a sincronia.

## Transcrição (para o prompt)

- **Ferramenta:** faster-whisper com `word_timestamps=True`. Para português, usar `large-v3` com `language="pt"`. O app oficial usa `medium.en`, só inglês.
- **Atribuição por segmento:** cada palavra vai para o segmento que contém o seu ponto médio, `start/24 <= (w.start+w.end)/2 < end/24`, mesma regra do app.
- **Silêncios:** marcar. Trechos sem fala pedem a instrução de boca fechada e relaxada.
- **Quem fala por segmento:** `target` (o personagem fala), `offscreen` (voz fora de quadro: não mexer a boca), `other` (outra pessoa fala) ou `none`.
