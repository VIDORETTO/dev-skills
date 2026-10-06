# Revisão comparativa: Hybrid × Spec Kit × Matt Pocock skills

Data: 2026-10-06. Revisão avaliada: `4f89771` (branch `claude/vigilant-clarke-0ndr1f`).
Referências consultadas: `github/spec-kit` em `2dda047` (v1.1.0, 2026-10-02) e `mattpocock/skills` (`main`, pastas `skills/engineering` e `skills/productivity`).

## Veredito

O Hybrid é sólido no que o diferencia: rastreabilidade `FR`/`AC` → ticket → evidência, invalidação por fingerprint, projeções geradas e retomada por checkpoint. Isso vai além do Spec Kit (que não tem evidência nem invalidação) e do Matt (que não tem estado persistido). `package-validate` passa e os 32 testes passam.

Os problemas estão em três frentes: (1) o runner aceita estados que o próprio `validate` rejeita; (2) a instalação e a invocação foram pensadas para Codex e ficam frágeis no Claude Code; (3) faltam peças que os outros dois kits já resolveram bem: diagnóstico de bug, entrevista estruturada, revisão em subagentes isolados e constituição do projeto.

## 1. Problemas encontrados

### Confirmados por execução

| # | Severidade | Problema | Como reproduzir |
| --- | --- | --- | --- |
| P1 | Alta | `ticket update` permite `ready → done` direto, sem passar por `in_progress/implemented/verified`, sem revisão e deixando `verification_status: not_run`. O `validate` seguinte falha com `done ticket must have verification_status=passed`. O runner grava um estado que ele mesmo considera inválido. | Exemplo `reserva-estoque`: `evidence add` para AC-001 e AC-004 e depois `ticket update --ticket TK-001 --status done`. |
| P2 | Alta | O gate de revisão de `done` (`operating-contract.md`, `hybrid-verify`) não existe no runner. Não há registro de revisão (`RV-xxx` ou campo `review_status`) que o comando consulte. | `grep review scripts/hybrid.py`: só aparece como fase e como warning. |
| P3 | Média | `--executed` é autodeclarado. `--procedure "echo nunca rodou" --result passed --executed` é aceito. A evidência é uma declaração, não uma prova, mas o README diz que o runner "comprova". | Mesmo cenário de P1. |
| P4 | Média | `detect_skill_root` só conhece `.agents/skills`, `.cursor/skills` e `.github/skills`. O Claude Code lê `.claude/skills`, então uma instalação padrão fica invisível nele. `package-validate` no projeto instalado também ignora `.claude/skills`. | `scripts/hybrid.py:2188` e `:2278`. |

### Riscos de desenho

