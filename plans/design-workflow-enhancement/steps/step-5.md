# Step 5

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 5: Update plan-tdd/SKILL.md with Documentation Perimeter

**Objective**: Add documentation perimeter loading to Phase 1 (Intake).

**Execution Model**: Sonnet

**Implementation**:

Read `agent-core/skills/plan-tdd/SKILL.md` and add documentation perimeter loading.

**Change Location**: Phase 1 section (starts at line ~104, has "Actions:" list with 4 items, not "Steps:")

**Add as Action 0 Before Existing Numbered Actions**:

Insert under "**Actions:**" heading, before existing action 1:

```markdown
0. **Load documentation perimeter from design:**
   - Read "Documentation Perimeter" section from design document
   - Load all files listed under "Required reading"
   - Execute Context7 queries listed under "Context7 references"
   - Note "Additional research allowed" guidance
```

Preserve existing actions 1-4 unchanged (no renumbering needed if we use 0).

**Integration Notes**:
- Documentation perimeter loads before existing Phase 1 actions (as action 0)
- TDD workflow always has design document (prerequisite)
- Using "0" for new action avoids renumbering existing 1-4

**Expected Outcome**: TDD planning skill reads documentation perimeter before existing intake actions.

**Unexpected Result Handling**:
- If Phase 1 uses "Steps:" instead of "Actions:": Adapt to match terminology
- If numbering scheme conflicts with adding 0: Start at 1 and renumber existing to 2-5

**Error Conditions**:
- File not found → Escalate to sonnet
- Phase structure unclear → Escalate to sonnet

**Validation**:
- Documentation perimeter step added as first step in Phase 1
- Existing intake steps preserved (possibly renumbered)
- No conditional logic needed (design always exists in TDD workflow)

**Success Criteria**:
- Phase 1 includes documentation perimeter loading as action 0
- Existing actions 1-4 preserved unchanged
- Action ordering is logical

**Report Path**: `plans/design-workflow-enhancement/reports/step-5-update-plan-tdd.md`

---
