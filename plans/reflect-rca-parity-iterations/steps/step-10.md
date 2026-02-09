# Step 10

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 10: Add Explicit Alignment Criterion to vet-fix-agent

**Objective:** Update vet-fix-agent to include alignment checking as a standard review criterion (not conditional on design reference presence).

**Design Reference:** DD-5 (design lines 121-135)

**File:** `agent-core/agents/vet-fix-agent.md` (existing, edit)

**Current State:**
- Review protocol has "Design anchoring" as a dimension when design reference provided
- Alignment (does implementation match spec?) is broader than design anchoring

**Changes Required:**

Locate review criteria section (likely within "### 3. Review Changes" or similar). Add explicit alignment criterion (~5 lines):

```markdown
**Alignment:**
- Does the implementation match stated requirements and acceptance criteria?
- For work with external references (shell scripts, API specs, mockups): Does implementation conform to the reference specification?
- Check: Compare implementation behavior against requirements summary (provided in task prompt)
- Flag: Deviations from requirements, missing features, behavioral mismatches
```

**Integration:**
- This becomes a standard review dimension alongside code quality, test coverage, design anchoring, etc.
- When design includes external reference, alignment includes conformance checking
- Not a separate "conformance mode" — alignment is always-on

**Implementation:**

1. Locate review protocol section (search for "### 3. Review Changes" or "Review dimensions")
2. After existing review criteria (code quality, design anchoring, etc.), add "Alignment" criterion
3. Integrate with existing protocol — alignment check happens during step 3 review

**Expected Outcome:**
- Alignment criterion added to standard review protocol
- Conformance checking is a special case of alignment (when external reference present)
- Not a conditional mode — alignment always checked

**Validation:**
- Read updated vet-fix-agent.md
- Verify alignment criterion added to review protocol
- Verify criterion explains both general alignment and conformance special case

**Success Criteria:**
- ~5 lines added to vet-fix-agent.md review protocol
- Alignment criterion present with check and flag guidance
- Conformance mentioned as special case (external references)

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-10-execution.md`

---


**Completion Criteria:**
- Step 9: plan-tdd and plan-adhoc both updated with conformance requirements (~30 lines total across 2 files)
- Step 10: vet-fix-agent updated with alignment criterion (~5 lines)
- All Phase 3 changes committed

**Verification:**
- Gap 1 (conformance test cycles) implemented via Step 9
- N2 (vet alignment) implemented via Step 10
- Gap 4 prerequisite satisfied (Phase 2 Steps 4-5 committed before Phase 3 started)

**Next Phase:** Phase 4 (Memory index update — final step)
# Phase 4: Memory Index Update

**Scope:** 1 step, ~16 index entries (~20-25 total lines), single session
**Model:** Haiku execution
**Complexity:** Low (append-only operation)

---
