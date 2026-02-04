# Step 2.2

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet

---

## Step 2.2: Enhance vet-agent

**Objective:** Add outline validation without changing fix policy

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/vet-agent.md`:

1. Add outline validation to Step 0:
   - When reviewing runbook, check if `plans/<job>/reports/runbook-outline-review.md` exists
   - If outline review missing, warn (not error) that outline was not reviewed

2. Add requirements inheritance check:
   - Verify runbook covers outline's requirements mapping
   - If outline exists, compare coverage

3. Preserve review-only behavior:
   - Do NOT change fix policy
   - Caller (planner) applies fixes with full context

**Reference:** Design Section "ENHANCED: vet-agent / tdd-plan-reviewer" lines 384-390

**Expected Outcome:** Agent warns about missing outline review

**Success Criteria:**
- Outline review check added
- Fix policy unchanged (remains review-only)
- Requirements inheritance mentioned

---
