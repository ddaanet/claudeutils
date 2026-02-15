# Step 6.2

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Step 6.2: Document execution-to-planning feedback requirement

**Objective**: Add execution-to-planning feedback requirement to orchestration-execution.md, documenting when local recovery is insufficient and global replanning is needed.

**Prerequisites**:
- Read `agents/decisions/orchestration-execution.md` (current execution patterns)
- Read `agents/decisions/workflow-core.md` (workflow context)

**Implementation**:

Update `agents/decisions/orchestration-execution.md`:

1. **Add new section**: "Execution-to-Planning Feedback" or integrate into existing error handling section

2. **Document three escalation tiers**:
   - **Item-level (UNFIXABLE)**: execution blocked by missing design decision → orchestrator stops, escalates to user
   - **Local recovery (refactor agent)**: implementation needs restructuring within same design → delegate to refactor agent, continue
   - **Global replanning (new)**: execution reveals design flaw requiring replanning → stop execution, return to planning phase

3. **Global replanning triggers**:
   - Design assumptions invalidated by implementation (e.g., "this API doesn't support X" when design assumed it did)
   - Scope creep detected during execution (multiple UNFIXABLE of same type indicating missing phase)
   - Runbook structure broken (dependency cycles, blocked items accumulating)
   - Test plan inadequate (coverage gaps discovered during implementation)

4. **Handoff to error-handling worktree**:
   - Note: FR-17 documents requirement only
   - Implementation: deferred to `wt/error-handling` worktree
   - That worktree will design concrete detection, escalation protocol, and replanning handoff

**Expected Outcome**: orchestration-execution.md has three-tier escalation model with global replanning triggers documented and implementation deferred to wt/error-handling.

**Error Conditions**:
- If tiers unclear → add concrete examples for each tier
- If global triggers vague → specify detection criteria or symptoms
- If handoff note missing → ensure FR-17 implementation deferral is explicit

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review orchestration-execution.md execution-to-planning feedback addition. Verify three escalation tiers are documented with distinctions, global replanning triggers are concrete, and implementation deferral to wt/error-handling is clear."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-6.2-vet-review.md

---

**Phase 6 Checkpoint**:
1. Final cleanup complete (Phase 1.4 deleted, execution feedback documented)
2. All 20 FRs implemented across 6 phases
3. No restart required (no agent/fragment loaded via CLAUDE.md changed)
4. Runbook execution complete

---
