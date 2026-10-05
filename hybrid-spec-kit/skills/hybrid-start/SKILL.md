---
name: hybrid-start
description: Route a development request into the hybrid workflow, inspect an existing project, and resume an effort from its checkpoint. Use when starting, resuming, or triaging a project, feature, bug, refactor, migration, prototype, or review.
disable-model-invocation: true
---

# Hybrid start

Use this as the entrypoint. It is a router with a small reconnaissance pass, not a superprompt that repeats the other skills.

## Read first

1. Read the repository's applicable `AGENTS.md`, `CLAUDE.md`, or equivalent instructions and the user's current request.
2. Inspect `git status --short --branch`, the repository root, existing `CONTEXT.md`/`CONTEXT-MAP.md`, ADRs, `docs/agents/`, `.hybrid/config.json`, and `specs/` only as far as the request needs.
3. If an effort is named, run `python <package-root>/scripts/hybrid.py start --project . --effort <id> --json`. After local installation, the equivalent is `python .hybrid/hybrid.py start --project . --effort <id> --json`.
4. For an existing effort, read [bounded-execution.md](../../shared/references/bounded-execution.md) and run `session --effort <id> --json` to select the next bounded milestone. Run readiness validation once before editing; reuse it only while its inputs are unchanged. A failed check routes repair to its owner; it does not authorize rewriting contracts.

Record a Git SHA before implementation when Git is available. With no commits, record an inventory fingerprint and say that the baseline is not a SHA. Include staged, unstaged, untracked, and user-owned work in the reconnaissance. If `start` reports canonical inputs that are not tracked in `state.json`, register them with `checkpoint write --input name=path`. Never clean, reset, stash, or overwrite existing work.

## Choose the route

- Vague idea with no repository: discovery, then the first useful result.
- New repository or product: discovery, project vision/restrictions, sufficient architecture, first marco, then feature cycles.
- Existing feature: focused code recognition, `hybrid-specify`, `hybrid-plan`, `hybrid-slice`, implement, verify, review.
- Small known function/rule: compact `change.md`, behavior case, implementation, verification, review.
- Bug: reproduction, supported cause, regression, correction, verification.
- Internal refactor: preserved behavior, characterization if needed, redesign, equivalence verification.
- Wide migration: expand, migrate in real batches, contract, integration verification.
- Research/prototype: question, experiment and limit, evidence, decision; mark prototype status explicitly.
- Ready diff: fixed baseline, separate Standards and Spec review.

Choose compact, standard, or expanded by uncertainty and risk, not by line count. An existing accepted contract goes directly to its recorded next action; do not repeat discovery/specification/planning by habit. Small known changes use compact mode. If an ambiguity changes behavior, data limits, public compatibility, or authorization, return `needs_input` with concrete options. Record reversible assumptions and continue independent work.

## Output and resumption

Return the protocol in [operating-contract.md](../../shared/references/operating-contract.md): `outcome`, changed artifacts/revisions, findings, evidence refs, and a concrete `next_action`. Read `state.json` before resuming. If inputs changed, run `invalidate --write`, reconcile the affected artifact owner, and do not reuse stale evidence. If no input or evidence changed, continue from the recorded next action without repeating interviews or approvals.

Do not decide the product, impose a stack, publish to a tracker, or implement application code in this skill.

## Bounded delivery

A broad “finish everything” request is delivered through bounded milestones, not one unlimited session. Use at most three related tickets and stop at the first session limit in bounded-execution. Planning and long evaluation are separate milestones. Do not create a Goal unless requested. At the boundary, persist an honest checkpoint and return one short prompt for a new session, including the next authorized effort when this one is complete.
