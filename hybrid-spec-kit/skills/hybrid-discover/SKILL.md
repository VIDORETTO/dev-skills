---
name: hybrid-discover
description: Clarify a development demand, its outcome, constraints, hypotheses, and material decisions before specification. Use for vague ideas, new projects, ambiguous features, research, prototypes, bugs with uncertain expectations, or migrations with open compatibility questions.
disable-model-invocation: true
---

# Hybrid discovery

**Scope:** only for work that passed the `hybrid-start` scope gate. A clear small request skips discovery entirely.

Reach enough shared understanding for the next deliverable, and stop there.

## Interview in rounds

1. Facts are your job: read the repository, instructions, `CONTEXT.md` and ADRs as far as a question needs. Decisions belong to the user.
2. Build the decision tree. The **frontier** is every decision whose prerequisites are settled. Ask the whole frontier in one round, most impactful first, each with your recommendation:

   ```text
   ❓ Q1 — <title>: <question and options>
   ➡️ <recommended answer and its consequence>
   ```

3. Wait for answers, recompute the frontier, and ask the next round. A question that depends on an open one waits. Record a reversible assumption instead of asking about it.
4. By type: an idea records evidence for/against, cost of inaction and a stop criterion; a bug records expected vs observed behavior and the reproduction; research records the experiment and its limit; a migration lists consumers and expand–contract assumptions.

When the answer belongs to someone who is not in the conversation (client, PO, another team), write `specs/<id>/questions.md`: purpose, one paragraph of context, one single-idea question per heading, most important first, answer stub under each. Return `needs_input` pointing to it.

## Exit

Done when no open question changes the next behavior, validation, or authorization. Write a discovery artifact only if a later phase consumes it. Hand durable terms to `hybrid-domain` and behavior to `hybrid-specify`. If the user decides not to build, record the reason and stop. A resumed discovery reads its checkpoint and asks nothing already answered.

Return `outcome` (`needs_input` for a material choice), artifacts, and `next_action`.
