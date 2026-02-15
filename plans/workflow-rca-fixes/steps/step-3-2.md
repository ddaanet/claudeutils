# Step 3.2

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: opus
**Phase**: 3

---

## Step 3.2: Update vet-requirement.md (UNFIXABLE validation + execution context enforcement)

**Objective**: Add UNFIXABLE validation steps and strengthen execution context requirements in vet-requirement.md.

**Dependencies**: Step 3.1 (vet-taxonomy.md must exist and be committed)

**Prerequisites**:
- Read `agent-core/fragments/vet-requirement.md` (current state)
- Step 3.1 committed (vet-taxonomy.md available as reference)

**Implementation**:

Update `agent-core/fragments/vet-requirement.md`:

1. **Update "Three issue statuses" → "Four issue statuses"**:
   - Add OUT-OF-SCOPE status between DEFERRED and UNFIXABLE
   - Align descriptions with vet-taxonomy.md
   - Four statuses: FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE

2. **Add UNFIXABLE validation steps** (after grep-for-UNFIXABLE in detection protocol):
   - Check each UNFIXABLE has subcategory code (U-REQ, U-ARCH, U-DESIGN)
   - Check each has investigation summary showing 4-gate checklist completion
   - Cross-reference against scope OUT list (should not overlap)
   - If validation fails: Resume agent for reclassification with guidance

3. **Strengthen execution context section** (FR-10):
   - Add requirement: IN/OUT scope fields must be structured lists, not empty prose
   - Add enforcement language: "Fail loudly if fields are missing or unstructured"
   - Add template example showing proper IN/OUT structure
   - Specify: OUT section prevents false positives, IN section grounds review

**Expected Outcome**: vet-requirement.md has four-status taxonomy, concrete UNFIXABLE validation with resume protocol, and strict execution context enforcement.

**Error Conditions**:
- If status descriptions diverge from taxonomy → align with vet-taxonomy.md
- If validation steps non-actionable → specify what to check and how
- If execution context enforcement vague → add "must" language and fail conditions

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review vet-requirement.md updates using vet-taxonomy.md from Step 3.1. Verify four statuses align with taxonomy, UNFIXABLE validation is concrete and includes resume protocol, and execution context section has strict enforcement guidance with structured field requirements."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-3.2-vet-review.md

---
