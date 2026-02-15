# Step 2.1

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Step 2.1: Restructure runbook-review.md as type-agnostic

**Objective**: Transform 4 review axes from TDD-only to type-agnostic with TDD/General bullets, add file growth as 5th axis, add behavioral vacuity detection.

**Prerequisites**:
- Read `agents/decisions/runbook-review.md` (current state)
- Read `agents/decisions/pipeline-contracts.md` (T1-T6 defect classification context)

**Implementation**:

Restructure runbook-review.md:

1. **Four axes restructure** (vacuity, ordering, density, checkpoints):
   - For each axis: type-neutral definition, then subsections:
     - **TDD:** [TDD-specific detection criteria]
     - **General:** [General-specific detection criteria]

2. **Add file growth as 5th axis**:
   - Definition: projected file sizes vs 400-line threshold
   - Detection: lines-per-cycle/step projection, split points
   - Both types: cumulative line tracking, split-phase placement

3. **Update process section**:
   - Use "item (cycle or step)" terminology throughout
   - Replace TDD-specific language with type-conditional phrasing

4. **Add behavioral vacuity detection**:
   - **TDD:** For each cycle pair (N, N+1) on same function, verify N+1's RED assertion would fail given N's GREEN. If not, cycles are behaviorally vacuous.
   - **General:** For consecutive steps modifying same artifact, verify step N+1 produces outcome not achievable by extending step N's implementation alone. If achievable, steps should be merged.
   - **Heuristic (both):** cycles/steps > LOC/20 signals consolidation needed.

**Expected Outcome**: runbook-review.md has 5 type-agnostic axes, behavioral vacuity detection for both types, and type-neutral process terminology.

**Error Conditions**:
- If axes remain TDD-specific → verify General subsections added
- If vacuity detection vague → add concrete verification steps
- If terminology inconsistent → grep for TDD-only terms, replace with item/cycle/step conditionals

**Validation**:
1. Commit changes
2. Delegate to vet-fix-agent: "Review runbook-review.md restructuring. Verify all 5 axes have type-agnostic definitions with TDD/General subsections, behavioral vacuity detection is concrete, and process section uses conditional terminology."
3. Read review report, grep for UNFIXABLE
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-2.1-vet-review.md

---