| # | Severidade | Risco |
| --- | --- | --- |
| R1 | Alta | **Invocação.** As 10 skills têm `disable-model-invocation: true`, que é uma chave só do Claude Code. No Codex, que é o alvo implícito (sintaxe `$skill`, `.agents/skills`), ela é ignorada. O Matt resolve com `agents/openai.yaml` (`policy.allow_implicit_invocation: false`). No Claude Code acontece o contrário: o modelo não consegue acionar `hybrid-verify` ou `hybrid-review` sozinho, mas `bounded-execution.md` espera que um Goal percorra implement → verify → review sem intervenção. |
| R2 | Média | **Limites 30 min / 60% de contexto.** Na maioria dos harnesses o agente não sabe quanto contexto já usou. Além disso, 60% de uma janela de 1M são 600k tokens, muito acima da faixa em que o modelo ainda raciocina bem (~150k, que o Matt chama de *smart zone*). A regra "nenhuma compactação planejada" contradiz a prática do Matt, em que `/compact` numa fronteira de fase é o padrão. Sugestão: expressar o limite em tokens absolutos ou em fronteiras de fase. |
| R3 | Média | **"Goal" não é definido.** O termo parece vir de um recurso de harness, provavelmente do Codex. No Claude Code não existe equivalente direto, e quatro skills e uma referência dependem dele. |
| R4 | Média | **Gates G1/G2/G3** aparecem em `specify`, `plan`, `slice` e no template de plano, mas não estão definidos em `vocabulary.md` nem em `operating-contract.md`. Não há G4 para revisão e entrega. |
| R5 | Média | **Constituição citada e inexistente.** `operating-contract.md` diz que "Constituição e instruções do repositório delimitam o trabalho", mas não há template nem skill para criá-la. No Spec Kit ela é o primeiro passo. |
| R6 | Média | **Revisão num único contexto.** `hybrid-review` faz Standards e Spec no mesmo contexto. O Matt roda cada eixo num subagente para que um não contamine o outro. O caso E30 ("mesma IA nos dois papéis") continua pendente. |
| R7 | Baixa | **Sedimento.** Toda skill termina com uma seção extra ("Milestone boundary", "Session efficiency", "Review a milestone once"...) que repete `bounded-execution.md`. O commit `4f89771` adicionou as dez de uma vez. É duplicação: muda-se a política em 11 lugares. |
| R8 | Baixa | **Idiomas misturados.** Os `SKILL.md` estão em inglês; referências, templates e docs, em português. Os termos divergem (ticket/fatia, finding/achado/lacuna). |
| R9 | Baixa | **Nomenclatura do Matt defasada.** O Hybrid usa `CONTEXT.md`/`CONTEXT-MAP.md`, mas o Matt atual usa `GLOSSARY.md`/`GLOSSARY-MAP.md`. Quem instalar os dois kits terá dois glossários. |
| R10 | Baixa | **`<package-root>` ambíguo depois da instalação.** O runner instalado fica em `.hybrid/hybrid.py`, não em `<package-root>/scripts/hybrid.py`. Só `hybrid-start` menciona o equivalente; as outras nove deixam o agente adivinhar. |
| R11 | Baixa | **Cópia duplicada.** `install` copia `shared/` duas vezes (`<skill-root>/../shared` e `.hybrid/shared`), o que abre espaço para divergência. |
| R12 | Baixa | **Proveniência inverificável.** `docs/sources.md` cita `ARQUITETURA-HIBRIDA-SKILLS.md`, `spec-kit/` e `mattpocock-skills-filtered/` como cópias locais que não estão no repositório. |
| R13 | Info | **Peso.** São 10 skills, um runner de 2,5 mil linhas, 8 schemas e cerca de 15 comandos. O modo compacto mitiga, mas uma mudança média ainda passa por 6 a 8 invocações manuais. O risco é o usuário pular etapas e deixar o estado inconsistente, o que leva de volta a P1. |

## 2. Comparação com o Spec Kit (v1.1.0)

| Spec Kit | Hybrid | Avaliação |
| --- | --- | --- |
| `/constitution` | ausente (R5) | **Lacuna.** Adotar um template curto de princípios e gates. |
| `/specify` | `hybrid-specify` | Equivalente. O Hybrid tem IDs estáveis, revisão e modo compacto, o que é melhor. |
| `/clarify` (taxonomia de ambiguidade em ~10 categorias, no máximo 5 perguntas, respostas gravadas em `## Clarifications` na spec) | `hybrid-discover` (impacto × incerteza) | **Adotar a taxonomia** como checklist de cobertura em `hybrid-specify`, e gravar as respostas na spec. |
| `/checklist` ("testes unitários para o texto dos requisitos", pertence ao revisor, o agente nunca marca `[x]`) | ausente | **Lacuna útil.** Pode virar um modo `requirements` em `hybrid-check`. |
| `/plan` | `hybrid-plan` | O Hybrid é mais forte: seams, oráculos, Context7, comandos observados versus executados. |
| `/tasks` (fases por user story, marcador `[P]`) | `hybrid-slice` + `graph` | O Hybrid é melhor: grafo real, `owned_areas` e fronteira. |
| `/analyze` | `hybrid-check --mode consistency` | Equivalente. |
| `/converge` (só acrescenta tarefas a `tasks.md`) | `hybrid-check --mode convergence` + dedupe | O Hybrid é melhor por deduplicar e reaproveitar ticket aberto. |
| `/implement` | `hybrid-implement` | Equivalente. O Hybrid acrescenta pacote, checkpoint e retorno à planejadora. |
| `/taskstoissues`, extensão `github` | fora de escopo | Decisão consciente da v1. |
| Hooks `before_*`/`after_*`, extensões, presets, workflows, bundles (`bugfix`, `assess`) | ausente | Não vale copiar o sistema de extensões. **Vale** a ideia do bundle `bugfix` (ver *diagnosing-bugs* abaixo). |
| Integração com 30+ agentes | `.agents`, `.cursor`, `.github` | Falta `.claude/skills` (P4). |
| Evidência e invalidação | **ausente no Spec Kit** | Diferencial do Hybrid. |

## 3. Comparação com `mattpocock/skills/engineering`

