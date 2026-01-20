# Step 9

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 9: Validation Test

**Objective**: Test /plan-tdd skill with sample design document.

**Script Evaluation**: Medium task (test execution)

**Execution Model**: Haiku

**Tool Usage**:
- Use Write to create sample design doc
- Invoke /plan-tdd skill
- Use Read to verify generated runbook
- Use Bash to run prepare-runbook.py on output

**Implementation**:

1. Create minimal sample design document at `plans/plan-tdd-skill/test-design.md`:
   - Goal: Simple authentication feature
   - 2-3 design decisions
   - 2 behavioral increments (2 cycles expected)

2. Invoke /plan-tdd skill with sample design doc:
   - Should generate runbook at `plans/test-auth/runbook.md`
   - Verify file created

3. Validate runbook format:
   - Has YAML frontmatter with `type: tdd`
   - Has Weak Orchestrator Metadata section
   - Has Common Context section
   - Has 2 Cycle sections (`## Cycle 1.1:`, `## Cycle 1.2:`)
   - Each cycle has RED Phase, GREEN Phase, Stop Conditions

4. Test prepare-runbook.py compatibility:
   ```bash
   python3 agent-core/bin/prepare-runbook.py plans/test-auth/runbook.md
   ```
   - Should create `.claude/agents/test-auth-task.md`
   - Should create `plans/test-auth/steps/cycle-1-1.md` and `cycle-1-2.md`
   - Should create `plans/test-auth/orchestrator-plan.md`

5. Document results in `plans/plan-tdd-skill/reports/step-9-validation.md`:
   - Test design doc used
   - Generated runbook format validation
   - prepare-runbook.py output
   - Any issues found

**Expected Outcome**: Successful test with valid TDD runbook generation and prepare-runbook.py processing.

**Unexpected Result Handling**:
- If /plan-tdd skill invocation fails → Document error, STOP
- If runbook format invalid → Document specific issue, STOP
- If prepare-runbook.py fails → Document error, STOP

**Error Conditions**:
- Sample design doc creation fails → STOP, report error
- Skill invocation error → STOP, report error details
- Validation failures → STOP, report specific validation issues

**Validation**:
- Generated runbook exists
- Runbook has correct format (type: tdd, cycles, sections)
- prepare-runbook.py completes successfully
- All expected artifacts created

**Success Criteria**:
- /plan-tdd skill successfully generates valid TDD runbook
- Runbook compatible with prepare-runbook.py
- All execution artifacts created correctly
- No errors during test execution

**Report Path**: `plans/plan-tdd-skill/reports/step-9-validation.md`

---
