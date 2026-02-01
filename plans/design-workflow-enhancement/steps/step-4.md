# Step 4

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 4: Update plan-adhoc/SKILL.md with Documentation Perimeter

**Objective**: Add documentation perimeter loading to Point 0.5 (Discover Codebase Structure).

**Execution Model**: Sonnet

**Implementation**:

Read `agent-core/skills/plan-adhoc/SKILL.md` and add documentation perimeter loading step.

**Change Location**: Point 0.5 section (starts at line 95)

**Add as Step 0 Before Existing Numbered Steps**:

Insert before existing "1. **Discover relevant prior knowledge:**":

```markdown
0. **Load documentation perimeter from design (if exists):**
   - If design document exists, read "Documentation Perimeter" section
   - Load all files listed under "Required reading"
   - Execute Context7 queries listed under "Context7 references"
   - Note "Additional research allowed" guidance
   - If no design document or no perimeter section, proceed to step 1
```

Preserve existing steps 1-2 unchanged.

**Integration Notes**:
- Documentation perimeter is loaded FIRST (when it exists) as step 0
- Existing steps 1-2 (memory-index discovery, file verification) still run unchanged
- Perimeter provides designer's recommended context; discovery validates/extends it

**Expected Outcome**: Planning skill reads documentation perimeter section from design (when exists) before existing discovery steps.

**Unexpected Result Handling**:
- If step numbering conflicts: Renumber existing steps accordingly
- If discovery steps already reference design document: Integrate perimeter loading with existing references

**Error Conditions**:
- File not found → Escalate to sonnet
- Section structure unclear → Escalate to sonnet

**Validation**:
- Documentation perimeter step added before existing discovery
- Conditional logic (skip if no design/no perimeter) included
- Integration preserves existing discovery steps

**Success Criteria**:
- Point 0.5 includes documentation perimeter loading as step 0
- Conditional logic (skip if no design/perimeter) included
- Existing steps 1-2 (memory-index, file verification) preserved

**Report Path**: `plans/design-workflow-enhancement/reports/step-4-update-plan-adhoc.md`

---
