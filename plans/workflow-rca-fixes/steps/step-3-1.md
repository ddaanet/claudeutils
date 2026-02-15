# Step 3.1

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.1: Add four-status taxonomy and investigation protocol to vet-fix-agent

**Objective**: Create vet-taxonomy.md reference file and update vet-fix-agent to use four-status system with investigation-before-escalation protocol and review-fix integration rule.

**Prerequisites**:
- Read `agent-core/agents/vet-fix-agent.md` (current: 436 lines)
- Note: projected +150 lines exceeds 400-line threshold → split required
- Read `agents/decisions/pipeline-contracts.md` (ODC classification context)

**Implementation**:

**Part A: Create taxonomy reference file**

Create `agent-core/agents/vet-taxonomy.md`:

1. **Four-status definitions**:
   - FIXED: Applied, no action needed
   - DEFERRED: Real issue, explicitly out of scope (maps to scope OUT), informational
   - OUT-OF-SCOPE: Not relevant to current review, informational
   - UNFIXABLE: Technical blocker requiring user decision (with subcategory)

2. **UNFIXABLE subcategory codes**:
   - U-REQ: Requirements ambiguity or conflict
   - U-ARCH: Architectural constraint or design conflict
   - U-DESIGN: Design decision needed, multiple valid approaches

3. **Subcategory examples** (1-2 per code)

4. **Deferred Items report section template**:
   ```
   ## Deferred Items

   The following items were identified but are out of scope:
   - **[Item]** — Reason: [why deferred, reference to scope OUT or design]
   ```

**Part B: Update vet-fix-agent**

Update `agent-core/agents/vet-fix-agent.md`:

1. **Add reference to vet-taxonomy.md**:
   - In frontmatter or early in system prompt
   - "Consult vet-taxonomy.md for status definitions and subcategory codes"

2. **Add 4-gate investigation-before-escalation checklist**:
   - Before classifying UNFIXABLE, must complete:
     1. Check scope OUT list → classify as OUT-OF-SCOPE if listed
     2. Check design for documented deferral → classify as DEFERRED if found
     3. Glob/Grep for existing patterns in codebase → apply pattern if found (FIXED)
     4. Only then classify UNFIXABLE with subcategory code and investigation summary

3. **Add review-fix integration rule (FR-18)**:
   - Before applying fix: Grep target file for heading the fix targets
   - If heading exists: Edit within that section (merge, don't append)
   - If no match: Append as new section
   - Prevents structural duplication from parallel sections

**Expected Outcome**:
- vet-taxonomy.md created with all four statuses, subcategories, examples, template
- vet-fix-agent updated to reference taxonomy, include 4-gate checklist, and merge-not-append fix rule
- Combined file sizes under threshold (taxonomy ~150, vet-fix-agent reduced to ~440)

**Error Conditions**:
- If taxonomy file incomplete → verify all statuses have clear criteria
- If checklist gates vague → add concrete actions for each gate
- If integration rule ambiguous → specify Grep → Edit flow explicitly

**Validation**:
1. Commit both files (taxonomy + vet-fix-agent update)
2. Delegate to agent-creator (plugin-dev): "Review and fix vet-fix-agent.md and vet-taxonomy.md. Verify taxonomy has complete status definitions with examples, vet-fix-agent references taxonomy correctly, 4-gate checklist is concrete, and review-fix integration rule specifies Grep-then-Edit flow."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.1-agent-review.md

---
