# 01: Pipeline completo (com os scripts da skill)

`S` = pasta `scripts/` da skill. `VPY` = python do venv local (ver [08-ambiente-local.md](08-ambiente-local.md)). `run_job.py`, `make_pod.py` e `assemble.py` rodam com qualquer python 3.10+.

## Fase A: local (CPU, grátis)

1. **Análise e preparação:**
   ```
   VPY S/prepare.py --video X --character ref.png --out JOB --lang pt --res 768
   ```
   Depois, ler `JOB/analysis.md` ([00-analise-previa.md](00-analise-previa.md)).
2. **Completar o `JOB/job.json`:**
   - `character.description`: descrição detalhada;
   - em cada segmento: `dialogue` (corrigir a transcrição), `speaker` e `behavior` (ações não verbais **com tempos relativos ao segmento**: sopro, respiração, pausas, giro de câmera, entrada e saída de quadro);
   - `settings.expansion_px`: 144 para figurino volumoso;
   - `settings.use_anchor`: false é o padrão validado. Ligar só depois de um teste A/B.
   - opcional: `character.extra_image` (close do rosto/folha do figurino) e, para testar a técnica do Genjutsu, `VPY S/make_guide.py JOB/job.json --mode depth_mesh --segs A1` ([16](16-guia-profundidade.md)).
3. **Conferir o prompt de cada segmento:**
   ```
   python S/run_job.py JOB/job.json prompt A1
   ```
4. **Estimar custo e pedir o OK do usuário.** Só então criar o pod.

## Fase B: GPU (RunPod)

5. **Criar o pod:**
   ```
   python S/make_pod.py [--qwen]
   ```
   gera o `body`. Passar para a ferramenta MCP `create-pod` e informar o preço/h que o create devolver (ver [07-runpod.md](07-runpod.md)).
6. **Esperar o pod:** fazer polling de `https://<pod>-8188.proxy.runpod.net/system_stats` até responder 200 (~2–4 min). Depois:
   ```
   python S/run_job.py JOB/job.json check <pod>
   ```
   Todos os nós devem dar `True`, e as listas de modelos devem estar preenchidas e com `--extra-model-paths-config` no argv.
7. **Primeiro segmento de cada shot, best-of-N:**
   ```
   python S/run_job.py JOB/job.json best <pod> A1 31337,777,11    (opcional: --guide MODO, --no-turbo)
   ```
   Gera um take por seed, roda `qa_take.py` em cada (python do venv via `H3_VPY`) e seleciona a maior nota. Shots independentes, como o C1, podem entrar na fila junto.
8. **Conferir o vencedor** ([09-qa.md](09-qa.md)) com som; se discordar da nota:
   ```
   python S/run_job.py JOB/job.json select A1 A1_s777
   ```
   O `select` desmarca as continuações que vieram de outro histórico.
9. **Encadear o resto do shot:**
   ```
   python S/run_job.py JOB/job.json chain <pod> A [--seeds 11,22]
   ```
   Com `--seeds`, best-of-N em cada segmento. Segmento reprovado: `best`/`seg … --seed N`, `select`, e `chain` de novo (regera só o que dependia dele). Janela curta que nenhuma seed resolve: `lipfix` (pod `--latentsync`).
10. **Montar e revisar no canvas:**
    ```
    python S/assemble.py JOB/job.json JOB/final.mp4
    ```
    Em seguida, QA completa (lip sync, identidade, máscara, cor) e conferência visual das emendas.
11. **Desligar:** `delete-pod` e, depois, `list-pods` e `list-network-volumes` vazios. Não deixe cobrança parada.
12. **Final em resolução cheia (CPU, sem pod):**
    ```
    VPY S/composite.py JOB/job.json JOB/final_full.mp4 --debug-mask
    ```
    Conferir a máscara nos giros e entregar o `final_full.mp4` ([17](17-composite.md)).

## Gates (não pular)

| Gate | Critério |
|---|---|
| Fonte | SDR natural, 24 fps, shots e segmentos coerentes, sons não verbais rotulados |
| Prompt | Descrição completa; `behavior` com tempos; nenhum campo "PREENCHER" |
| Pod | `check` ok antes de enviar o 1º job |
| 1º segmento | Correlação de lip sync ≥ 0,6 na maioria das janelas de 1 s; SyncNet perto da fonte; identidade `id_ref` ≥ ~0,45 com margem ≥ 0,2 contra a fonte; chapéu e cabelo inteiros |
| Cada continuação | Emenda sem salto (identidade, luz, posição); QA ok |
| Final | Frames = fonte; cor ok; nenhuma pessoa em shot `preserve`; áudio original completo; `final_full` sem halo na borda |

## Ordem de prioridade quando algo dá errado

1. Ler a seção correspondente em [10-falhas.md](10-falhas.md). Quase tudo já aconteceu uma vez.
2. Trocar a seed (`best` com 2–3 seeds). É a variável mais barata e com o maior efeito.
3. Ajustar o `behavior` (descrever melhor o que a boca faz).
4. Ajustar a máscara (`--expansion`).
5. Só então mexer em sampler, steps ou Turbo ([06-parametros.md](06-parametros.md)).
