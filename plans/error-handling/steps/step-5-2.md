# Step 5.2

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 5

---

## Step 5.2: Add cross-references between error-related fragments

**Objective**: Add "See Also" sections to each error-related fragment pointing to related fragments, enabling navigation across the framework.
**Script Evaluation**: Small (≤25 lines — 2-line See Also additions to 5 files)
**Execution Model**: Opus (fragment artifacts)

**Prerequisite**: Verify all target files exist (Phases 1-4 must be complete). Read each file to find appropriate insertion point (end of file or after final section).

**Implementation**:
Add "**See Also:**" note at the end of each fragment (append, additive only — no modification of existing content):

- `error-handling.md` → "See Also: `error-classification.md` (taxonomy), `escalation-acceptance.md` (resolution criteria), `task-failure-lifecycle.md` (task states), `continuation-passing.md` (CPS chain error protocol)"
- `error-classification.md` → "See Also: `escalation-acceptance.md` (resolution criteria for each category)"
- `escalation-acceptance.md` → "See Also: `error-classification.md` (category definitions), `agent-core/skills/orchestrate/SKILL.md` (recovery protocol)"
- `task-failure-lifecycle.md` → "See Also: `continuation-passing.md` (CPS chain recording), `agent-core/skills/handoff/SKILL.md` (trim rules)"
- `continuation-passing.md` → "See Also: `task-failure-lifecycle.md` (Blockers notation)"

**Expected Outcome**: Each of the 5 target fragments has a See Also note at its end. All additions are ≤2 lines per file.

**Error Conditions**:
- If a target file doesn't exist (Phase dependency not met), STOP and report which step failed

**Validation**:
- `grep "See Also" agent-core/fragments/error-handling.md` returns match
- `grep "See Also" agent-core/fragments/error-classification.md` returns match
- `grep "See Also" agent-core/fragments/escalation-acceptance.md` returns match
- `grep "See Also" agent-core/fragments/task-failure-lifecycle.md` returns match
- `grep "See Also" agent-core/fragments/continuation-passing.md` returns match

---
