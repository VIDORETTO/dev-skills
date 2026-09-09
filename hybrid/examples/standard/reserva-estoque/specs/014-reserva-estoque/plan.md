---
schema: hybrid/plan
schema_version: "1.0"
effort_id: 014-reserva-estoque
revision: 1
spec_revision: 2
status: ready
---

# Plan: Reserva de estoque

## Summary

Manter a lógica de reserva atrás da Interface pública existente, acrescentando idempotência por chave e consistência na operação de persistência já usada pelo módulo.

## Technical context

- Language/runtime: a confirmar no repositório consumidor.
- Dependencies: módulo de estoque existente.
- Storage/data: adapter de persistência existente; confirmar suporte à chave.
- Test command: comando existente do projeto, verificado antes de executar cada ticket.
- Target/platform: serviço de pedidos.

## Consumed contract

- Spec: `spec.md`, revision 2.
- Requirements and acceptance refs: FR-001, FR-002, FR-003; AC-001–AC-005.

## Modules, interfaces, consumers, and seams

O Module de reserva expõe as Interfaces `reserve` e `getReservation` ao fluxo de pedidos. O seam escolhido é essa Interface pública; o teste de concorrência usa o adapter de persistência representativo. Símbolos existentes devem ser confirmados no checkout antes da execução.

## Chosen approach and alternatives

Usar a Interface existente e a garantia transacional do adapter atual, depois de confirmar sua documentação. Não criar uma camada genérica nova nem testar por consulta direta ao banco. Uma fila assíncrona foi descartada para esta fatia porque mudaria o resultado síncrono aceito.

## Data, compatibility, and external dependencies

Se a chave não existir no modelo, expandir de modo compatível, migrar consumidores e só então contrair. Não remover o formato anterior até comprovar ausência de consumidores.

## Verification strategy

AC-001 e AC-004 serão exercitados pela Interface com resultados literais. AC-002 e AC-003 usarão a mesma chave e dados/conflito. AC-005 exigirá duas operações concorrentes no adapter representativo; duas chamadas sequenciais não comprovam o critério. O comando identificado na configuração será registrado separadamente do resultado realmente executado.

## Change map

| Path | Existing/new | Symbol or section | Purpose | Reference revision |
| --- | --- | --- | --- | --- |
| `src/stock/reservations` | existing | `reserve`, `getReservation` | localizar seam e implementação | checkout antes do ticket |
| `tests/stock/reservations` | existing/new | public behavior cases | observar os cinco AC | checkout antes do ticket |

## Derived technical obligations

- **OT-001** → FR-003/AC-005: a verificação deve exercitar disputa real no adapter representativo.

## Risks and gates

G2 exige confirmar a capacidade do adapter. G3 exige blockers concluídos e caminhos atualizados. AC-005 fica sem aprovação se o ambiente não conseguir executar concorrência real.
