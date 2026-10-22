# 10: Registro de falhas (para não repetir)

| # | Rodada | Sintoma | Causa raiz | Correção / regra |
|---|---|---|---|---|
| 1 | 1 | Parecia "sem troca" | Script baixou a saída do `LoadVideo` (a entrada) em vez da do `SaveVideo` | Ler a saída **pelo ID do nó de saída**. Desconfiar se o arquivo tiver o mesmo tamanho da entrada |
| 2 | 1 | Lip sync horrível | Áudio de origem fora do condicionamento; troquei o áudio depois (remux) | O áudio de origem entra no Ref2VA e no guia. O remux não conserta lip sync |
| 3 | 1 | Salto no meio do vídeo | Dois trechos independentes de 11,5 s, sem histórico | Janelas de 124 frames com histórico de 18 |
| 4 | 1 | Rosto plastificado | Referência recortada em 270 px e geração em 480p | Referência em alta resolução; 768p no final |
| 5 | 1 | Halos e fundos misturados | Minha composição com rembg | Não compor à mão; usar a difusão mascarada oficial |
| 6 | 2 | OOM em 96 GB | `--highvram` do template | Remover a flag |
| 7 | 2 | Cores e contraste estourados | Vídeo HDR (HLG) sem tone mapping | Converter para SDR BT.709 antes ([02](02-preprocessamento.md)) |
| 8 | 2 | Personagem aparece na fachada vazia | A pessoa sai de quadro, e o modelo inventa o personagem | Dividir em shots; trecho vazio fica original |
| 9 | 2 | Fundo regerado | `H3RelayWindowedEdit` não usa máscara | Ferramenta oficial com SAM |
| 10 | 3 | Lip sync ruim nos primeiros ~4 s | Primeira janela sem âncora e prompt sem diálogo transcrito | Âncora no frame 0 ([05](05-ancora.md)); diálogo por segmento ([03](03-prompt.md)); voz isolada |
| 11 | 3 | Parte do chapéu some | Máscara da cabeça careca + 64 px menor que o deerstalker nos closes | Expansão proporcional de 128 a 160 px e revisão do overlay ([04](04-mascara.md)) |
| 12 | 3 | Mancha cinza na parede durante giro rápido | Borda da máscara com movimento rápido (1 a 2 frames) | Reroll do segmento ou máscara maior; revisar giros rápidos |
| 14 | 4 | Âncora Qwen piorou o lip sync (de 0,67 para 0,28) e dobrou a abertura da boca | A âncora fixa um rosto com escala e boca diferentes, e o H3 segue a âncora em vez da fonte | Âncora **opcional**: testar com e sem, pela QA. Neste vídeo (selfie em close), sem âncora venceu |
| 15 | 4 | Âncora para shot que começa com a pessoa entrando pela borda | O Qwen recompôs a cena e inventou uma segunda pessoa | Não usar âncora quando a pessoa está parcial no frame 0 |
| 16 | 4 | Sopro e respiração viravam "fala" | O prompt não mencionava ação de boca sem fala | Descrever no prompt, com tempos, as ações não verbais (sopro, respiração, pausa). Correlação de 0,41 para 0,67 |
| 17 | 4 | Lista de modelos vazia no ComfyUI | O ComfyUI subiu antes de o template gravar o `extra_model_paths.yaml` (corrida) | Gravar um yaml próprio e passar `--extra-model-paths-config`, com `MODEL_VOLUME_PATH` apontando para a pasta (evita o download duplo de 89 GB) |
| 18 | 4 | Fala com a boca quase fechada (o original articula pouco) sai com articulação maior | Limite do LoRA ("close-up expressions may not match") | Várias seeds, ficar com a melhor pela QA. Aceitar o limite residual |
| 13 | infra | Pod de CPU OOM; volume recusado; 403 no proxy | Ver [07](07-runpod.md) | Ver [07](07-runpod.md) |
| 19 | skill | `prepare.py` criou um shot `preserve` de 2 frames no meio da fala | Queda momentânea de detecção (rosto muito perto ou balanço de câmera) | Histerese: ausência menor que 12 frames é ignorada (`--min-absence`) |
| 20 | skill | Shot começando antes de a pessoa voltar (pedestres de 3–6% na fachada contados como "pessoa") | Limiar de presença baixo para trechos de fundo | Filtro de pico: o trecho só conta se a presença passar de 15% em algum frame (`--peak-min`) |
| 21 | skill | QA de cor acusou −30 de Y no vídeo inteiro | O figurino escuro no lugar da pele clara muda o Y médio do quadro (não é defeito) | `qa_color.py` mede **só o fundo** (fora das pessoas, dilatado 180 px). Fundo real: Δ ≈ −3 (ok) |
| 22 | skill | Whisper omitiu "Motocão" numa execução e não na outra | Variação do Whisper | Revisar `dialogue` à mão; a transcrição é rascunho |
| 23 | 18/10 | O `main` da h3-character-swap-tool removeu `worker_nodes/h3_character_swap` (refactor Relay 2.0 em 17/10) | Clonar `main` sem fixar versão quebraria o boot | `make_pod.py` faz checkout do commit validado `0670e4fdf95a`. Revalide antes de migrar |
| 24 | skill | `prepare.py` quebrava (`min() arg is an empty sequence`) em shots de 158–179 frames (e 288–309, 418–439…) | Em `split()`, quando o resto fica entre `max` e `max+min`, `hi = e−min` < `lo` | Corrigido em 21/10: nesse caso corta perto do meio. Testado de 22 a 3000 frames |
| 25 | skill | Depois de `select A1 <outro take>`, o `chain` pulava o A2 antigo (gerado com o histórico do A1 anterior) e a montagem saía com emenda errada | O `chain` só checava se havia take escolhido | Corrigido em 21/10: cada take grava `history_from`; `select` desmarca os seguintes de outro histórico; `chain` regera só esses; `assemble`/`composite` recusam montar |
| 26 | skill | Regerar uma continuação com a mesma seed e outro histórico sobrescrevia o take antigo | O nome do take era só `<seg>_s<seed>` | Continuações levam `_hXXXX` (marca do take anterior); os dois takes convivem |
| 27 | skill | Download de modelo falhando 3 vezes no boot passava em silêncio; o erro só aparecia no 1º job | O laço de download não verificava o resultado | `make_pod.py` imprime `SEED_FAILED`/`BOOT_ABORT` e o ComfyUI não sobe (pod fica de pé para ler o log) |
| 28 | 22/10 | Âncoras "de teste" montadas por código (rosto colado) passavam nos números e falhavam no olho; o usuário pediu para parar | Imagem sintética não representa o editor nem a referência real | Âncora e teste de âncora só com editor de verdade (Qwen ou Nano Banana/GPT Image) e frames/referências reais e boas ([05](05-ancora.md)) |
| 29 | 22/10 | Edição real com o rosto nítido reprovada como "sem rosto" | O FaceLandmarker do MediaPipe falha com rosto pequeno (~135 px) no quadro inteiro | `qa_anchor` e `qa_lipsync` (e o `qa_syncnet`, que usa o mesmo código) tentam de novo num recorte ampliado em volta do rosto. Num vídeo do mesmo frame: antes 0/48 frames medidos, depois 48/48 |
| 30 | 22/10 | Aviso de "boca mais fechada" com as duas bocas no mesmo estado | Abertura da boca medida em coordenadas normalizadas, distorcidas no quadro vertical | MAR em pixels no `qa_anchor`; limite do aviso e peso na nota recalibrados (0,10 e 1,6) |
| 31 | 22/10 | Na folha de revisão, o recorte "boca" não mostrava a boca e a etiqueta cobria a imagem | Recorte estimado pelo centro do rosto da fonte e aplicado igual nas duas imagens | Recortes centrados nos pontos dos lábios e do rosto de cada imagem; etiquetas numa faixa acima |