| Matt | Hybrid | Avaliação |
| --- | --- | --- |
| `ask-matt` (roteador com fluxo principal, *on-ramps* e árvore de fronteira de fase) | `hybrid-start` | Equivalente. Vale importar a árvore de `PHASE-BOUNDARIES.md` (continue / clear / handoff / subagente / compact) para substituir os limites 30 min / 60% (R2). |
| `grilling` + `grill-with-docs` (rodadas, fronteira de decisões, Q numerada com resposta recomendada, fatos via subagente) | `hybrid-discover` | **Adaptar o formato de rodadas.** O Hybrid descreve a ideia, mas não dá formato operacional. |
| `domain-modeling` | `hybrid-domain` | Equivalente. Alinhar o nome do glossário (R9). |
| `codebase-design` (módulo profundo, *design it twice*) | `testing.md` + `hybrid-plan` | Parcial. Pode entrar `DESIGN-IT-TWICE.md` como referência de `hybrid-plan` para escolher interfaces. |
| `to-spec` | `hybrid-specify` | O Hybrid é mais rigoroso. O Matt confirma os seams com o usuário antes de escrever. |
| `to-tickets` (**pergunta ao usuário** se a granularidade e as arestas estão certas antes de publicar; *prefactor first*) | `hybrid-slice` | **Adotar o passo de aprovação do fatiamento** e a regra de "prefactor primeiro". |
| `implement` / `implement-spec` (subagentes em paralelo na fronteira, worktrees, branch de integração) | `hybrid-implement` + `session` (série, até 3) | Opcional. O grafo e `owned_areas` do Hybrid já dão o que é preciso para uma variante paralela, mas isso conflita com "não commitar por padrão". |
| `tdd` (refatorar fica fora do loop; seams confirmados) | `testing.md` | Equivalente. O Hybrid permite refatoração pequena com a suíte verde, uma divergência aceitável. |
| `code-review` (eixos em **subagentes paralelos**, baseline de *code smells* de Fowler, sem reordenar entre eixos) | `hybrid-review` | **Adaptar:** subagentes e a lista de smells, que hoje é só "smell baseline" sem conteúdo (R6). |
| `diagnosing-bugs` (loop de feedback que fica vermelho, minimizar, 3 a 5 hipóteses falseáveis, logs `[DEBUG-xxxx]`, limpeza) | rota "Bug" em uma linha | **Maior lacuna.** Adaptar como referência `shared/references/diagnosis.md`, usada pela rota de bug. |
| `prototype` | rota "Pesquisa/protótipo" sem guia | Adaptar como referência curta, com o protótipo como fonte primária num branch `prototype/*`. |
| `research` (subagente em segundo plano, arquivo citado) | Context7 em `hybrid-plan` | Opcional. |
| `wayfinder` (mapa de decisões para esforços grandes e nebulosos, "névoa de guerra") | perfil "ampliado", sem definição | Adaptar localmente (`specs/<id>/map.md` com decisões em vez de tickets) só se houver esforços desse tamanho. |
| `retro` | ausente | **Adotar.** Fecha o ciclo e transforma erros mecânicos em checks automáticos. |
| `triage`, `pr`, `wizard`, `setup-*` | fora de escopo (tracker e publicação) | Não adaptar agora. |

## 4. `mattpocock/skills/productivity`: o que adaptar

| Skill | Recomendação | Como |
| --- | --- | --- |
| **`grilling` / `grill-me`** | **Sim, prioridade alta** | Levar o formato de rodadas (❓ Q*n* + ➡️ resposta recomendada, fronteira recalculada a cada rodada, fatos buscados pelo agente) para `hybrid-discover` e para `routing.md`. |
| **`writing-for-agents`** | **Sim, prioridade alta** | Este repositório é um repositório de skills, então ela serve para mantê-lo. Instalar como skill do repo e usar para auditar o Hybrid: duplicação (R7), negações, *no-ops*, "palavras-âncora". |
| **`to-questionnaire`** | **Sim, prioridade média** | Quando um `needs_input` depende de uma terceira pessoa (cliente, PO), `hybrid-discover` gera `specs/<id>/questions.md` no formato do Matt e retorna `needs_input` apontando o arquivo. |
| **`handoff`** | **Parcial** | O `session --write` já cobre continuação na mesma ferramenta. Adotar dois pontos: (a) redigir segredos e dados pessoais no prompt de continuação; (b) um modo para outra ferramenta ou colega que referencia os artefatos pelo caminho em vez de copiá-los. |
| **`wait-what`** | Opcional, custo quase zero | Um `hybrid-explain` de 3 linhas: "re-explique a última mensagem em linguagem simples usando `CONTEXT.md`". |
| **`teach`** | Não para o Hybrid | Pode servir à skill `criacao-de-cursos` deste repositório (missão, registros de aprendizagem, ZDP, prática de recuperação). |

