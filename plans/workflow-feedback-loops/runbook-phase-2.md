## Phase 2: Enhanced Agents

### Step 2.1: Enhance design-vet-agent

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

### Step 2.2: Enhance vet-agent

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

### Step 2.3: Enhance tdd-plan-reviewer

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

### Step 2.4: Enhance vet-fix-agent

**Objective:** Add runbook rejection and requirements context requirement

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/agents/vet-fix-agent.md`:

1. Add explicit runbook rejection to Step 0:
   - If task prompt contains path to `runbook.md` → reject with error
   - Error message: "This agent reviews implementation changes, not planning artifacts. Use vet-agent for runbook review."

2. Add requirements context requirement:
   - Document that prompt MUST include requirements summary
   - Example format from design Section FP-5

3. Document scope explicitly:
   - Agent reviews implementation changes (code, tests)
   - Agent does NOT read runbook.md
   - Input is changed file list, not git diff text

**Reference:** Design Section "FP-5: Phase Boundary Review (ENHANCED)" lines 285-334

**Expected Outcome:** Agent rejects runbook paths, requires requirements context

**Success Criteria:**
- Step 0 includes runbook rejection logic
- Documentation requires requirements in prompt
- Scope is explicit (implementation only)
