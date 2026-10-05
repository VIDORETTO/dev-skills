---
name: hybrid-verify
description: Execute a hybrid ticket's behavior and regression verification, record current evidence with tested revisions and limitations, and advance only evidence-supported status. Use after implementation or when rechecking changed/stale inputs.
disable-model-invocation: true
---

# Hybrid verify

Verification proves observed behavior against acceptance criteria; it does not repair code silently. Read the ticket, contract, plan verification strategy, current instructions, and existing evidence. Check freshness with `invalidate --effort <id> --json` before reusing results, once per relevant input set; do not rerun after an unrelated poll/read.

## Execute and record

1. Use the exact command/procedure recorded in the ticket and plan, from the stated directory and environment. If it is only present in configuration, label it observed but not executed.
2. Cover every selected `AC` at its planned seam. Add UI inspection/interactions, representative persistence/concurrency, migration compatibility, adapter contract, or post-use procedure when the plan requires them.
3. Record each result with:

```text
python <package-root>/scripts/hybrid.py evidence add --project . --effort <id> --ticket TK-xxx --acceptance-refs AC-001 --procedure "<exact command>" --result passed --executed --path <path> --observations "<observed result>"
```

Use `not_run` for unavailable tests and state the concrete impediment; use `partial` for partial coverage; never turn a failed or unexecuted command into `passed`. In compact mode omit `--ticket`; the runner associates the record with `change.md`. The runner stores `EV-xxx`, environment, timestamp, input fingerprints, and a projection in `verification.md`.

4. If code, spec, plan, acceptance, environment, or relevant dependency changed, mark affected evidence `stale` with `invalidate --write`, then rerun. Do not let a hash change silently decide semantic impact; record the classification.
5. Advance a ticket to `verified` only when its required acceptance refs have current passed evidence. `done` also requires the review gate; a checkbox is not an evidence record.

For business metrics that need real use, report technical delivery separately and leave the metric pending. A screenshot proves one rendered state only; it does not prove persistence or authorization.

Return exact procedures, result IDs, tested revision, limitations, stale refs, and next action. A verification-only request does not modify code.

## Verification economy

Use the [bounded execution policy](../../shared/references/bounded-execution.md). Record one evidence result per meaningful procedure/scope with all applicable AC refs, not one per assertion or poll. Reuse unchanged valid evidence; rerun the affected checks after changes and required global gates at their specified milestone. Qualify an external evaluator with a small diagnostic sample before the accepted full run; preserve its required sample size and stopping rules. Keep long-running evaluation in its own milestone, with process/progress location in the handoff.
