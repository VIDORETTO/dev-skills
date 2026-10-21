# 16: Guia de profundidade e face mesh (técnica do Genjutsu adaptada ao H3)

> **Status: experimental.** O fluxo, o grafo e os clipes foram testados (incluindo o envio ao ComfyUI e a fiação do SAM no clipe original), mas ainda não numa geração real em GPU. Use como A/B no 1º segmento.

## De onde vem

O [Genjutsu-Skill](https://github.com/SaeedAngiz1/Genjutsu-Skill) (clone aberto do fluxo do Genjutsu, sobre Seedance 2.5 Edit) não manda o vídeo original para o modelo. Antes:

1. segmenta a pessoa com SAM 3;
2. troca os pixels dela por um mapa de **profundidade colorido** (Depth Anything Video), mantendo o fundo RGB;
3. opcionalmente desenha a **malha facial** do MediaPipe (tesselação + contornos de olhos, sobrancelhas e lábios) sobre o rosto;
4. no prompt, diz que as cores e as linhas são só guia e devem sumir da saída.

O modelo recebe silhueta, pose, movimento, expressão e lábios, mas **nenhum pixel do rosto original**. Isso ataca de frente o vazamento de identidade e a tendência de imitar a "boca pequena" da fonte.

## Como foi adaptado aqui

```bash
VPY S/make_guide.py JOB/job.json --mode depth_mesh --segs A1        # cria clips_guide/depth_mesh/A1.mp4 + A1_preview.jpg
python S/run_job.py JOB/job.json best <pod> A1 11,22,33 --guide depth_mesh
python S/run_job.py JOB/job.json best <pod> A1 11,22,33             # mesma seeds, sem guia (controle)
```

| Modo | O que muda no clipe | Quando testar |
|---|---|---|
| `depth` | Pessoa vira profundidade colorida (inferno) | Personagem com corpo/roupa muito diferente; vazamento de roupa/mãos |
| `mesh` | Vídeo original + malha facial por cima do rosto | Vazamento só do rosto; boca pequena imitada |
| `depth_mesh` | Profundidade + malha facial | Os dois problemas |

- **O SAM continua no clipe original.** O `run_job.py` acrescenta um segundo `LoadVideo` (nó 32) e um `H3CharacterSwapPrepareVideo` (nó 33) e liga só a geração (`803.source_video`, `803.source`, `803.source_audio`) neles. Os nós 100–110 seguem no nó 31, então a máscara é a mesma da receita normal.
- **A pintura fica DENTRO da máscara do H3.** Fora da máscara o latente da entrada é preservado: se a profundidade vazasse para fora, ela apareceria no resultado. Por isso o `make_guide` usa a pessoa do rembg, só o **maior componente**, **erodida** (`--erode 6`). A máscara do H3 é SAM + `expansion_px`, sempre maior.
- **Várias pessoas na cena:** só a maior é pintada. Só use o guia com `selection=largest`.
- **Cor estável:** a profundidade é normalizada pelos percentis da região da pessoa no clipe inteiro, não por frame.
- **Face mesh:** landmarks sempre do frame ORIGINAL (não do pintado); frames sem rosto (perfil, oclusão) ficam sem malha e o script avisa quantos.
- **Prompt:** o `run_job.py` acrescenta a frase do modo ("Inside the person region, <Video 1> shows a colored depth map…") e "Remove all depth colors and mesh lines from the output".
- **Áudio:** o clipe-guia leva exatamente o mesmo áudio (voz isolada) do clipe original. O Genjutsu sobe a voz em +3 semitons; aqui não, porque não há motivo conhecido para isso no H3 local.
- **Nome do take:** ganha o sufixo do modo (`A1_s11_depth_mesh`).

## Riscos (o que observar no A/B)

- O LoRA nunca viu essa entrada. Pode **copiar as cores** (manchas laranja/roxas) ou as **linhas da malha** na pele. Reprova na hora; olhe o `qa_take` e os frames.
- Sem os pixels da boca original, a boca depende só de áudio + texto + malha. Se o `qa_syncnet` cair, o modo `mesh` puro (que mantém o resto do rosto) é o próximo teste.
- A profundidade monocular (Depth Anything V2 Small por frame) pode tremer nas bordas em movimento rápido. A normalização global reduz, mas não zera.

## Dependências

`VPY` com torch + `transformers` (Depth Anything V2 Small, padrão `--depth da2`, baixa do Hugging Face) ou `timm` (MiDaS small, `--depth midas`, via torch.hub/GitHub). O face mesh usa o mesmo FaceLandmarker do `qa_lipsync.py`.

## Registro

Depois do A/B, registre em `10-falhas.md` (se piorar) ou promova para a receita no `SKILL.md` (se melhorar), com os números do `qa_take` dos dois lados.
