---
schema: hybrid/ticket
schema_version: "1.0"
id: TK-001
effort: [EFFORT_ID]
type: delivery
status: draft
ticket_revision: 1
requires: []
requirement_refs: [FR-001]
acceptance_refs: [AC-001]
spec_revision: 1
plan_revision: 1
owned_areas: [src/area, tests/area]
verification_status: not_run
review_status: pending
---

# TK-001 — [Título da fatia]

<!-- Obrigatórias: Objetivo e limites, Leitura em ordem, Exemplos de aceite, Validação.
     As demais são opcionais: apague a seção quando não houver nada específico deste ticket.
     O ciclo red/green, a condição de retorno e o relatório de saída já estão em hybrid-implement. -->

## Objetivo e limites

Entrega um comportamento demonstrável ligado aos refs acima.

Não inclui: [exclusões específicas desta fatia].

## Leitura em ordem

1. `[path]` → `[symbol/section]` — [por que ler].

## Exemplos de aceite

- **AC-001**: estado [x] + entrada [y] → resultado [z]; efeito proibido [b]. Oráculo: [spec/exemplo independente].

## Validação

`[comando exato]`, executado em `[diretório]`.

## Decisões já resolvidas (opcional)

- [Abordagem e motivo curto]. Liberdade local: [detalhes reversíveis].

## Mapa de alterações (opcional)

- Existente: `[path]` → `[symbol]`. Novo: `[path]` → `[NewSymbol]`. Fora da fatia: `[path]`.

## Contrato técnico (opcional)

Entradas, saídas, invariantes, erros, efeitos, compatibilidade/concorrência, quando não forem óbvios pelo contrato.
