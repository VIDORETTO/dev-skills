# Quando o usuário quer “o software inteiro”

“Clonar tudo” não fornece um critério de aceite. Antes de prometer escopo, obtenha **inventário de capacidades**, **fronteiras** e **graus de fidelidade**. Este playbook amplia `grill-me.md` e `quality-gates.md`.

## Três níveis de resultado (exemplos, não padrões universais)

- **Inspirado:** resolver o mesmo problema do usuário com comportamento novo, sem exigir identidade ao original.
- **Paridade dos fluxos críticos:** reproduzir workflows nomeados e testados, sem prometer cobertura total.
- **Compatibilidade ampliada:** executar suítes de referência por módulo, arquivos, API e plataforma; ainda sujeita à cobertura conhecida.

Pergunta que evita expectativas falsas: “Quais são os 5 fluxos que, se não funcionarem, tornam o clone inútil?”. Depois faça ranking e transforme em épicos isolados. Dê prioridade também a **dados, autenticação autorizada, persistência, erros e integração**; não apenas às telas bonitas.

## Catálogo de features

| Campo | Descrição |
|---|---|
| `feature` | nome e usuário beneficiado |
| `criticality` | crítico / importante / opcional |
| `evidence` | observado / inferido / desconhecido + EV IDs |
| `oracle` | como demonstrar o comportamento |
| `dependency` | módulos, dados e permissões necessárias |
| `implementation` | reuso / fonte / black-box / RE pontual |
| `status` | não iniciado / parcial / validado |
| `risks` | segurança, licenças, dados, performance |

Comece pelo **mapa superficial**: telas, URLs, menus, workflows, arquivos, contratos e dependências. Só investigue internamente os módulos que não podem ser explicados por fonte/documentação/contrato. Para software grande, separe investigação e implementação em **fatias verticais** completas que possam ser demonstradas e testadas.

## Estratégia em três ondas

1. **Discovery com orçamento limitado:** mapear escopo e produzir 1 prova de viabilidade de alto risco. Não gastar semanas em descompilação indiscriminada.
2. **Vertical slice:** implementar e testar fluxo de ponta a ponta com dados e UI reais/sintéticos, observabilidade e regressão.
3. **Expansão guiada por cobertura:** ampliar features por prioridade de usuário, dependência técnica e custo; comparar em cada entrega.

## Métricas e limites honestos

- `N features validas / M catalogadas` mede **cobertura do catálogo**, que pode estar incompleto.
- `P testes passados / T executados` mede a suíte em um build e ambiente, não “percentual de clone”.
- Documentar claramente o que foi catalogado mas não implementado, e o que ainda pode nem ter sido descoberto.
- Não usar screenshots de uma tela como prova de paridade de sistema.

## Critério para preferir recomeçar do zero

Uma solução original pode ser melhor se os requisitos prioritários são gerais, não existe compatibilidade de arquivo/protocolo obrigatória, a infraestrutura do original é inadequada, e reuso/OSS acelera manutenção. Mesmo assim, objetivos e testes devem estar explícitos.
