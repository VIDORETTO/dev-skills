---
name: hybrid-start
description: Decide whether a development request needs the hybrid workflow at all, then route or resume it from its checkpoint with the smallest budget. Use when starting, resuming, or triaging a feature, bug, refactor, migration, prototype, or review.
disable-model-invocation: true
---

# Hybrid start

A router with a budget. Its first job is to keep small work out of the kit.

`hybrid <cmd>` below means `python .hybrid/hybrid.py <cmd> --project . --json` (or `python <package>/scripts/hybrid.py` before installation).

## Scope gate (run first, costs no tool call)

Use the kit only when at least one holds:

1. the work spans more than one session or will be handed to another agent or a cheaper model;
2. several behaviors or modules, persistence, a public contract/API, a data migration, or concurrency are involved;
3. the expected behavior is ambiguous enough that a wrong guess means rework;
4. traceable acceptance evidence is required.

Otherwise the request is **direct work**: a typo, docs or config tweak, a single-function change with known behavior, a bug with an obvious fix, a refactor inside one file, a question, or anything you expect to finish in one session in about 20 tool calls. Say so in one line and do it directly, with the repository's normal tests: no artifacts, no runner calls, no further hybrid skills. Follow the user if they insist on the kit.

## Route and budget

| Route | When | Budget |
| --- | --- | --- |
| Direct | scope gate fails | 0 artifacts, 0 runner calls |
| Compact | small but needs a recorded contract or evidence | `change.md` + `evidence run`; ≤2 runner calls; no separate verify/review |
| Standard | gate passes with several behaviors | planning session (discover → specify → plan → slice), then one fresh session per milestone; ≤3 runner calls per ticket |
| Expanded | standard plus large uncertainty, public compatibility, or hard migration | standard plus explicit discovery decisions and expand–contract |

Existing accepted artifacts go straight to their recorded next action; repeat no discovery, interview, or readiness check whose inputs did not change. A bug with unclear cause or a non-reproducible failure follows [diagnosis.md](../../shared/references/diagnosis.md) before any contract work.

## Resume an effort

Run `hybrid next --effort <id> --write` once. It registers canonical inputs, marks stale evidence, selects up to three related tickets, and returns readiness for the first one. Read the ticket file it names and continue with `hybrid-implement`. A failed readiness routes the reported error to the artifact's owner skill. Preserve staged, unstaged, and untracked user work; never clean, reset, or stash it.

## Session boundary

Renew the session at a ticket boundary or near 100k tokens of context. Planning and execution are separate sessions. At a boundary, report the observed result and one short continuation prompt from `next`/`session`; create a Goal only when the user asks ([bounded-execution.md](../../shared/references/bounded-execution.md)).

Return `outcome`, changed artifacts, and `next_action` per [operating-contract.md](../../shared/references/operating-contract.md). This skill does not implement application code or choose the product.
