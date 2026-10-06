---
name: hybrid-implement
description: Execute one ready hybrid ticket (or a compact change) as a focused vertical slice with behavior-first tests, minimal code, runner-recorded evidence, and honest status. Use when implementing an accepted ticket or the equivalent compact change.
disable-model-invocation: true
---

# Hybrid implement

**Scope:** only for work that passed the `hybrid-start` scope gate. Direct work is implemented without this skill.

The ticket (or `change.md`) is the whole execution context; the planning conversation is not needed.

## Start: one call

- Standard: `hybrid next --effort <id> --write`. Continue only when `ticket.ready` is true; otherwise return its `errors`/`blockers` to the planner, keeping your edits. Then `hybrid ticket update --effort <id> --ticket TK-xxx --status in_progress`.
- Compact: read `change.md`; no runner call is needed to start.

Read the ticket's "Leitura em ordem" paths and nothing broader.

## Loop, one behavior at a time

1. Write the next behavior case at the agreed seam, with an independent oracle: a literal, a property, or an accepted example. Internal modules stay unmocked.
2. Run it and see red caused by missing or wrong behavior. An environment or import error is not a valid red.
3. Make the smallest change that turns it green, then run the focused regression. Refactor only with the suite green.

Run the focused test file while iterating and the ticket's validation command once at the end. Details are in [testing.md](../../shared/references/testing.md), read it only when a seam or oracle is unclear.

## Close: evidence in the same run

Run the final validation through the runner. It executes the command, records the evidence, and advances the ticket:

```text
hybrid evidence run --effort <id> --ticket TK-xxx --acceptance-refs AC-001,AC-002 --command "<exact validation command>" --path <code path> --path <test path>
```

- `passed` with every ticket `AC` covered → the ticket becomes `verified`. No separate `hybrid-verify` is needed.
- `failed` → fix and rerun; the output tail is in the response.
- Compact: omit `--ticket`, then check the diff against `change.md` yourself (`git diff --stat` + `git diff`). That is the whole review for compact work.

Keep acceptance text, expected results, scope, and public/data contracts exactly as given. A new decision, incompatible path, unplanned dependency, or repeated failure without new evidence goes back to the planner with ticket, step, evidence, work done, decision needed, and impact.

Commit, publish, and deploy only when asked. Return changed files, ticket status, `EV` refs, pending work, and `next_action`: the next ticket in the same session if it is in `queue` and context is below ~100k tokens; otherwise `hybrid-review` for the milestone and a continuation prompt.