## 5. Plano sugerido, por prioridade

1. **Runner:** validar transições de ticket no `ticket update` (P1), com a mesma regra de `validate` e uma máquina de estados explícita. Criar um registro mínimo de revisão (`review add`, ou campo `review_status` com o baseline) e exigi-lo para `done` (P2).
2. **Instalação:** adicionar `.claude/skills` à detecção (P4) e gerar `agents/openai.yaml` por skill para o Codex (R1).
3. **Evidência:** opção `evidence run --procedure ...`, em que o runner executa o comando e grava código de saída, duração e hash da saída. Manter `--executed` para casos manuais, com `attested: true` (P3).
4. **Skills:** formato de rodadas em `hybrid-discover`; subagentes e lista de smells em `hybrid-review`; passo de aprovação do fatiamento em `hybrid-slice`; nova referência `diagnosis.md` para a rota de bug.
5. **Política:** definir G1 a G4 em `vocabulary.md` (R4); trocar 30 min / 60% pela árvore de fronteira de fase com limite em tokens (R2); definir ou remover "Goal" (R3); trocar as dez seções "Milestone boundary" por um ponteiro de uma linha (R7).
6. **Artefatos:** template de constituição (R5) e modo `requirements` em `hybrid-check`, inspirado no `/checklist` (Spec Kit).
7. **Novas skills opcionais:** `hybrid-retro` e, se fizer sentido, `to-questionnaire`.

## 6. Custo em tokens e tempo (meta: ≤10% sobre o uso sem skill)

### O que realmente gera custo

Num loop de agente, cada turno reenvia o contexto inteiro. Logo, tokens cobrados ≈ Σ(contexto em cada turno) ≈ nº de turnos × contexto médio. O tempo depende principalmente do nº de turnos (ida e volta ao modelo + ferramenta) e dos tokens de saída. Daí saem três alavancas, em ordem de impacto:

1. **Turnos extras.** Cada "leia X", "rode Y", "registre Z" vira pelo menos uma chamada, e o agente obedece. O estudo da ETH Zurich sobre AGENTS.md (ICLR 2026) mediu isso: arquivos escritos por desenvolvedores aumentaram o custo em até 19% e o número de passos, com ganho médio de ~4% em sucesso. Os gerados por LLM custaram mais de 20% a mais e reduziram o sucesso em ~3%. A causa principal são as instruções que pedem para explorar e testar mais, não o tamanho do texto.
2. **Comprimento da sessão.** O custo cresce de forma quadrática com o nº de turnos, então dividir em sessões curtas a partir de um pacote pequeno reduz o custo. É por isso que a correção de `4f89771` (marcos e continuação) foi na direção certa.
3. **Texto estático lido cedo.** 10 mil tokens lidos no turno 2 são reenviados em todos os turnos seguintes. Com cache, a leitura repetida custa ~10% do preço, mas ainda ocupa a janela e a "smart zone".

### Medição estática do pacote atual

| Item | ≈ tokens |
| --- | --- |
| Um `SKILL.md` | 640–1.040 |
| `bounded-execution.md` (citada por 10 skills) | 1.540 |
| `operating-contract.md` | 840 |
| Leitura obrigatória da rota compacta (5 skills + referências) | ~11–13 mil |
| Saídas JSON do runner (`start`, `session`, `validate`...) | 60–440 cada; `package` ~1.570 |
| Ticket do exemplo (saída escrita pelo modelo) | ~750 cada |

O runner em si é barato. O custo está no **nº de chamadas que as skills mandam fazer**. Na rota compacta isso dá cerca de 20 a 25 chamadas extras: `start`, `session`, validação, checkpoint, leitura de 3 a 5 referências, `invalidate`, reexecução dos testes no `verify` (que o `implement` já tinha rodado), `evidence add` e cinco comandos git no `review`. Além disso, o usuário precisa digitar 5 comandos.

### Estimativa (modelo, não medição)

Premissas: prompt de sistema de 15 mil tokens. Tarefa pequena: 12 turnos sem skill. Tarefa média: 70 turnos numa única sessão.

