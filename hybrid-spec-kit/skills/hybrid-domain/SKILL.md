---
name: hybrid-domain
description: Maintain the project's domain glossary and selective architecture decision records while preserving bounded-context language. Use when a term is resolved, terminology conflicts, or a hard-to-reverse technical decision needs durable context.
disable-model-invocation: true
---

# Hybrid domain

**Scope:** only for work that passed the `hybrid-start` scope gate, and only for terms and decisions the active work needs.

Own `CONTEXT.md`, `CONTEXT-MAP.md` when it exists, and ADRs. Feature specs, plans, and tickets belong to other skills.

## Glossary

When a term is resolved, update the owning `CONTEXT.md`: what the concept is in one or two sentences, one canonical term, and ambiguous alternatives under `_Avoid_`. With several contexts, edit the one the map assigns. Keep it to domain language: implementation details and generic programming terms stay out.

If code and the proposed language disagree, report the path/symbol and say whether the code is observed behavior or a decision to change.

## ADR

Write `docs/adr/NNNN-slug.md` (highest number + 1) only when the decision is hard to reverse, surprising without context, and the result of a real trade-off. Record context, decision, and reason; add rejected options only when a future reader needs them. A reversible local preference belongs in `plan.md`.

Return changed paths, terminology conflicts, ADR refs, and the next owner.
