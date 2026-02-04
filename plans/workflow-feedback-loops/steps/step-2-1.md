# Step 2.1

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet

---

## Step 2.1: Enhance design-vet-agent

**Objective:** Extend design-vet-agent with fix-all policy and explicit requirements validation

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/design-vet-agent.md`:

1. Add explicit requirements input validation to Step 0:
   - Before review, verify requirements exist (plans/<job>/requirements.md OR requirements section in design)
   - If requirements missing, return structured error with recommendation

2. Extend fix policy from critical/major to fix-all:
   - Change instructions to apply ALL fixes (critical, major, AND minor)
   - Rationale: Document fixes are low-risk; earlier cleanup saves iteration

3. Enhance requirements traceability verification:
   - Existing Step 4.5 validates traceability table exists
   - Enhance to verify completeness: every FR-* has corresponding design element

**Reference:** Design Section "FP-2: Design Review (ENHANCED)" lines 149-166

**Expected Outcome:** Agent applies all fixes, validates requirements exist

**Success Criteria:**
- Step 0 includes requirements existence check
- Fix policy explicitly says "apply ALL fixes including minor"
- Traceability verification is more thorough

---
