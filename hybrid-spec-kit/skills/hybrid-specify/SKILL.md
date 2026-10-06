---
name: hybrid-specify
description: Write and evolve a versioned behavioral contract with stable requirements and acceptance criteria for a hybrid development effort. Use after discovery or when an existing spec/change needs creation, clarification, bug expectation, migration scope, or contract reconciliation.
disable-model-invocation: true
---

# Hybrid specify

**Scope:** only for work that passed the `hybrid-start` scope gate. Direct work needs no contract.

Own the behavior contract: `spec.md` (standard/expanded) or `change.md` (compact). Architecture belongs to `hybrid-plan`.

## Write

Start from [the standard template](../../shared/templates/standard/spec.md) or [the compact template](../../shared/templates/compact/change.md). Capture:

- problem, consumer, desired result, and prioritized journeys, or a direct function contract (inputs, outputs, invariants, errors, units, rounding, compatibility);
- included scope and explicit exclusions;
- stable `FR-xxx` requirements and observable `AC-xxx` criteria covering primary, alternate, error, and relevant non-functional cases;
- hypotheses and dependencies, with delivery-verifiable success kept apart from post-delivery metrics.

Before closing, scan for gaps that would change behavior: scope and roles, data identity and lifecycle, error/empty states, limits and scale, security and privacy, external failure modes, concurrency, and testability of each `AC`. Ask only about gaps that change behavior, using the round format of `hybrid-discover`, and write each answer into the contract.

## Rules

Keep IDs stable: a new item gets the next number, and existing ones are never renumbered. Increment `revision` for a meaningful change; a semantic change requires reconciling plan, tickets, and evidence. Compact mode keeps everything in `change.md`.

Run `hybrid validate --effort <id>` once after editing.

G1 passes when behavior and criteria are coherent, testable, bounded, and no critical choice is silently assumed. Return contract path/revision, open questions, affected dependents, and `next_action` (`hybrid-plan`, or `hybrid-implement` for compact).
