---
schema: hybrid/ticket
schema_version: "1.0"
id: TK-002
effort: 014-reserva-estoque
type: delivery
status: ready
ticket_revision: 1
requires: [TK-001]
requirement_refs: [FR-002]
acceptance_refs: [AC-002, AC-003]
spec_revision: 2
plan_revision: 1
owned_areas: [src/stock/reservations, tests/stock/reservations]
verification_status: not_run
---

# TK-002 — Repetição idempotente e conflito

## Objetivo e limites

Entrega repetição sem duplicar reserva e rejeição de reutilização conflitante.

Não inclui: concorrência, expiração ou transportadora.

## Leitura em ordem

1. `specs/014-reserva-estoque/spec.md` → AC-002/AC-003 — recuperar o contrato literal.
2. `src/stock/reservations` → `reserve` e `getReservation` — confirmar como a chave é exposta.

## Decisões já resolvidas

- Repetição igual retorna o resultado original e não reaplica o efeito.
- Liberdade local: representação interna compatível com o adapter existente.
- Alternativa descartada: aceitar uma quantidade diferente silenciosamente.

## Mapa de alterações

- Existente: `src/stock/reservations` → `reserve` — consultar e comparar a chave.
- Novo: `tests/stock/reservations/idempotency-behavior` → cenários AC-002/AC-003.
- Fora da fatia: disputa concorrente de TK-003.

## Contrato técnico

- Entradas: chave de repetição, produto e quantidade.
- Saídas: reserva original para dados iguais; conflito para dados diferentes.
- Invariantes: uma chave não produz duas reservas nem muda quantidade após repetição.
- Erros: conflito de chave com dados diferentes.
- Efeitos: repetição não diminui disponibilidade.
- Compatibilidade/concorrência: preservar formato existente; concorrência fica em TK-003.

## Exemplos de aceite

- **AC-002**: reserva 3 com chave K + mesma solicitação → mesma reserva e disponibilidade inalterada.
- **AC-003**: chave K já usada com 3 + nova solicitação de 4 → conflito e estado inalterado.

## Dependências e sequência de execução

Depende de: TK-001 concluído com status `done`.

- [ ] TK-002.1 Exercitar repetição e observar red relevante.
- [ ] TK-002.2 Implementar AC-002 sem duplicar efeito.
- [ ] TK-002.3 Exercitar conflito e implementar AC-003.
- [ ] TK-002.4 Executar regressão e registrar evidência.

## Validação

- Diretório: raiz do projeto consumidor.
- Comando/procedimento exato: teste focalizado de idempotência identificado no projeto.
- Estado esperado: AC-002 e AC-003 passam com disponibilidade observável.
- Comando identificado na configuração mas não executado: registrar separadamente.
- Distinguir defeito de ambiente: não interpretar falha de adapter ausente como red de negócio.

## Condição de retorno à planejadora

Retornar se a Interface não permitir recuperar por chave ou se a mudança exigir redefinir conflito/compatibilidade.

## Relatório de saída

Relatar arquivos/símbolos, AC-002/AC-003, EV refs, desvios e próxima ação. Não alterar a spec para aceitar uma implementação divergente.
