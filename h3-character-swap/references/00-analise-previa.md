# 00: Análise prévia (antes de gastar um centavo de GPU)

A maior parte dos defeitos vistos em 4 rodadas reais nasceu **antes** da GPU: HDR não convertido, pessoa saindo de quadro, sopro não descrito, máscara pequena para o figurino. A análise prévia existe para pegar tudo isso de graça, na CPU local.

## 1. Rodar o `prepare.py`

```bash
python scripts/prepare.py --video <video> --character <ref.png> --out <job_dir> --lang pt --res 768
```

Ele gera `analysis.md`, `job.json` (rascunho), clipes por segmento e os frames de âncora. Leia o `analysis.md` **inteiro** e responda às perguntas abaixo.

## 2. Checklist da fonte

| Pergunta | Onde ver | Se sim |
|---|---|---|
| A fonte é HDR (`arib-std-b67` ou `smpte2084`)? | `analysis.md` › Fonte | O prepare já converte. Conferir visualmente se o SDR ficou natural; se estiver escuro, subir `npl` de 203 para 300–400 |
| Tem corte de câmera? | Cortes detectados | Um shot por corte. Corte dentro de janela vira "zoom" |
| A pessoa sai de quadro? | Tabela de shots (`preserve`) | Esses trechos ficam com o original. Confirmar os limites, sem gerar pessoa em cena vazia |
| Há outras pessoas? | Olhar frames | Ajustar `sam_text` (ex.: "bald man in dark t-shirt") e `selection` |
| Há oclusões (mão no rosto, objeto)? | Olhar frames | Revisar esses frames na máscara e na QA |
| Há giro rápido de câmera ou motion blur? | Olhar frames | Esperar borrão leve. Revisar a borda da máscara nesses frames |
| Quanto o rosto ocupa (close extremo, médio, aberto)? | Frames | Close extremo: lip sync é o critério principal; usar máscara maior. Aberto: a âncora pode ajudar |
| A pessoa fala? Em que língua? Quem fala? | `transcript.json` | Preencher `speaker` por segmento (`target`, `offscreen`, `other` ou `none`) |
| Há sons vocais **sem palavra** (sopro, respiração forte, riso, tosse, assobio)? | ⚠️ em `analysis.md` | **Descrever com tempos no `behavior`.** No caso real, isso levou a correlação de 0,41 para 0,67 |
| A fala é "de boca pequena" (pessoa que mexe pouco os lábios)? | Ver os frames falando | Avisar o usuário: o LoRA tende a articular mais. Testar seeds |

## 3. Checklist do personagem

| Pergunta | Ação |
|---|---|
| A referência é nítida e grande (rosto ≥ ~300 px; ideal 1000 px ou mais)? | Se for recorte pequeno, o resultado fica "plastificado". Pedir imagem melhor |
| A referência é uma folha (várias vistas)? | Serve. Folhas variadas fizeram parte do treino. Usar a **imagem inteira**, não um recorte minúsculo |
| O personagem tem volume maior que a pessoa original (chapéu, cabelo armado, capa, ombreiras)? | `expansion_px` de 128 a 160 (o padrão oficial é 64 e cortou o chapéu) |
| O estilo é cartoon, anime ou 3D sobre vídeo real? | É possível (cross-style faz parte do treino), mas é mais instável. Prever mais seeds |
| Luz de estúdio ou fundo branco na referência? | O prompt já pede para adaptar à luz da cena. Conferir na prévia |

Escreva `character.description` com rosto (idade aparente, pele, formato, olhos, sobrancelhas, nariz, barba), cabelo (cor, volume, comprimento) e **cada peça de roupa** (cor, padrão, material). Veja exemplos em [13-exemplos.md](13-exemplos.md).

## 4. Checklist de segmentação

- **Tamanho:** ~4–6,5 s cada (90–157 frames). O ideal do autor é 124 frames; acima de 10 s há drift.
- **Onde cortar:** de preferência em pausa de fala. O prepare procura frames sem palavra.
- **Primeiro segmento:** é o mais difícil (sem histórico) e merece 2–3 seeds.
- **Continuações:** usam 18 frames de histórico do take escolhido do segmento anterior. Mudar o take anterior obriga a regerar os seguintes.

## 5. Estimativa para o usuário (antes de ligar o pod)

| Item | Valor de referência (RTX PRO 6000, US$ 2,49/h) |
|---|---|
| Boot com download dos modelos | ~2–4 min |
| Segmento de ~5 s em 768p, Turbo 8 steps | ~3,5–6,5 min |
| Âncora Qwen (opcional) | ~85 s por variação |
| Vídeo de 20 s, 4 segmentos, 1 take cada | ~25 min, ~US$ 1 |
| Com 3 seeds no 1º segmento e um reroll | ~45 min, ~US$ 2 |

Diga o custo estimado ao usuário e confirme **antes** de criar o pod.

## 6. Relatório prévio ao usuário (modelo)

```
Análise prévia — <vídeo>
• Fonte: <res> <fps> <duração> · <HDR→SDR | SDR> · canvas <W>x<H>
• Shots: A (0–15,5 s) gerar · B (15,5–18,4 s) original, sem pessoa · C (18,4–22,5 s) gerar
• Segmentos: A1 5,4 s (sopro 0,5–1,9 s + "Pessoal, meu nome é…") · A2 6,4 s · A3 3,7 s · C1 4,1 s
• Riscos: close extremo (lip sync); fala de boca pequena; chapéu maior que a cabeça (máscara 144 px); giro rápido aos 15 s
• Plano: 3 seeds no A1 → escolher pela QA → encadear A2/A3 → C1 → montar
• Estimativa: ~40 min de GPU, ~US$ 1,70. Posso criar o pod?
```
