# Step 2.4

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Step 2.4: Enhance vet-fix-agent

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
