# 11: Caso real completo, "Sherlock" (17/10/2026)

O caso que originou a skill: 4 rodadas, o que cada uma mudou e o que os números mostraram. Use para calibrar expectativas e para reconhecer sintomas.

## Entrada

- **Vídeo:** `IMG_4882.MOV` do iPhone, 4K HEVC 10 bits **HLG/BT.2020**, 60 fps, vertical (rotação −90), 22,5 s.
- **Cena:** selfie de um homem careca de camiseta escura falando em português na rua.
  - **0,5–1,9 s:** ele **assopra** para a câmera, com os lábios em bico.
  - **Fala:** "Pessoal, meu nome é Sherlock Holmes. Eu passei 5 anos procurando a melhor oficina de motos de Araras. E eu finalmente encontrei. Tá aqui." Depois **vira a câmera para a rua e para a fachada da loja** (15,5–18,4 s, sem pessoa) e volta: "Motocão Motocenter. Pode trazer aqui."
- **Personagem:** 3 folhas de referência de um Sherlock com chapéu deerstalker de tweed, cabelo cacheado volumoso, casaco com capa, colete, camisa branca e gravata de tricô.

## Rodada 1: template do RunPod + workflow nativo, 480p, 2 trechos de 11,5 s

- **Erros:**
  - prompt genérico;
  - áudio **não** condicionado;
  - recorte de 270 px da folha como referência;
  - trechos independentes;
  - composição de fundo com rembg;
  - **bug no download** (pegou a saída do `LoadVideo`).
- **Resultado:** lip sync horrível, rosto plastificado, salto no meio, halos.

## Rodada 2: h3-relay `H3RelayWindowedEdit` 768p, janelas 124/18 com áudio de origem

- **Melhorou:** enquadramento, emendas e visual fotográfico.
- **Problemas:**
  - **cor e contraste errados**, porque a fonte HDR não foi convertida (Y 115 contra 148);
  - **personagem inventado na fachada vazia** (frames 414–438);
  - fundo regerado inteiro.
- **Infra:** OOM por `--highvram`; corrigido.

## Rodada 3: ferramenta oficial com SAM (máscara 64 px), SDR, shots separados, prompt descritivo

- **Melhorou:** fundo idêntico (44 dB), cores naturais, fachada original.
- **Problemas:**
  - **lip sync ruim nos primeiros ~4 s** (correlação −0,02 a 0,38);
  - **parte do chapéu sumindo** nos closes (máscara da cabeça careca + 64 px).

## Rodada 4: segmentos com diálogo, voz isolada, máscara de 144 px, ações não verbais

- **Preparação:**
  - Whisper large-v3 (29 palavras) e Demucs;
  - energia por 0,25 s mostrou o sopro (0,5–1,9 s, sem palavras);
  - segmentos cortados em pausas: A1 0–129, A2 130–282, A3 283–371 (original 372–441), C1 442–539.
- **Âncoras com Qwen-Image-Edit 2511:**
  - frame 0: 1 de 3 seeds usável;
  - frame 442 (pessoa parcial na borda): o Qwen **inventou uma 2ª pessoa**.
- **Testes A/B no A1** (correlação global / razão de amplitude):

| Variante | Corr | Amp |
|---|---|---|
| âncora + diálogo `<d>` | 0,28 | 2,43 |
| âncora + template do app entre aspas | 0,17 | 2,05 |
| âncora + "siga a performance" (sem diálogo) | 0,21 | 2,13 |
| **sem âncora** + `<d>` + sopro descrito | **0,67** | 1,87 |
| sem âncora + `<d>` sem sopro descrito | 0,41 | 1,43 |
| sem âncora + pausa explícita, seed 777 | 0,58 | 1,70 |
| **sem âncora + pausa explícita, seed 31337** | **0,75** | 1,78 |

- **Final:**
  - shot A 0,71 (sopro 0,94, pausa 0,51, "Pessoal" 0,23);
  - shot C 0,82 (antes 0,70);
  - chapéu inteiro, emendas contínuas;
  - **avaliação do usuário: "ficou perfeito".**

## Lições que viraram regra

1. Converter HDR para SDR antes de tudo.
2. Dividir em shots onde a pessoa sai de quadro; o trecho vazio fica com o original.
3. Usar a ferramenta oficial com máscara SAM e expansão proporcional ao figurino.
4. Prompt por segmento: diálogo transcrito **e** ações não verbais com tempo.
5. Voz isolada no condicionamento, áudio original na entrega.
6. Âncora opcional, decidida por A/B. Em close de selfie, ela piorou o resultado.
7. Seeds variam muito (0,58 contra 0,75 no mesmo prompt): testar 2–3 no 1º segmento.
8. Medir sempre: `qa_lipsync.py`.
9. Limite residual: fala de "boca pequena" sai mais articulada. É limitação admitida pelo autor do LoRA.
