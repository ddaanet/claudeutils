# Step 8

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

---

## Step 8: Update Help Text and Error Messages

**Objective**: Update CLI help text, error messages, and output to reflect TDD support.

**Script Evaluation**: Prose description (20-30 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Update `main()` help text or usage string:
   ```
   Transforms runbook markdown into execution artifacts:
     - Plan-specific agent (.claude/agents/<runbook-name>-task.md)
     - Step/Cycle files (plans/<runbook-name>/steps/)
     - Orchestrator plan (plans/<runbook-name>/orchestrator-plan.md)

   Supports:
     - General runbooks (## Step N:)
     - TDD runbooks (## Cycle X.Y:, requires type: tdd in frontmatter)
   ```
2. Update error messages:
   - "ERROR: No steps found in general runbook"
   - "ERROR: No cycles found in TDD runbook"
   - "ERROR: TDD runbook missing 'type: tdd' in frontmatter"
3. Update success output summary:
   - Report runbook type (general/TDD)
   - Report steps or cycles count
   - Show appropriate file type (step-N.md vs cycle-X-Y.md)
4. Review all print statements and ensure consistency:
   - Use "step" for general runbooks
   - Use "cycle" for TDD runbooks
   - Clear distinction in output

**Expected Outcome**: Help text and messages reflect TDD support.

**Unexpected Result Handling**:
- If help text conflicts with actual behavior → revise text

**Error Conditions**:
- Inconsistent terminology → Fix all instances

**Validation**:
- Help text mentions both general and TDD runbooks
- Error messages use correct terminology
- Output summary shows correct type and counts

**Success Criteria**:
- Help text updated to mention TDD support
- At least 3 error messages updated
- Output summary reflects runbook type
- All terminology consistent (steps vs cycles)
- Changes documented in report

**Report Path**: `plans/prepare-runbook-tdd/reports/step-8-report.md`

---
