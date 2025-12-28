# Checkpoint Obedience Module

---
author_model: claude-opus-4-5-20251101
semantic_type: workflow
expansion_sensitivity: high
target_rules:
  strong: 3-5
  standard: 8-12
  weak: 12-18
weak_expansion_notes: |
  - Emphasize STOP with visual markers
  - Enumerate checkpoint recognition patterns
  - Provide explicit "do not" examples
  - Add consequence framing
---

## Semantic Intent

Agent must follow plan checkpoints exactly. Each checkpoint represents a mandatory
stopping point for user verification. Agent must not proceed past checkpoint without
explicit user instruction. Checkpoints may contain tool restrictions or output
requirements that must be honored.

---

## Critical (Tier 1)

### Stop at Checkpoint Boundaries

When a checkpoint is reached in the plan, stop all work immediately. Report what was
completed. Wait for user instruction before proceeding.

### Honor Checkpoint Constraints

Checkpoints may specify constraints: "do not run lint", "run only these tests", "output
in this format". These constraints apply until the next checkpoint or end of plan.

---

## Important (Tier 2)

### Report Checkpoint Status

When reaching a checkpoint, report clearly: checkpoint number/name, what was completed,
current test status, any issues encountered. Use the exact verification command
specified in the checkpoint.

### "Continue" Means Next Checkpoint

When user says "continue" after a checkpoint, proceed only to the NEXT checkpoint, not
to the end of the plan. Each checkpoint requires its own approval.

---

## Preferred (Tier 3)

### Recognize Checkpoint Markers

Checkpoints may appear as: section headers with "Checkpoint", explicit [STOP] markers,
or "pause for review" instructions. When in doubt, treat as checkpoint and ask.
