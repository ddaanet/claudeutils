# Step 4.1

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 4

---

## Step 4.1: Extend continuation-passing.md with error propagation model

**Objective**: Add error handling section to continuation-passing.md documenting what happens when a skill fails mid-chain — abort protocol, Blockers recording format, pivot transactions, and idempotence requirement.
**Script Evaluation**: Prose (25-100 lines — new section added to existing fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/continuation-passing.md` — understand cooperative skills table and continuation protocol. Read `agent-core/fragments/task-failure-lifecycle.md` (created in Step 3.1) — understand Blockers recording format before documenting it here.

**Implementation**:
Add "## Error Handling" section after the "## Cooperative Skills" table and before "## Adding Continuation to a New Skill":

1. **Error Propagation Model (D-1)**:
   - When a cooperative skill fails mid-execution:
     1. Classify the error as retryable or non-retryable (per error-classification.md decision tree) — informs recorded context, does NOT change immediate response
     2. Abort the remaining continuation — do not propagate to next skill in chain
     3. Record in session.md Blockers section using task-failure-lifecycle.md recording template: error category, retryable classification, which skill failed, what continuation was pending, and resume instructions

2. **Pivot Transactions**:
   - After `/orchestrate` completes its execution phase, compensating for failures becomes impractical (Saga pattern — no rollback for multi-step committed state). These are points-of-no-return in the chain.
   - Chain stages and their pivot status:
     - Before `/orchestrate` begins: all prior artifacts can be revised (non-pivot)
     - After `/orchestrate` completes execution: compensating individual steps impractical (pivot point)
   - If failure occurs after a pivot: record the pivot status in the Blockers entry so user knows compensation context

3. **Recovery Idempotence**:
   - All recovery operations must be idempotent — safe to retry after the user fixes the root cause
   - Idempotence patterns: check-before-write (verify resource doesn't exist before creating), upsert over insert, version-check before overwrite
   - Required because: user may resume with `r` after partial fix, re-executing the last skill's recovery actions

4. **Manual Resume**:
   - User reads the Blockers entry from session.md
   - Fixes the root cause documented in the entry
   - Runs `r` to resume from the recorded chain state
   - The `r` command picks up the in-progress task, which references the continuation state

**Expected Outcome**: Error Handling section present in continuation-passing.md with abort-and-record model, pivot transactions, idempotence requirement, and resume instructions.

**Error Conditions**:
- If task-failure-lifecycle.md recording template format unclear (Step 3.1 not complete), STOP and report dependency not met

**Validation**:
- "Error Handling" or "Error Propagation" heading present in continuation-passing.md
- "Blockers" or "session.md Blockers" referenced (abort-and-record)
- "pivot" or "point-of-no-return" concept present
- "idempotent" or "idempotence" requirement stated
- `grep -n "abort\|Blockers\|pivot\|idempoten" agent-core/fragments/continuation-passing.md` returns 3+ matches

---
