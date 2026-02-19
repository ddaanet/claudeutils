# Step 5.3

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 5

---

## Step 5.3: Cross-document terminology consistency review

**Objective**: Read all error-related artifacts and verify terminology is consistent across documents. Fix any discrepancies found.
**Script Evaluation**: Prose (review pass — read 7 files, targeted edits where discrepancies found)
**Execution Model**: Opus (all targets are architectural artifacts)

**Prerequisite**: All of Phases 1–4 must be complete. Read all 7 target files before assessing consistency.

**Implementation**:
Read all 7 files: `error-handling.md`, `error-classification.md`, `escalation-acceptance.md`, `task-failure-lifecycle.md`, `continuation-passing.md`, `orchestrate/SKILL.md`, `handoff/SKILL.md`.

Check for consistency across documents:
1. **Fault/failure vocabulary**: "fault" and "failure" used identically per Avižienis FEF chain (categories 1&4=faults, 2&3=failures, 5=neither — it's a misalignment, not categorized in FEF)
2. **Retryable/non-retryable**: same definition (transient vs deterministic) and same examples across every document that uses these terms
3. **State notation**: `[!]` blocked, `[✗]` failed, `[–]` canceled used identically wherever referenced
4. **Acceptance criteria**: D-3's three criteria (precommit, clean tree, output validation) referenced consistently when mentioned

For each discrepancy found: apply targeted fix (edit the document with the inconsistency to match the authoritative source — error-classification.md for taxonomy, task-failure-lifecycle.md for state notation, escalation-acceptance.md for acceptance criteria).

If no discrepancies found: confirm consistency in report, no edits needed.

Write report to: `plans/error-handling/reports/step-5.3-consistency.md`

**Expected Outcome**: Report documents which terminology checks passed, which had discrepancies, and what fixes were applied (or confirms no fixes needed). All 7 documents use consistent terminology.

**Error Conditions**:
- If a fundamental contradiction is found (two documents define the same term incompatibly and neither is clearly correct per the design outline), STOP and escalate to user

**Validation**:
- Report file exists at `plans/error-handling/reports/step-5.3-consistency.md`
- Report confirms all 4 consistency checks (fault/failure, retryable, state notation, acceptance criteria)
- If fixes applied: each fix targets specific document with specific change
