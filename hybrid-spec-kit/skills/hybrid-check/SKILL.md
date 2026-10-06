---
name: hybrid-check
description: Analyze hybrid artifacts for cross-document inconsistencies or implementation gaps, persist actionable findings, and deduplicate repeated convergence work. Use before implementation for consistency or after changes for convergence.
disable-model-invocation: true
---

# Hybrid check

**Scope:** standard and expanded efforts, when artifacts changed outside the normal flow or a milestone needs a convergence audit. The normal flow already validates through `next`.

Two modes; neither edits the contract to hide a gap:

- `consistency` compares contract, plan, tickets, IDs, references, ownership, and graph;
- `convergence` compares accepted behavior with current code and evidence.

## Run

Run only the requested mode, once per input set: `hybrid check --effort <id> --mode <mode>`. Add `--write` only when the user authorized persisting findings; it deduplicates by effort + origin + gap type + area. An existing open ticket stays the canonical place for a correction.

Then add the judgement the runner cannot make: requirements without tickets, criteria without evidence, contradictory revisions, scope expansion, and code that is missing, partial, contradictory, or unrequested. Each finding cites path/symbol, criterion or rule, consequence, severity, and owner.

With identical inputs and evidence, reuse prior findings and open no new cycle. A necessary in-scope correction goes to its existing ticket; optional improvements go to backlog.

Return mode, findings (new and deduplicated IDs), and the next gate.
