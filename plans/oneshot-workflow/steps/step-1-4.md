# Phase 1 Execution - Step 4

**Plan**: `plans/oneshot-workflow/phase1-execution-plan.md`
**Common Context**: See plan file for script specification, baseline rename info, and file structure

---

## Step 1.4: Test Script with Phase 2 Runbook

**Objective**: Verify script works correctly with existing Phase 2 execution plan

**Script Evaluation**: Prose description (test execution with multiple verification steps)

**Execution Model**: Haiku

**Implementation**:

**Part A: Prepare test environment**
1. Ensure clean state (remove any previous test outputs)
2. Verify test runbook exists: `plans/unification/phase2-execution-plan.md`

**Part B: Execute script**
```bash
cd /Users/david/code/claudeutils
python3 /Users/david/code/agent-core/bin/prepare-runbook.py \
    plans/unification/phase2-execution-plan.md
```

**Part C: Verify outputs**

Check created files (Note: runbook name is derived from parent directory `unification`, not filename):
1. Plan-specific agent: `.claude/agents/unification-task.md`
   - Verify file exists
   - Verify contains baseline content
   - Verify contains appended common context (if any)
   - Verify frontmatter updated

2. Step files: `plans/unification/steps/step-2-1.md`, `step-2-2.md`, `step-2-3.md`
   - Verify all 3 step files created (Step 2.1, 2.2, 2.3)
   - Verify each contains correct step content
   - Verify each has plan reference

3. Orchestrator plan: `plans/unification/orchestrator-plan.md`
   - Verify file exists
   - Verify contains orchestrator instructions or default

**Part D: Validate content**
1. Read plan-specific agent, verify structure:
   - Contains baseline quiet-task content
   - Contains separator: "---\n# Runbook-Specific Context"
   - Contains Common Context section from runbook (if present)
   - Frontmatter updated with correct name ("unification-task")
2. Read step-2-1.md, verify format:
   - Has "# Step 2.1:" heading
   - Contains step content from runbook
   - Has reference to plan or common context
3. Read orchestrator-plan.md, verify contains instructions
4. Check for any error messages or warnings from script

**Part E: Re-run test (idempotency check)**
- Run script again with same input
- Verify no errors on overwrite
- Verify outputs updated (not duplicated)

**Expected Outcome**: Script executes successfully, creates all expected outputs

**Unexpected Result Handling**:
- If script fails: Document error, check if it's a script bug or runbook format issue
- If outputs incorrect: Document discrepancies, escalate to sonnet for script fix
- If runbook format incompatible: Document format issue, escalate to user for design decision

**Error Conditions**:
- Script execution error → Capture error output, escalate to sonnet
- Missing outputs → Document which files missing, escalate to sonnet
- Malformed outputs → Document formatting issues, escalate to sonnet
- Idempotency failure → Document overwrite errors, escalate to sonnet

**Validation**:
- Script exits with code 0
- All expected files created
- File contents match expected format
- No errors in script output
- Re-run succeeds

**Success Criteria**:
- Script executes without errors
- All 3 expected output files created
- Plan-specific agent contains baseline + context
- Step files contain correct content
- Orchestrator plan created
- Re-run succeeds (idempotent)
- No warnings or errors in output

**Report Path**: `plans/oneshot-workflow/reports/phase1-step4-execution.md`

---

---

## Execution Instructions

1. Read `phase1-execution-plan.md` for:
   - Prerequisites and validation requirements
   - Error escalation triggers
   - Success criteria

2. Execute this step following the implementation section above

3. Perform all validation checks as specified

4. Write execution log to report path specified above with:
   - What was done
   - Results and artifacts created
   - Any errors or unexpected outcomes
   - Verification of success criteria

5. Return format:
   - Success: "done: <brief summary>"
   - Failure: "error: <description with diagnostic info>"

6. **Stop immediately** on any unexpected results per communication rules
