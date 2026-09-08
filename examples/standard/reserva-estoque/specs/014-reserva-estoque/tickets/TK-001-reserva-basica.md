---
schema: hybrid/ticket
schema_version: "1.0"
id: TK-001
effort: 014-reserva-estoque
type: delivery
status: ready
ticket_revision: 1
requires: []
requirement_refs: [FR-001]
acceptance_refs: [AC-001, AC-004]
spec_revision: 2
plan_revision: 1
owned_areas: [src/stock/reservations, tests/stock/reservations]
verification_status: not_run
---

# TK-001 — Reserva válida e insuficiência

## Objetivo e limites

Entrega reserva válida e rejeição de quantidade insuficiente.

Não inclui: idempotência, conflito de chave, concorrência ou transportadora.

## Leitura em ordem

1. `src/stock/reservations` → `reserve` — confirmar a Interface atual.
2. `tests/stock/reservations` → casos existentes — preservar o padrão de teste.

## Decisões já resolvidas

- Testar pela Interface pública existente; não consultar estado interno.
- Liberdade local: nomes de helpers de teste compatíveis com a convenção do projeto.
- Alternativa descartada: criar um serviço genérico de estoque nesta fatia.

## Mapa de alterações

- Existente: `src/stock/reservations` → `reserve` — aplicar regra de disponibilidade.
- Novo: `tests/stock/reservations/reserve-behavior` → `reserves-available-quantity` — criar se necessário.
- Fora da fatia: persistência de idempotência e integração externa.

## Contrato técnico

- Entradas: produto existente e quantidade inteira positiva.
- Saídas: reserva criada com a quantidade solicitada ou erro de insuficiência.
- Invariantes: disponibilidade nunca fica negativa; rejeição não altera estoque.
- Erros: insuficiência para solicitação acima do disponível.
- Efeitos: reserva observável pela Interface.
- Compatibilidade/concorrência: manter a Interface atual; concorrência será TK-003.

## Exemplos de aceite

- **AC-001**: 10 disponíveis + 3 → reserva 3 e disponibilidade 7; o resultado literal vem da spec.
- **AC-004**: 7 disponíveis + 8 → erro de insuficiência e disponibilidade 7; não alterar estado.

## Dependências e sequência de execução

Depende de: nenhum.

- [ ] TK-001.1 Escrever AC-001 e observar red pelo comportamento ausente.
- [ ] TK-001.2 Implementar o mínimo e observar green de AC-001.
- [ ] TK-001.3 Escrever AC-004, implementar rejeição e observar a disponibilidade preservada.
- [ ] TK-001.4 Executar regressão, registrar checkpoint e evidência.

## Validação

- Diretório: raiz do projeto consumidor.
- Comando/procedimento exato: comando de teste focalizado identificado no projeto.
- Estado esperado: AC-001 e AC-004 passam com oráculo literal.
- Comando identificado na configuração mas não executado: registrar se houver.
- Distinguir defeito de ambiente: falha de importação/serviço não conta como red de negócio.

## Condição de retorno à planejadora

Retornar se `reserve` não aceitar os dados previstos, se a Interface exigir mudança pública ou se a persistência não oferecer a operação necessária.

## Relatório de saída

Relatar arquivos e símbolos alterados, AC-001/AC-004, EV refs, limitações e próxima ação. Não marcar `done` sem verificação e review.
