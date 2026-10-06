---
name: hybrid-review
description: Review a hybrid milestone against repository Standards and the accepted Spec in two independent passes over a fixed baseline, including committed, staged, unstaged, and new files. Use once per milestone, for a ready diff, or for a review-only request.
disable-model-invocation: true
---

# Hybrid review

**Scope:** once per milestone in standard/expanded efforts, or for a review-only request. A compact change is reviewed inside `hybrid-implement`.

Review reports; fixes are a separate, authorized implementation step.

## Fix the scope (one command)

Use the baseline from the checkpoint (or the one the user gives) and capture everything at once:

```text
git status --short && git diff <baseline> --stat && git diff <baseline>
```

`git diff <baseline>` covers committed, staged, and unstaged changes; `git status` lists new untracked files, which you read directly. Without Git, record an inventory fingerprint and the included paths.

## Two independent axes

Run each axis in its own subagent when the harness offers one (so neither contaminates the other); otherwise run them sequentially and keep the notes apart.

- **Standards:** documented repository rules first. Then a judgement-call baseline, overridden by any repository rule: unclear names, duplicated logic, feature envy, data clumps, primitive obsession, repeated switches, shotgun surgery, speculative generality, middle man. Skip anything tooling already enforces.
- **Spec:** each `FR`/`AC` missing, partial, wrong, or exceeded; weakened expected values in tests; non-independent oracles. With no spec, say so.

Each finding cites file/symbol, rule or `AC`, consequence, and severity. Report the axes under separate headings and never rerank across them. Persist a finding with `hybrid finding add` only when it needs tracking.

## Close the gate

When the Spec axis has no blocking finding, mark each reviewed ticket done in one call: `hybrid ticket update --effort <id> --ticket TK-xxx --status done --review passed`. With blocking findings, use `--review changes_requested` and route the fix to the ticket. After a fix, re-review only the changed hunks.

Return baseline, findings per axis, tickets closed, and `next_action`.
