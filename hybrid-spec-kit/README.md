<div align="center">

# Hybrid Development Kit

**Skills locais para transformar intenção em trabalho executável, verificável e retomável.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](#requisitos)
[![10 skills](https://img.shields.io/badge/skills-10-7C3AED?style=flat-square)](#skills)
[![stdlib only](https://img.shields.io/badge/dependencies-stdlib%20only-0F766E?style=flat-square)](#requisitos)
[![Local v1](https://img.shields.io/badge/scope-local%20v1-F97316?style=flat-square)](#limites-atuais)
[![Last commit](https://img.shields.io/github/last-commit/VIDORETTO/dev-skills?style=flat-square&label=last%20commit)](https://github.com/VIDORETTO/dev-skills/commits/main)

</div>

<p align="center">
  <img src="assets/hybrid-workflow.svg" alt="Fluxo do Hybrid Development Kit, da descoberta à revisão" width="100%">
</p>

O **Hybrid Development Kit** é um pacote local de skills e runtime determinístico para conduzir demandas de desenvolvimento com contexto suficiente, escopo explícito e evidência rastreável.

Ele combina contrato comportamental, linguagem de domínio, Modules/Interfaces/Seams, fatias verticais, execução por ticket, checkpoints, retomada e revisão separada de **Standards** e **Spec**.

> A regra central é simples: as skills lidam com decisões e julgamento; o runner comprova localmente o que pode ser verificado sem inventar resultado — IDs, referências, grafos, projeções, fingerprints, evidências e estado.

## Sumário

- [O que este kit resolve](#o-que-este-kit-resolve)
- [Visão geral](#visão-geral)
- [Skills](#skills)
- [Custo e eficiência: kit pesado × Hybrid](#custo-e-eficiência-kit-pesado--hybrid)
- [Instalação](#instalação)
- [Fluxo rápido](#fluxo-rápido)
- [Runner determinístico](#runner-determinístico)
- [Artefatos e fontes de verdade](#artefatos-e-fontes-de-verdade)
- [Estrutura da pasta](#estrutura-da-pasta-hybrid-spec-kit)
- [Exemplos](#exemplos)
- [Validação](#validação)
- [Medir o overhead](#medir-o-overhead)
- [Limites atuais](#limites-atuais)
- [FAQ](#faq)
- [Contribuindo](#contribuindo)
- [Proveniência](#proveniência)

## O que este kit resolve

Projetos conduzidos por conversas ou por múltiplos agentes costumam perder decisões, misturar planejamento com implementação e declarar progresso sem uma prova reproduzível. O kit cria uma trilha local para que cada etapa tenha um dono, uma fonte canônica e um próximo passo claro.

Na prática, ele ajuda a:

- transformar uma ideia vaga em contrato comportamental com `FR` e `AC` estáveis;
- registrar apenas as decisões de domínio que realmente precisam sobreviver à conversa;
- escolher módulos, interfaces e seams antes de fatiar o trabalho;
- entregar tickets verticais que podem ser executados por uma sessão nova;
- retomar um esforço por checkpoint sem depender do histórico original;
- distinguir estado do ticket de evidência de execução;
- invalidar evidências quando contrato, código ou ambiente mudam;
- revisar uma mudança em dois eixos independentes: conformidade com padrões e aderência à spec.

O pacote é local por desenho. Ele não publica, faz merge, dispara deploy ou cria um tracker remoto.

## Visão geral

Toda demanda passa primeiro pelo filtro de escopo. Só o trabalho que justifica o custo entra na cadeia de artefatos:

```text
demanda ──► filtro de escopo ──► pequena? ──► trabalho direto (0 artefatos, 0 runner)
                  │
                  ▼ sessão de planejamento
discover → domain → specify → plan → slice
                  │
                  ▼ uma sessão curta por marco (até 3 tickets)
next ──► implement (red → green) ──► evidence run ──► review do marco ──► done
  ▲                                                                    │
  └──────────────── checkpoint + prompt de continuação ◄───────────────┘
```

`verify` e `check` ficam fora do caminho normal: entram para evidência obsoleta, procedimentos manuais ou externos e auditorias.

Cada passagem responde a uma pergunta diferente:

| Etapa | Pergunta | Resultado principal |
| --- | --- | --- |
| Descoberta | Qual problema vale resolver agora? | contexto, limites, hipóteses e decisões |
| Domínio | Que linguagem e regras precisam permanecer consistentes? | vocabulário e ADRs seletivos |
| Especificação | Como saberemos que o comportamento está correto? | `spec.md` ou `change.md` com `FR`/`AC` |
| Planejamento | Onde a mudança deve entrar e como será verificada? | `plan.md`, módulos, seams, riscos e comandos |
| Fatiamento | Qual é a primeira entrega vertical executável? | tickets com dependências e pacote completo |
| Check | Os artefatos convergem? | consistência, grafo, prontidão e reconciliação |
| Implementação | Qual comportamento será entregue agora? | código mínimo e estado honesto do ticket |
| Verificação | O comportamento foi realmente observado? | evidência executada pelo runner (`evidence run`) |
| Revisão | A mudança respeita padrões e contrato? | relatório separado de Standards e Spec |

## Skills

As dez skills são instaladas como pastas com `SKILL.md` e são acionadas só pelo usuário: `/hybrid-start` no Claude Code ou `$hybrid-start` no Codex. Cada skill traz `agents/openai.yaml` com `allow_implicit_invocation: false`, então o Codex não as carrega sozinho.

### Quando não usar

O kit tem custo fixo: cada instrução extra vira passos e tokens (veja [Custo e eficiência](#custo-e-eficiência-kit-pesado--hybrid)). Por isso `hybrid-start` aplica primeiro um filtro de escopo. O kit é usado apenas quando pelo menos uma destas condições vale:

1. o trabalho atravessa mais de uma sessão ou vai para outro agente ou modelo;
2. envolve vários comportamentos ou módulos, persistência, contrato público, migração ou concorrência;
3. a ambiguidade é grande o bastante para um palpite errado gerar retrabalho;
4. é preciso evidência rastreável de aceite.

Correção de texto, docs ou configuração, função com comportamento conhecido, bug de correção óbvia, refatoração num único arquivo ou qualquer coisa que caiba numa sessão com cerca de 20 chamadas é **trabalho direto**: sem artefatos, sem runner, sem skills hybrid.

| Rota | Orçamento |
| --- | --- |
| Direta | 0 artefatos, 0 chamadas ao runner |
| Compacta | `change.md` + `evidence run`; no máximo 2 chamadas; sem verify/review separados |
| Padrão | sessão de planejamento + uma sessão curta por marco; até 3 chamadas ao runner por ticket |

| Skill | Responsabilidade |
| --- | --- |
| [`hybrid-start`](skills/hybrid-start/SKILL.md) | Faz reconhecimento, classifica a demanda e retoma esforços existentes. |
| [`hybrid-discover`](skills/hybrid-discover/SKILL.md) | Registra problema, consumidor, limites, hipóteses, evidências e decisões materiais. |
| [`hybrid-domain`](skills/hybrid-domain/SKILL.md) | Mantém vocabulário, contexto e ADRs apenas quando uma decisão precisa sobreviver. |
| [`hybrid-specify`](skills/hybrid-specify/SKILL.md) | Escreve o contrato comportamental e os critérios de aceitação versionados. |
| [`hybrid-plan`](skills/hybrid-plan/SKILL.md) | Mapeia módulos, interfaces, consumidores, seams, riscos e verificação técnica. |
| [`hybrid-slice`](skills/hybrid-slice/SKILL.md) | Converte o contrato em tickets verticais prontos para uma sessão nova. |
| [`hybrid-check`](skills/hybrid-check/SKILL.md) | Analisa consistência, convergência, blockers, projeções e prontidão. |
| [`hybrid-implement`](skills/hybrid-implement/SKILL.md) | Executa um ticket com comportamento primeiro, mudança mínima e checkpoint. |
| [`hybrid-verify`](skills/hybrid-verify/SKILL.md) | Reverifica evidência obsoleta, procedimentos manuais/externos e gates de entrega; o caminho normal registra evidência no `implement`. |
| [`hybrid-review`](skills/hybrid-review/SKILL.md) | Faz revisão fixa em dois eixos: Standards e Spec, sem corrigir silenciosamente. |

## Custo e eficiência: kit pesado × Hybrid

Esta seção resume o estudo feito antes da otimização do kit. A análise completa, com premissas e o modelo de custo, está em [`docs/comparative-review.md`](docs/comparative-review.md).

### O que gera custo num agente

Cada turno reenvia o contexto inteiro. Os tokens cobrados são aproximadamente **nº de turnos × contexto médio**, e o tempo depende principalmente do nº de turnos. Daí saem três alavancas, em ordem de impacto:

1. **Turnos extras.** Toda instrução do tipo "leia X", "rode Y" ou "registre Z" vira pelo menos uma chamada, e o agente obedece.
2. **Comprimento da sessão.** O custo cresce de forma quadrática com o nº de turnos. Sessões curtas, que partem de um pacote pequeno, custam menos que uma sessão longa.
3. **Texto lido cedo.** O que entra no turno 2 é reenviado em todos os turnos seguintes. Com cache sai mais barato, mas ainda ocupa a janela.

### O que a pesquisa mostra

| Fonte | Achado |
| --- | --- |
| ETH Zurich, *Evaluating AGENTS.md* (ICLR 2026) | Arquivos de contexto escritos por desenvolvedores melhoraram o sucesso em ~4% e aumentaram o custo em até 19%. Os gerados por LLM reduziram o sucesso em ~3%, aumentaram o custo em mais de 20% e acrescentaram ~4 passos por tarefa. A causa: instruções que pedem mais exploração e mais testes, e os agentes seguem. |
| Spec Kit × OpenSpec, mesma tarefa | 120.947 contra 57.740 tokens no total (+109%). Só o planejamento: 96.298 contra 38.117 (+152%). Implementação: 84.742 contra 53.612 (+58%). |
| Anthropic, skills e cache | Antes de ser acionada, uma skill custa só o frontmatter (~100 tokens); o corpo entra quando ela é invocada. Tokens em cache custam 10% da entrada normal. |
| Matt Pocock, *smart zone* | O modelo raciocina bem até cerca de 150 mil tokens de contexto. A troca de sessão deve acontecer numa fronteira de fase. |

### Kit pesado × Hybrid otimizado

O "kit pesado" é o padrão encontrado no Spec Kit e na primeira versão deste próprio kit, medida antes da otimização.

| Aspecto | Kit pesado | Hybrid otimizado |
| --- | --- | --- |
| Pedido pequeno | passa por todas as fases | filtro de escopo: trabalho direto, sem artefatos nem runner |
| Leitura obrigatória na rota compacta | ~11–13 mil tokens (5 skills + referências) | ~1,5 mil tokens (`hybrid-start` + `hybrid-implement`) |
| Entrada de uma sessão | 4 chamadas (`start`, `invalidate`, `session`, `package`), ~2,4 mil tokens de saída | 1 chamada (`next`), ~360 tokens |
| Execução dos testes | no `implement` e de novo no `verify` | uma vez, gravada por `evidence run` |
| Evidência | declarada pelo agente (`--executed`) | observada pelo runner (`exit_code`, duração, hash) |
| Revisão | 5 comandos git, por ticket | 1 comando, por marco, eixos em subagentes |
| Ticket | 11 seções, ~670 tokens | 4 seções obrigatórias, ~370 tokens |
| Política de sessão | 1.540 tokens; renova com 60% da janela (600 mil numa janela de 1M) | ~395 tokens; renova por ticket ou ~100 mil tokens |
| Texto das 10 skills | ~32 mil caracteres, com seções repetidas | ~21,5 mil caracteres (−33%), referências sob demanda |

### Estimativa de overhead contra o uso sem skill

Isto é um **modelo, não uma medição**. Premissas: prompt de sistema de 15 mil tokens; tarefa pequena com 12 turnos e média com 70 turnos.

| Cenário | Kit pesado | Hybrid otimizado |
| --- | --- | --- |
| Tarefa pequena | ~+400% de tokens, ~3× os turnos | 0% (trabalho direto) ou ~+25% na rota compacta |
| Tarefa média | ~+150% numa sessão longa | ~−7% (sessão de plano + 3 sessões curtas de execução) |

Conclusões:

- **Abaixo de 10% é viável em tarefas médias e grandes**, e o kit pode até ficar abaixo do uso sem skill, porque divide o trabalho em sessões curtas.
- **Em tarefas pequenas, o único overhead aceitável é zero**, e por isso elas não entram no kit.
- O número real vem de [`scripts/bench_ab.py`](#medir-o-overhead), comparando o custo por tarefa concluída.

### Fontes

- ETH Zurich SRI Lab, [*Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?*](https://arxiv.org/abs/2602.11988) (ICLR 2026). Resumos em [InfoQ](https://infoq.com/news/2026/03/agents-context-file-value-review/) e [agentpatterns.ai](https://agentpatterns.ai/instructions/evaluating-agents-md-context-files/).
- [*Is your "safe choice" burning your budget?*](https://medium.com/it-chronicles/is-your-safe-choice-burning-your-budget-1cfddf8782e4), comparação de tokens entre Spec Kit e OpenSpec.
- Anthropic, [*Harnessing Claude's intelligence*](https://claude.com/blog/harnessing-claudes-intelligence), sobre contexto por turno e cache.
- [*Reduce AI token usage with progressive disclosure*](https://chudi.dev/blog/reduce-ai-token-usage-progressive-disclosure).
- Matt Pocock, [`skills/engineering`](https://github.com/mattpocock/skills/tree/main/skills/engineering) (`ask-matt`, fronteiras de fase e *smart zone*) e [`skills/productivity`](https://github.com/mattpocock/skills/tree/main/skills/productivity) (`writing-for-agents`).
- GitHub, [Spec Kit](https://github.com/github/spec-kit) v1.1.0.

## Instalação

### Requisitos

- Python 3.10 ou posterior;
- Git é opcional, mas permite registrar o SHA usado como baseline;
- nenhuma dependência externa para executar o runner.

### Validar este pacote

```powershell
git clone https://github.com/VIDORETTO/dev-skills.git
cd dev-skills/hybrid-spec-kit

python scripts/hybrid.py package-validate --json
python -m unittest discover -s tests -v
```

### Instalar em um projeto existente

Partindo da pasta `hybrid-spec-kit` deste repositório:

```powershell
python scripts/hybrid.py install `
  --project C:\caminho\do\projeto `
  --json
```

Por padrão, as skills vão para a primeira raiz existente entre `.agents/skills`, `.claude/skills`, `.cursor/skills` e `.github/skills`; sem nenhuma delas, para `.agents/skills`. Para o Claude Code, use `--skill-root .claude/skills`:

```powershell
python scripts/hybrid.py install `
  --project C:\caminho\do\projeto `
  --skill-root .claude/skills `
  --json
```

O comando também instala:

- referências compartilhadas em `.agents/shared`;
- uma cópia das referências em `.hybrid/shared`;
- o runner em `.hybrid/hybrid.py`.

Arquivos diferentes já existentes geram conflito e são preservados. Use `--force` somente depois de revisar o inventário produzido pela instalação.

## Fluxo rápido

### 1. Inicialize o projeto adotado

```powershell
python .hybrid/hybrid.py init `
  --project . `
  --mode standard `
  --json
```

O modo `standard` separa contrato, plano, tickets e evidências. Para uma mudança pequena e conhecida, use o modo `compact`, que mantém contrato, plano breve, tarefas e limitações em um único `change.md`.

### 2. Crie um esforço

```powershell
python .hybrid/hybrid.py scaffold `
  --project . `
  --effort 014-reserva-estoque `
  --title "Reserva de estoque" `
  --json
```

Depois de preencher o contrato, valide e gere as visões:

```powershell
python .hybrid/hybrid.py validate `
  --project . `
  --effort 014-reserva-estoque `
  --json

python .hybrid/hybrid.py graph `
  --project . `
  --effort 014-reserva-estoque `
  --json

python .hybrid/hybrid.py render `
  --project . `
  --effort 014-reserva-estoque `
  --view all `
  --json
```

### 3. Execute um ticket com três chamadas

```powershell
# entrada única: registra insumos, invalida evidência obsoleta, escolhe o ticket e checa prontidão
python .hybrid/hybrid.py next --project . --effort 014-reserva-estoque --write --json

python .hybrid/hybrid.py ticket update --project . --effort 014-reserva-estoque `
  --ticket TK-001 --status in_progress --json

# o runner executa o comando, grava a evidência e avança o ticket para verified
python .hybrid/hybrid.py evidence run --project . --effort 014-reserva-estoque `
  --ticket TK-001 --acceptance-refs AC-001 `
  --command "python -m pytest tests/stock/test_reservation.py -q" `
  --path src/stock --path tests/stock --json
```

O `next` devolve um pacote pequeno: caminho do ticket, aceites, erros, bloqueios e comando de validação. Ele substitui `start` + `invalidate` + `session` + `package`. O `evidence run` registra `exit_code`, duração e hash da saída; em caso de falha, devolve só as últimas linhas. `evidence add --executed` continua disponível para procedimentos manuais ou externos, e nesse caso é uma declaração do agente.

### 4. Feche o marco com revisão

Depois do `hybrid-review` do marco, cada ticket é fechado numa chamada:

```powershell
python .hybrid/hybrid.py ticket update --project . --effort 014-reserva-estoque `
  --ticket TK-001 --status done --review passed --json
```

`done` exige evidência atual aprovada para todos os aceites e `review_status: passed`. O runner recusa transições de `draft`/`blocked` para estados de entrega e não reabre `cancelled`/`superseded`.

## Goals limitados e continuação

Use uma sessão de planejamento para fixar contrato/plano/tickets e sessões novas para executar os próximos marcos. Um pedido de concluir o projeto inteiro segue pelo checkpoint, sem repetir descoberta nem ampliar requisitos a cada continuação.

```text
python .hybrid/hybrid.py session --project . --effort 014-reserva-estoque --write --json
```

O comando sugere até três tickets relacionados, prioriza o ticket ativo e grava `.hybrid/continuations/<effort>.md` com um prompt curto para a próxima sessão. Verifique a prontidão antes de editar; a sugestão não altera `state.json` nem aprova evidência. O agente troca de sessão na fronteira de um ticket ou perto de 100 mil tokens de contexto, entrega trabalho parcial honestamente e evita compactações planejadas.

A primeira contagem observada de tickets vira baseline. Para uma migração cuja quantidade original seja conhecida, forneça `--baseline-tickets <n>` uma vez. Crescimento acima de 20% exige reconciliar causas antes de mais expansão; defeitos necessários e IDs existentes são preservados. Correções do aceite permanecem no ticket quando válido, e melhorias opcionais ficam no backlog.

Os limites orientam o agente: o runner não monitora tempo/contexto, cria Goals, interrompe processos ou abre sessões. A entrega parcial só encerra um Goal se essa alternativa estiver prevista no seu objetivo; um Goal antigo global não é declarado concluído artificialmente. Veja a [política de execução limitada](shared/references/bounded-execution.md) e o [uso operacional](docs/usage.md).

## Runner determinístico

O arquivo [`scripts/hybrid.py`](scripts/hybrid.py) usa somente a biblioteca padrão do Python. Ele não tenta substituir o julgamento das skills: sua função é manter invariantes locais e produzir saídas reproduzíveis.

| Comando | O que comprova |
| --- | --- |
| `install` | cópia local, raiz de skills, referências, runtime e conflitos |
| `init` | configuração, modo de trabalho e checkpoint inicial |
| `scaffold` | estrutura mínima de um esforço padrão ou compacto |
| `validate` | frontmatter, IDs, referências, campos, caminhos e regras do esforço |
| `graph` | dependências, ciclos, fronteira executável e sobreposição de áreas |
| `render` | projeções derivadas como `todo.md`, `backlog.md` e `verification.md` |
| `next` | entrada única: insumos, evidência obsoleta, próximo ticket e prontidão, em saída curta |
| `package` | prontidão completa do pacote entregue a uma executora |
| `ticket update` | transição de estado validada; `done` exige evidência e `--review passed` |
| `evidence run` | executa o comando, registra exit code, fingerprint e avança o ticket |
| `evidence add` | evidência declarada para procedimentos manuais ou externos |
| `start` | rota de retomada, baseline, inputs atuais e próxima ação |
| `session` | sugestão de marco limitado, baseline de tickets e continuação protegida; não comprova prontidão |
| `invalidate` | evidências e dependentes potencialmente obsoletos |
| `check` | consistência ou convergência dos artefatos |
| `dedupe` | lacunas repetidas por chave estável |
| `checkpoint write` | posição, revisão, inputs canônicos e próxima ação |
| `package-validate` | integridade do pacote distribuível completo |

Checkpoints usam escrita atômica e `--expected-revision` para detectar escrita concorrente. O runner registra SHA quando há commits; sem Git, usa fingerprint do inventário.

Mais detalhes operacionais estão em [`docs/usage.md`](docs/usage.md).

## Artefatos e fontes de verdade

O kit diferencia arquivos que devem ser editados de arquivos que apenas refletem o estado canônico.

| Contexto | Fonte canônica | Projeções ou estado |
| --- | --- | --- |
| Esforço padrão | `spec.md`, `plan.md` e `tickets/*.md` | `todo.md`, `backlog.md`, `verification.md` |
| Mudança compacta | `change.md` | evidência associada ao esforço |
| Estado operacional | `state.json` | posição, revisão, baseline, inputs e próxima ação |
| Runtime instalado | `.hybrid/config.json` e `.hybrid/hybrid.py` | `.hybrid/shared` e `.hybrid/generated.json` |

Regra prática: corrija a fonte proprietária e regenere a projeção. Não mantenha `todo.md`, `backlog.md` ou `verification.md` como listas concorrentes.

## Estrutura da pasta `hybrid-spec-kit`

```text
.
├── assets/
│   └── hybrid-workflow.svg       # visão visual do fluxo
├── docs/
│   ├── comparative-review.md     # estudo: Spec Kit, Matt Pocock, custo em tokens
│   ├── evaluation.md             # interpretação e matriz E01–E31
│   ├── sources.md                # proveniência e adaptações
│   ├── usage.md                  # operação detalhada
│   └── validation-report.md      # registro reproduzível das validações
├── examples/
│   ├── compact/                  # exemplo com change.md
│   ├── evaluation/              # casos comportamentais
│   └── standard/                 # exemplo com spec, plan e tickets
├── scripts/
│   ├── bench_ab.py               # benchmark A/B com e sem o kit
│   └── hybrid.py                 # runtime determinístico local
├── shared/
│   ├── references/               # contratos de operação e vocabulário
│   ├── schemas/                  # schemas JSON
│   └── templates/                # templates de artefatos
├── skills/                       # dez skills (SKILL.md + agents/openai.yaml)
└── tests/
    ├── test_bench.py             # harness A/B com claude falso
    ├── test_lean.py              # next, evidence run, gates, instalação
    ├── test_runner.py            # testes do runtime e fixtures
    └── test_session.py           # marcos, dependências e continuação
```

## Exemplos

| Exemplo | Demonstra | Entrada principal |
| --- | --- | --- |
| [`standard/reserva-estoque`](examples/standard/reserva-estoque/README.md) | contrato, plano, tickets, grafo, pacote e checkpoint | `specs/014-reserva-estoque/` |
| [`compact/limite-desconto`](examples/compact/limite-desconto/README.md) | mudança proporcional sem tickets paralelos | `specs/002-limite-desconto/change.md` |
| [`evaluation`](examples/evaluation/README.md) | cenários para avaliação comportamental | `examples/evaluation/cases.json` |

Comandos para explorar os exemplos:

```powershell
python scripts/hybrid.py validate `
  --project examples/standard/reserva-estoque `
  --effort 014-reserva-estoque `
  --json

python scripts/hybrid.py graph `
  --project examples/standard/reserva-estoque `
  --effort 014-reserva-estoque `
  --json

python scripts/hybrid.py render `
  --project examples/standard/reserva-estoque `
  --effort 014-reserva-estoque `
  --view all `
  --json

python scripts/hybrid.py validate `
  --project examples/compact/limite-desconto `
  --effort 002-limite-desconto `
  --json
```

Os caminhos de código nos exemplos são deliberadamente ilustrativos. Eles mostram o protocolo do kit, não uma aplicação pronta para produção.

## Validação

Valide o pacote antes de distribuí-lo:

```powershell
python scripts/hybrid.py package-validate --json
python -m unittest discover -s tests -v
```

`package-validate` verifica as dez skills, frontmatter, tamanho, links relativos, schemas e compilação do runner. A suíte (49 testes) exercita o runtime em workspaces temporários: instalação, validação, grafos, projeções, checkpoints, evidências, `next`, `evidence run`, transições e gate de revisão, deduplicação, configuração e o harness A/B.

O estado de cada execução, a revisão testada e suas limitações ficam em [`docs/validation-report.md`](docs/validation-report.md). A matriz E01–E31 em [`docs/evaluation.md`](docs/evaluation.md) separa checks determinísticos de avaliação comportamental por modelo.

## Medir o overhead

A meta é que, em tarefas que passam no filtro de escopo, o kit custe no máximo 10% a mais que o uso sem skill, medido como custo por tarefa concluída. Para medir:

```bash
python scripts/bench_ab.py --tasks tasks.json --runs 3 --out bench-out \
  --claude-args "--permission-mode acceptEdits"
```

Cada tarefa (`id`, `repo` de template, `prompt`, `check`) roda nos braços `baseline` e `hybrid`, intercalados. O script grava `runs.jsonl` e `summary.json`, com medianas de turnos, duração e tokens, além do custo por sucesso. A execução consome uso real do modelo: comece com uma tarefa e `--runs 1`.

## Limites atuais

Esta versão trabalha localmente e não inclui:

- adapter para tracker remoto;
- preset específico de Spec Kit;
- motor genérico de workflows;
- GUI;
- publicação, merge ou deploy;
- instalação global ou alteração de configurações pessoais;
- medição real de overhead já executada: o harness existe, mas ainda não foi rodado com modelo;
- execução de serviços externos pelo runner.

Consultas de documentação atual para bibliotecas, SDKs, APIs, CLIs e serviços ficam a cargo de `hybrid-plan` por meio do Context7 quando essa capacidade estiver disponível.

## FAQ

### O kit é um agente autônomo?

Não. As skills orientam decisões, leitura, planejamento e revisão. O runner é um runtime determinístico local; ele não inventa decisões nem considera um ticket concluído apenas porque seu status foi alterado.

### Quando usar `standard` ou `compact`?

Use `compact` para uma função, regra ou correção pequena, com contrato e plano que cabem em um único `change.md`. Use `standard` quando houver múltiplos artefatos, dependências, tickets, handoff entre sessões ou risco de reconciliação.

### Posso editar as projeções geradas?

Não como fonte de verdade. Edite contrato, plano, tickets ou `change.md` e rode `render` novamente. Se uma projeção foi alterada manualmente, o runner sinaliza conflito para que a edição seja reconciliada.

### Uma evidência `passed` prova que o produto está pronto?

Não. Ela prova somente o procedimento executado, os caminhos observados, a revisão testada e o resultado registrado. Critérios de entrega, revisão e métricas pós-uso continuam sendo gates distintos.

## Contribuindo

Antes de abrir uma mudança:

1. rode `package-validate` e a suíte de testes;
2. preserve a separação entre artefatos canônicos e projeções;
3. não transforme uma decisão semântica em detalhe silencioso de implementação;
4. atualize exemplos e documentação quando um comando ou invariável mudar;
5. registre limitações de validação em vez de promover observação não executada a sucesso.

Para mudanças que alteram comportamento do protocolo, atualize também os schemas, templates, fixtures ou casos de avaliação afetados.

## Proveniência

O pacote foi adaptado da arquitetura local `ARQUITETURA-HIBRIDA-SKILLS.md` 1.2, combinando ideias do [Spec Kit](https://github.com/github/spec-kit) (artefatos separados, IDs, análise de consistência e convergência) e das [skills de Matt Pocock](https://github.com/mattpocock/skills) (entrevista em rodadas, glossário/ADR, seams, fatias verticais, TDD, revisão em dois eixos, diagnóstico de bug). As decisões e adaptações estão em [`docs/sources.md`](docs/sources.md) e a comparação com os dois kits em [`docs/comparative-review.md`](docs/comparative-review.md).

**Estado atual:** v1 local otimizada para custo. Validação determinística verde; avaliação comportamental e medição A/B de overhead ainda pendentes de execução com modelo.
