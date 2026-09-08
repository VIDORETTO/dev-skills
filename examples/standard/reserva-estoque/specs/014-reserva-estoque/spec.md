---
schema: hybrid/spec
schema_version: "1.0"
effort_id: 014-reserva-estoque
revision: 2
status: accepted
profile: standard
---

# Specification: Reserva de estoque

## Problem and desired result

Um pedido precisa reservar unidades sem permitir que uma repetição da mesma solicitação reduza o estoque novamente. O resultado é uma reserva observável, disponibilidade atualizada e rejeições explicadas.

## Consumers and actors

O consumidor é o fluxo de pedidos que solicita uma reserva. A chave de repetição identifica a solicitação, não o produto.

## Scope

### Included

- Reservar quantidade disponível, repetir de forma idempotente e rejeitar conflitos ou insuficiência.

### Excluded

- Estorno, expiração e integração com transportadora.

## User journeys and scenarios

### US-001 — Reservar quantidade disponível (Priority: P1)

Como um fluxo de pedidos, quero reservar unidades disponíveis para que o pedido não consuma estoque de forma incorreta.

Independent demonstration: iniciar com 10 unidades, reservar 3 e consultar o resultado.

#### Acceptance scenarios

- **AC-001** — Dado um produto com 10 unidades disponíveis, quando 3 unidades são reservadas, então a reserva tem 3 e ficam 7 disponíveis.
- **AC-004** — Dado um produto com 7 unidades disponíveis, quando são solicitadas 8, então a operação é rejeitada e continuam 7 disponíveis.

### US-002 — Repetir uma solicitação sem duplicar efeito (Priority: P1)

Como um fluxo que pode reenviar pedidos, quero que a mesma chave retorne o resultado original sem reservar novamente.

#### Acceptance scenarios

- **AC-002** — Dada uma reserva já criada, quando a mesma chave e os mesmos dados são reenviados, então a reserva original é retornada e a disponibilidade não muda.
- **AC-003** — Dada uma chave já usada, quando a quantidade diferente é reenviada, então a operação retorna conflito e não altera a reserva.

### US-003 — Preservar o limite sob concorrência (Priority: P1)

Como um operador de estoque, quero que solicitações concorrentes respeitem a disponibilidade para que ela nunca fique negativa.

#### Acceptance scenarios

- **AC-005** — Dadas duas solicitações simultâneas de 4 unidades e apenas 5 disponíveis, no máximo uma reserva 4; a disponibilidade não fica negativa.

## Requirements

- **FR-001** — O sistema MUST reservar somente quantidade disponível e expor a reserva criada.
- **FR-002** — O sistema MUST tratar a mesma chave com os mesmos dados de modo idempotente e rejeitar reutilização conflitante.
- **FR-003** — O sistema MUST preservar a disponibilidade sob concorrência.

## Limits, errors, and compatibility

Quantidade acima do disponível produz erro de insuficiência sem alteração. Chave reutilizada com dados diferentes produz conflito sem alteração. A interface existente de reserva e consulta deve continuar compatível.

## Hypotheses and dependencies

- Hipótese H-001: a persistência atual consegue representar a chave de repetição. Impacto: define se o plano precisa de migração. Check: inspecionar o modelo e executar o cenário de conflito.
- Dependência: módulo de estoque existente. Estado: observado.

## Success criteria

### Delivery-verifiable

- **SC-001** — AC-001, AC-002, AC-003, AC-004 e AC-005 possuem testes ou procedimentos executados e evidência atual.

### Post-delivery observation

- **SC-002** — Observar a taxa de reservas duplicadas após uso real; não é inferida pelos testes.

## Decisions and open questions

A consistência deve ser garantida pela Interface de reserva e pela persistência representativa escolhida no plano. Não há pergunta de produto pendente para esta fatia.
