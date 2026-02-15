# Step 2.3

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Step 2.3: Add LLM failure mode gate to runbook Phase 0.95

**Objective**: Add inline validation step in Phase 0.95 before fast-path promotion to check vacuity, ordering, density, checkpoints.

**Prerequisites**:
- Read `agent-core/skills/runbook/SKILL.md` Phase 0.95 section
- Step 2.1 committed (criteria reference from runbook-review.md)

**Implementation**:

In Phase 0.95 (Outline Sufficiency Check), add validation step before promotion:

1. **Gate placement**: After sufficiency criteria check, before "If sufficient → promote outline to runbook"

2. **Gate content**:
   ```
   **LLM failure mode gate (before promotion):**
   Check for common planning defects (criteria from runbook-review.md updated in Step 2.1):
   - Vacuity: any items that only create scaffolding without functional outcome?
   - Ordering: any items referencing structures from later items?
   - Density: adjacent items on same function with <1 branch difference?
   - Checkpoints: gaps >10 items without checkpoint?
   Fix inline before promotion. If unfixable, fall through to Phase 1 expansion.
   ```

3. **Integration**: Gate runs before promotion decision, fixes applied inline, unfixable issues trigger normal Phase 1 path.

**Expected Outcome**: Phase 0.95 has inline LLM failure mode check preventing defective outlines from fast-path promotion.

**Error Conditions**:
- If gate criteria vague → reference specific runbook-review.md sections
- If gate placement wrong → ensure it's before promotion, after sufficiency
- If unfixable path unclear → specify fallthrough to Phase 1

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook Phase 0.95 LLM failure mode gate addition. Verify gate checks all 4 criteria, placement before promotion is correct, and unfixable fallthrough is clear."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-2.3-skill-review.md

---

**Phase 2 Checkpoint**:
1. All review logic updated (runbook-review.md, review-plan, runbook skill)
2. No restart required (decision documents and skills loaded on demand, not at startup)
3. Proceed to Phase 3

---


**Complexity:** High (3 steps, ~300 lines including taxonomy split)
**Model:** Sonnet
**Restart required:** Yes (agent definition + fragment changes)
**Diagnostic review:** Yes (improving vet tools)
**FRs addressed:** FR-7, FR-8, FR-9, FR-10, FR-18

---
