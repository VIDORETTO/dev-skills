---
name: hybrid-plan
description: Design the technical solution for an accepted hybrid contract by mapping modules, interfaces, consumers, seams, risks, compatibility, and executable verification. Use when a standard or expanded effort needs a plan, research, data model, contract, migration strategy, or technical decision.
disable-model-invocation: true
---

# Hybrid plan

**Scope:** standard and expanded efforts only. A compact change keeps its short plan inside `change.md`.

Own the technical solution: `plan.md`, plus research, data model, or contracts only when the next slices need them.

## Explore

Read the accepted contract, the code and tests around the affected behavior, `CONTEXT.md`, relevant ADRs, and [testing.md](../../shared/references/testing.md). Verify paths and symbols and label each as existing or new. Read only what the next slice needs.

Choose Modules, their Interfaces, consumers, and the highest seam that stays fast, deterministic, and diagnostic. Add an adapter only where a real variation exists. For persistence, concurrency, external integration, UI, or public compatibility, state the representative evidence required. When a library, SDK, API, or service affects a decision, query Context7 (or primary docs) once with the full question and record version and source.

## Write `plan.md`

Include: consumed spec revision; chosen approach and real alternatives; module/interface map; change locations; data, migration, and dependency strategy; seams and independent oracles; the exact validation command per ticket (marked observed or executed); risks; and the G2 gate. Use expand–contract for wide refactors or migrations.

Identify the initial ticket count and the first milestone. Keep test, helper, and instrumentation work inside the behavior slice. A behavior change discovered here goes back to `hybrid-specify`.

Register the plan and validate in one call: `hybrid next --effort <id> --write`. Return plan revision, research refs, limitations, and `next_action` (`hybrid-slice`).
