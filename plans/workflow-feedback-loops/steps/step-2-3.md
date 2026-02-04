# Step 2.3

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet

---

## Step 2.3: Enhance tdd-plan-reviewer

**Objective:** Add outline validation without changing fix policy

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/tdd-plan-reviewer.md`:

1. Add outline validation:
   - When reviewing TDD runbook, check if `plans/<job>/reports/runbook-outline-review.md` exists
   - If outline review missing, warn that outline was not reviewed

2. Add requirements inheritance:
   - Verify runbook covers outline's requirements mapping

3. Preserve review-only behavior:
   - Do NOT change fix policy
   - Caller (planner) applies fixes with full context

**Reference:** Design Section "ENHANCED: vet-agent / tdd-plan-reviewer" lines 384-390

**Expected Outcome:** Agent warns about missing outline review

**Success Criteria:**
- Outline review check added
- Fix policy unchanged
- Requirements inheritance mentioned

---
