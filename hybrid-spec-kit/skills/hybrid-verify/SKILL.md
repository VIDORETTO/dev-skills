---
name: hybrid-verify
description: Re-verify stale evidence, external or manual procedures, and milestone gates for a hybrid effort, recording observed results and limitations. Use when evidence became stale, a check needs a service or a human, or a delivery gate requires a full run.
disable-model-invocation: true
---

# Hybrid verify

**Scope:** standard and expanded efforts. The normal path records evidence in `hybrid-implement` with `evidence run`; use this skill only for:

- evidence that `next` reported stale;
- procedures the runner cannot execute (manual UI inspection, an unavailable service, a production metric);
- a milestone or delivery gate that requires a full suite.

## Record

- An executable command goes through `hybrid evidence run ... --command "<exact command>" --path <path>`, which observes the exit code itself.
- A manual or external procedure goes through `hybrid evidence add ... --procedure "<what was done>" --result <passed|failed|partial> --executed --path <path> --observations "<what was observed>"`. The record stays attested, not runner-observed.
- When a procedure cannot run, record `--result not_run` with the concrete impediment.

Record one result per meaningful procedure, covering all its `AC` refs. Reuse unchanged valid evidence. A screenshot proves one rendered state; a business metric that needs real use stays pending and is reported separately.

For an external evaluator, qualify it on a small sample first, then run the accepted full set with frozen inputs. Its process and progress location go into the checkpoint.

Return procedures, `EV` refs, limitations, and `next_action`. A verification-only request changes no code.
