# Step 6.1

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Step 6.1: Delete Phase 1.4 from runbook skill

**Objective**: Remove obsolete Phase 1.4 (file size awareness) section from runbook skill, now redundant with outline-level enforcement from Phase 4.

**Prerequisites**:
- Read `agent-core/skills/runbook/SKILL.md` to locate Phase 1.4 section
- Step 4.1 committed (outline-level growth validation as replacement)

**Implementation**:

Update `agent-core/skills/runbook/SKILL.md`:

1. **Locate Phase 1.4 section**:
   - Section title: "Phase 1.4: File Size Awareness"
   - Content: convention for noting file sizes during item planning

2. **Delete entire section**:
   - Remove heading, content, examples
   - Update section references if Phase 1.4 mentioned elsewhere in skill
   - Update table of contents if present

3. **Verify no orphaned references**:
   - Grep runbook SKILL.md for "1.4", "file size awareness", "file growth" in Phase 1 context
   - Remove or update any cross-references

**Expected Outcome**: Phase 1.4 section deleted from runbook skill, no orphaned references remain, outline-level enforcement (from Phase 4) is now the mechanism.

**Error Conditions**:
- If section not found → verify current Phase 1.4 exists with Grep
- If orphaned references remain → update cross-references or table of contents
- If deletion breaks section numbering → phases are named, not strictly numbered (acceptable)

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook skill Phase 1.4 deletion. Verify entire section removed, no orphaned references remain, and skill structure is intact."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-6.1-skill-review.md

---
