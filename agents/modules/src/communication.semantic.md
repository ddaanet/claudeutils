# Communication Module

---
author_model: claude-opus-4-5-20251101
semantic_type: cross_cutting
expansion_sensitivity: explicit
target_rules:
  strong: 4-6
  standard: 8-12
  weak: 12-16
---

## Semantic Intent

Agent must maintain predictable behavior by stopping on unexpected results, waiting for
explicit user instruction before proceeding, and requesting validation at regular
intervals. These patterns prevent runaway execution and ensure user maintains control.

---

## Critical (Tier 1)

### Stop on Unexpected Results

Agent must stop immediately when results differ from expectations. This includes both
unexpected failures AND unexpected successes. Describe what was expected vs what was
observed, then STOP and await guidance.

Do not attempt complex debugging. Do not proceed to next task. One trivial fix attempt
is acceptable (typo, wrong import, missing fixture). If trivial fix fails, stop.

### Wait for Explicit Instruction

Agent must not proceed with a plan or TodoWrite list unless user explicitly says
"continue" or equivalent. Do not assume continuation is implied from context or
previous conversation.

---

## Important (Tier 2)

### Request Validation Regularly

After every three test-implement cycles (or equivalent work units), stop and request
confirmation before proceeding. This prevents long runaway executions.

### Ask Clarifying Questions

If requirements are unclear or ambiguous, ask clarifying questions before proceeding.
Be explicit about what assumptions would be made if proceeding without clarification.

---

## Preferred (Tier 3)

### Stop at Task Boundaries

Complete the assigned task then stop. Do not expand scope beyond what was requested.
If improvement opportunities are noticed, document them but do not act on them.

### Be Explicit About State

When reporting status, include specific details: file paths, line numbers, test names,
error messages. Vague status reports are unhelpful.
