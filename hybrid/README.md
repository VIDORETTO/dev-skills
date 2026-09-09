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
- [Instalação](#instalação)
- [Fluxo rápido](#fluxo-rápido)
- [Runner determinístico](#runner-determinístico)
- [Artefatos e fontes de verdade](#artefatos-e-fontes-de-verdade)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Exemplos](#exemplos)
- [Validação](#validação)
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

O fluxo padrão percorre uma cadeia curta de artefatos canônicos:

```text
demanda
  │
  ▼
discover → domain → specify → plan → slice → check
                                                    │
                                                    ▼
                                            implement → verify → review
                                                    │
                                                    ▼
                                           checkpoint + evidência
                                                    │
                                                    └──→ start / resume
```

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
| Verificação | O comportamento foi realmente observado? | evidência executada, revisão e limitações |
| Revisão | A mudança respeita padrões e contrato? | relatório separado de Standards e Spec |

## Skills

As dez skills são instaladas como pastas com `SKILL.md` e podem ser chamadas explicitamente com `$nome-da-skill`.

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
| [`hybrid-verify`](skills/hybrid-verify/SKILL.md) | Executa os procedimentos reais e registra evidências atuais e suas limitações. |
| [`hybrid-review`](skills/hybrid-review/SKILL.md) | Faz revisão fixa em dois eixos: Standards e Spec, sem corrigir silenciosamente. |

## Instalação

### Requisitos

- Python 3.10 ou posterior;
- Git é opcional, mas permite registrar o SHA usado como baseline;
- nenhuma dependência externa para executar o runner.

### Validar este pacote

```powershell
git clone https://github.com/VIDORETTO/dev-skills.git
cd dev-skills/hybrid

python scripts/hybrid.py package-validate --json
python -m unittest discover -s tests -v
```

### Instalar em um projeto existente

Partindo da pasta `hybrid` deste repositório:

```powershell
python scripts/hybrid.py install `
  --project C:\caminho\do\projeto `
  --json
```

Por padrão, as dez skills são copiadas para `.agents/skills`. Para projetos que usam outra convenção:

```powershell
python scripts/hybrid.py install `
  --project C:\caminho\do\projeto `
  --skill-root .cursor/skills `
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

### 3. Prepare e execute um ticket

```powershell
python .hybrid/hybrid.py package `
  --project . `
  --effort 014-reserva-estoque `
  --ticket TK-001 `
  --json

python .hybrid/hybrid.py ticket update `
  --project . `
  --effort 014-reserva-estoque `
  --ticket TK-001 `
  --status in_progress `
  --json
```

O primeiro comando verifica se a sessão recebeu contrato, plano, referências atuais, blockers satisfeitos e todos os campos necessários. O segundo atualiza estado; ele não substitui uma prova de execução.

### 4. Registre evidência

```powershell
python .hybrid/hybrid.py evidence add `
  --project . `
  --effort 014-reserva-estoque `
  --ticket TK-001 `
  --acceptance-refs AC-001 `
  --procedure "python -m pytest tests/stock/test_reservation.py -q" `
  --result passed `
  --executed `
  --path src/stock `
  --path tests/stock `
  --observations "resultado observado" `
  --json
```

Resultados `passed`, `failed` e `partial` exigem `--executed` e ao menos um caminho existente. Quando o ambiente impede a execução, use `not_run` e registre a limitação concreta.

### 5. Retome e reconcilie

```powershell
python .hybrid/hybrid.py start `
  --project . `
  --effort 014-reserva-estoque `
  --json

python .hybrid/hybrid.py invalidate `
  --project . `
  --effort 014-reserva-estoque `
  --json

python .hybrid/hybrid.py check `
  --project . `
  --effort 014-reserva-estoque `
  --mode convergence `
  --json
```

Alterações em contrato, plano, código sob teste ou ambiente podem tornar evidências antigas obsoletas. O runner identifica a divergência; a classificação semântica continua sendo uma decisão do fluxo.

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
| `package` | prontidão do pacote entregue a uma executora |
| `ticket update` | transição explícita de estado do ticket |
| `evidence add` | procedimento, execução, caminhos, fingerprint, revisão e limitações |
| `start` | rota de retomada, baseline, inputs atuais e próxima ação |
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

## Estrutura da pasta `hybrid`

```text
.
├── assets/
│   └── hybrid-workflow.svg       # visão visual do fluxo
├── docs/
│   ├── evaluation.md             # interpretação e matriz E01–E31
│   ├── sources.md                # proveniência e adaptações
│   ├── usage.md                  # operação detalhada
│   └── validation-report.md      # registro reproduzível das validações
├── examples/
│   ├── compact/                  # exemplo com change.md
│   ├── evaluation/              # casos comportamentais
│   └── standard/                 # exemplo com spec, plan e tickets
├── scripts/
│   └── hybrid.py                 # runtime determinístico local
├── shared/
│   ├── references/               # contratos de operação e vocabulário
│   ├── schemas/                  # schemas JSON
│   └── templates/                # templates de artefatos
├── skills/                       # dez skills distribuíveis
└── tests/
    └── test_runner.py            # testes do runtime e fixtures
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

`package-validate` verifica as dez skills, frontmatter, tamanho, links relativos, schemas e compilação do runner. A suíte de testes exercita o runtime em workspaces temporários, incluindo instalação, validação, grafos, projeções, checkpoints, evidências, gates, deduplicação e configuração.

O estado de cada execução, a revisão testada e suas limitações ficam em [`docs/validation-report.md`](docs/validation-report.md). A matriz E01–E31 em [`docs/evaluation.md`](docs/evaluation.md) separa checks determinísticos de avaliação comportamental por modelo.

## Limites atuais

Esta versão trabalha localmente e não inclui:

- adapter para tracker remoto;
- preset específico de Spec Kit;
- motor genérico de workflows;
- GUI;
- publicação, merge ou deploy;
- instalação global ou alteração de configurações pessoais;
- medição comparativa de custo, economia ou superioridade;
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

O pacote foi adaptado da arquitetura local `ARQUITETURA-HIBRIDA-SKILLS.md` 1.2, com referências preservadas a `spec-kit` e `mattpocock-skills-filtered`. As decisões, contribuições e adaptações estão documentadas em [`docs/sources.md`](docs/sources.md).

**Estado atual:** v1 local, com avaliação determinística preparada e avaliação comportamental ainda dependente de um modelo/contexto autorizado para executar os casos.