| Cenário | Tokens cobrados | Turnos |
| --- | --- | --- |
| Pequena: sem skill | ~300 mil | 12 |
| Pequena: Hybrid atual (rota compacta completa) | **~1,5 M (+400%)** | ~34 |
| Pequena: Hybrid enxuto (1 skill, ~1,2 mil tokens, 2 chamadas) | ~370 mil (+25%) | 14 |
| Média: sem skill, 1 sessão | ~4,7 M | 70 |
| Média: Hybrid atual numa sessão | ~11,8 M (+150%) | ~115 |
| Média: Hybrid enxuto (sessão de plano + 3 sessões curtas de execução) | ~4,3 M (**−7%**) | ~100 |

Referência externa: num mesmo experimento, o Spec Kit gastou ~121 mil tokens contra ~58 mil do OpenSpec (+109%). Só o planejamento ficou 152% maior. O Hybrid atual tem uma cerimônia parecida com a do Spec Kit.

### Conclusão

- **≤10% é viável em tarefas médias e grandes**, e pode até ficar abaixo do uso sem skill. A condição é que o kit faça três coisas: separar o planejamento da execução em sessões curtas, entregar um pacote pequeno à execução e não acrescentar chamadas ao ciclo de implementação.
- **Em tarefas pequenas, ≤10% só é viável se o kit quase não atuar.** Duas chamadas extras já representam ~15–25% de uma tarefa de 12 turnos. A rota certa para algo trivial é "não usar o kit". Para algo pequeno mas rastreável, o caminho é uma rota de uma skill, sem referências e com 1 ou 2 chamadas ao runner.
- A comparação justa é **custo por tarefa concluída corretamente**: o retrabalho do uso sem skill entra na conta. Mesmo assim, a meta proposta mede o overhead bruto.

### Mudanças com maior retorno (ordem sugerida)

1. **Um comando de entrada:** `hybrid.py next --effort <id> --json` substituiria `start` + `session` + `invalidate` + `package`, devolvendo um pacote de ≤600 tokens com o ticket, o que ler e o comando de validação. Economiza 3 ou 4 turnos por sessão.
2. **`evidence run`:** o runner executa o comando de teste, grava a evidência e avança o status do ticket na mesma chamada. Com isso o `verify` deixa de ser uma fase separada no caminho normal e o teste final não roda duas vezes.
3. **Orçamento explícito por rota**, escrito no `hybrid-start`:
   - trivial: 0 artefatos e 0 chamadas ao runner;
   - compacta: 1 skill, 1 artefato, no máximo 2 chamadas;
   - padrão: sessão de plano separada e, na execução, no máximo 3 chamadas ao runner por ticket.
4. **Referências só sob demanda (progressive disclosure):** cada `SKILL.md` deve trazer em linha as 3 a 5 regras que usa sempre. As referências só seriam lidas num caso específico (migração, avaliação externa, conflito). Remover as 10 seções "Milestone boundary" e reduzir `bounded-execution.md` para cerca de 300 tokens.
5. **Revisão proporcional:**
   - compacta: nenhuma fase separada; basta um `git diff` comparado com o `change.md` no fim do `implement`;
   - padrão: uma revisão por marco, em subagente, o que mantém o contexto principal pequeno;
   - um único comando git (`git status --short` + `git diff <baseline>`) em vez de cinco.
6. **Renovar a sessão mais cedo:** por ticket ou perto de 80–100 mil tokens, e não com 60% da janela (que numa janela de 1M são 600 mil). O custo é quadrático, então renovar tarde sai caro.
7. **Template de ticket com seções condicionais:** omitir as que não se aplicam. Hoje são 11 seções e cerca de 670 tokens por ticket, gerados com o modelo mais caro.
8. **Medir em vez de estimar:** um harness A/B com `claude -p --output-format json` (que retorna `num_turns`, `duration_ms`, `usage` e `total_cost_usd`). Usar 3 a 5 tarefas reais, ≥3 execuções por braço, e comparar a mediana do custo por tarefa aprovada. Critério de aceite: ≤10% em tarefas médias, e na rota trivial nenhum overhead.

Fontes: [ETH Zurich, *Evaluating AGENTS.md*](https://arxiv.org/abs/2602.11988) (via [InfoQ](https://infoq.com/news/2026/03/agents-context-file-value-review/) e [agentpatterns.ai](https://agentpatterns.ai/instructions/evaluating-agents-md-context-files/)); [Spec Kit × OpenSpec, comparação de tokens](https://medium.com/it-chronicles/is-your-safe-choice-burning-your-budget-1cfddf8782e4) (artigo inacessível daqui; números do resumo da busca); [Anthropic, *Harnessing Claude's intelligence*](https://claude.com/blog/harnessing-claudes-intelligence) (cache e contexto por turno).
