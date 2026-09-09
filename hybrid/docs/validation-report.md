# Relatório de validação

Data do registro: 2026-09-08. O pacote não está dentro de um repositório Git próprio; por isso a revisão testada é identificada como `working tree 2026-09-08`, sem inventar um SHA. Os repositórios-fonte `spec-kit/` e `mattpocock-skills-filtered/` permaneceram limpos.

## Comandos executados

| Procedimento | Resultado | Revisão testada | Limitação |
| --- | --- | --- | --- |
| `python scripts/hybrid.py package-validate --json` | Passou: 10 skills, 8 schemas, links relativos e compilação do runner | working tree 2026-09-08 | Não prova qualidade semântica das instruções |
| `python -m unittest discover -s tests -v` | Passou: 19 testes, incluindo fixtures temporários, compacto, exemplos, grafo, projeções, checkpoint, baseline Git, evidência, gates de pacote, deduplicação, configuração e instalação | working tree 2026-09-08; fixtures efêmeros | Não substitui a execução por uma IA em contexto novo |
| `python -m json.tool examples/evaluation/cases.json > $null` | Passou | working tree 2026-09-08 | Verifica somente sintaxe JSON |
| `validate` no exemplo padrão e no compacto | Passou nos dois; os exemplos agora usam `specs/<effort-id>` | working tree 2026-09-08 | Os caminhos de código dos exemplos continuam ilustrativos |
| `start` nos dois exemplos, `graph` e `package` no padrão | Passou; fronteira `TK-001`, pacote `TK-001` pronto e inputs atuais | working tree 2026-09-08 | O pacote exemplo não executa a aplicação hipotética |
| instalação local em projeto temporário e `package-validate` pelo `.hybrid/hybrid.py` instalado | Passou dentro da suíte; conflitos de arquivo existente também foram exercitados | working tree 2026-09-08; projeto efêmero | Não altera uma instalação real nem testa outro agente |

O runner distingue `observed_only` de `executed`: uma evidência `passed`, `failed` ou `partial` exige `--executed`, guarda o fingerprint dos caminhos relevantes e inclui contrato e plano quando aplicáveis. A atualização de estado do ticket não invalida uma execução; alteração de contrato, código ou outra entrada vinculada exige nova execução.

## Casos E01–E31

Os procedimentos completos e os oráculos que devem ficar fora do contexto da executora estão em [`examples/evaluation/cases.json`](../examples/evaluation/cases.json). A tabela registra o estado desta entrega para cada caso.

| Caso | Procedimento registrado | Resultado | Revisão testada | Limitação |
| --- | --- | --- | --- | --- |
| E01 | `hybrid-start` + `hybrid-discover` em diretório sem repositório | Pendente de modelo | Não executada | Requer julgamento de descoberta e primeiro resultado |
| E02 | Rota de função pequena com `change.md` | Pendente de modelo | Não executada | Requer escolha proporcional e execução de código |
| E03 | Git temporário com alteração do usuário + `hybrid-start` | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture Git temporário | O check cobre baseline e preservação por leitura; decisão semântica da IA permanece pendente |
| E04 | Exemplo com tickets prontos + entrada na próxima etapa | Pendente de modelo | Não executada | Requer detectar fase faltante sem repetir gates |
| E05 | Caso ambíguo em discovery/specify | Pendente de modelo | Não executada | Requer pergunta material concreta |
| E06 | Retomada após remover campo editorial do plano | Pendente de modelo | Não executada | Requer distinguir convenção de decisão material |
| E07 | Bug reproduzível → regressão → correção | Pendente de modelo | Não executada | Requer observar red/green em aplicação |
| E08 | Revisão de teste cujo esperado copia a implementação | Pendente de modelo | Não executada | Requer julgamento de oráculo independente |
| E09 | Mapa de consumidores + `hybrid-plan`/`hybrid-slice` | Pendente de modelo | Não executada | Requer avaliar migração expand–contract |
| E10 | `state.json` interrompido + retomada em contexto novo | Pendente de modelo | Não executada | Requer observar não repetição de trabalho |
| E11 | Alterar revisão da spec + `invalidate`/`check` | Pendente de modelo | Não executada | Requer reconciliação semântica de dependentes |
| E12 | Alterar caminho em `input_paths` + `invalidate --write` | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | O check prova fingerprint/stale; impacto semântico exige modelo |
| E13 | Review Git com commit, staged, unstaged e arquivo novo | Pendente de modelo | Não executada | Requer análise de diff completo |
| E14 | `check --mode convergence` com aceite sem evidência corrente | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | O check não avalia a decisão da executora |
| E15 | `finding add` duas vezes com a mesma chave | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | Cobre identidade/estado, não qualidade da correção |
| E16 | `hybrid-verify` sem serviço obrigatório | Pendente de modelo | Não executada | Requer registrar impedimento real sem aprovar |
| E17 | `hybrid-review` em pedido review-only | Pendente de modelo | Não executada | Requer observar que não houve edição/publicação |
| E18 | Ticket verde com checklist de reviewer pendente | Pendente de modelo | Não executada | Requer separar ownership de aprovação |
| E19 | Tickets com `owned_areas` sobrepostas + grafo | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | O check detecta a sobreposição; a decisão de serialização/dependência requer avaliação comportamental |
| E20 | Não executar adapter de tracker remoto | Não aplicável | N/A | Tracker remoto está fora da v1 |
| E21 | Medir contexto lido pela executora para funcionalidade grande | Pendente de modelo | Não executada | Requer medir uma execução real |
| E22 | Renderizar duas vezes e comparar arquivos/hashes | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | Cobre projeção sem mudança, não julgamento de rota |
| E23 | Verificação técnica com métrica pós-entrega | Pendente de modelo | Não executada | Requer separar observação de produção |
| E24 | Cancelar esforço e iniciar nova demanda | Pendente de modelo | Não executada | Requer preservar histórico em uma conversa real |
| E25 | Entregar somente ticket, contratos e referências a uma sessão limpa | Pendente de modelo | Não executada | Não houve segundo modelo/contexto autorizado |
| E26 | Alterar símbolo antes da execução e observar retorno | Pendente de modelo | Não executada | Requer localizar incompatibilidade sem improvisar |
| E27 | Roadmap com `CAND-004` + render de backlog/TODO | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | Cobre projeções separadas; promoção ainda exige avaliação de prontidão |
| E28 | Alterar texto/revisão de AC + `start`/`invalidate`/`check` | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | Cobre revisão, fingerprint, stale e reabertura; não avalia a reconciliação humana |
| E29 | Review de diff que enfraquece o esperado | Pendente de modelo | Não executada | Requer julgamento semântico do contrato |
| E30 | Uma IA executa planejamento e execução completos | Pendente de modelo | Não executada | Requer auditar separação de gates em rota real |
| E31 | Ticket com evidência passada → `todo.md`/`backlog.md` derivados | Passou subcheck determinístico; comportamento pendente | working tree 2026-09-08 + fixture temporário | Cobre geração/hash; não prova uma entrega de produto |

Nenhum caso comportamental foi declarado aprovado por presença de texto ou por schema válido. A passagem de trabalho para outra IA e a medição de custo/economia permanecem pendentes até existir um modelo/contexto autorizado para executar os casos com o campo `expected` oculto.
