---
name: hybrid-slice
description: Decompose an accepted hybrid contract and plan into vertical execution tickets with stable IDs, real blockers, concrete code context, and generated task views. Use when a standard or expanded effort is ready to become executable by a fresh session or a lower-cost AI.
disable-model-invocation: true
---

# Hybrid slice

**Scope:** standard and expanded efforts only. Compact work stays in `change.md`, with no tickets.

Ticket files are the single editable source for delivery and status; `todo.md` and `backlog.md` are generated from them.

## Propose, then write

1. From `spec.md` and `plan.md`, draft a few vertical slices. Each one is a demonstrable behavior through the modules it uses and fits one fresh session. Prefactoring comes first. Tests, review, and helpers stay inside their behavior slice.
2. Show the breakdown as a numbered list (title, blocked by, what it delivers) and ask once whether the granularity and edges are right. Iterate only on what the user changes.
3. Write each ticket from [the ticket template](../../shared/templates/standard/ticket.md) and get IDs from `hybrid next-id --effort <id> --prefix TK`. Fill every required section; omit the optional ones that do not apply. `requires` lists only genuine blockers, and a predecessor counts only when `done`.

A ticket that leaves a material design (authentication, concurrency, public contract) to the executor stays `blocked`, and the choice goes back to planning. Overlapping `owned_areas` mean serialize the tickets or add a real blocker. See [execution-package.md](../../shared/references/execution-package.md) only when a package field is unclear.

## Close

Run `hybrid next --effort <id> --write` once: it validates the graph and reports readiness for the first ticket. Then run `hybrid render --effort <id> --view all`. Record the initial ticket count; growth over 20% triggers reconciliation, never deletion of required work.

G3 passes when inputs are current, blockers are satisfied, references are verified, and the first package is ready. Return ticket paths, frontier, and `next_action`: a fresh session with `hybrid-start`.
