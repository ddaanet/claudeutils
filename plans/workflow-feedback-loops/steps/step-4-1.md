# Step 4.1

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Step 4.1: Update prepare-runbook.py

**Objective:** Add Phase metadata to step file frontmatter

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/bin/prepare-runbook.py`:

1. Extract phase number from step headers:
   - Parse `## Phase N` headers in runbook
   - Track current phase as steps are processed
   - For flat runbooks (no phase headers), use phase 1

2. Add Phase field to step file frontmatter:
   - Each step file gets `phase: N` in YAML frontmatter
   - Enables orchestrator phase boundary detection

3. Validation:
   - Warn if phase numbers have gaps
   - Error if phase numbers decrease (non-monotonic)

**Reference:** Design Section "Implementation Notes" line 540

**Expected Outcome:** Step files include phase metadata for orchestrator

**Success Criteria:**
- Step files have `phase: N` in frontmatter
- Phase extraction handles both flat and grouped runbooks
- Validation catches phase ordering issues

---
