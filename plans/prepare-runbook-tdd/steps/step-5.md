# Step 5

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

---

## Step 5: Implement Conditional Baseline Selection

**Objective**: Modify `read_baseline_agent()` to load `tdd-task.md` for TDD runbooks and `quiet-task.md` for general runbooks.

**Script Evaluation**: Prose description (15-20 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Review existing `read_baseline_agent()` function
2. Add `runbook_type` parameter to function signature
3. Implement conditional baseline selection:
   - If `runbook_type == "tdd"` → load `agent-core/agents/tdd-task.md`
   - If `runbook_type == "general"` → load `agent-core/agents/quiet-task.md`
   - If unknown type → default to `quiet-task.md` and warn
4. Update all calls to `read_baseline_agent()` to pass runbook type
5. Add error handling for missing baseline files:
   - "ERROR: Baseline agent not found: [path]"
   - Exit with clear error message

**Expected Outcome**: Baseline selection conditional on runbook type.

**Unexpected Result Handling**:
- If baseline file missing → Clear error and STOP

**Error Conditions**:
- Baseline file not found → Report path and exit
- Invalid runbook type → Warn and use default

**Validation**:
- Correct baseline loaded for TDD runbooks
- Correct baseline loaded for general runbooks
- Error message clear when baseline missing

**Success Criteria**:
- `read_baseline_agent()` accepts runbook_type parameter
- Conditional logic implemented
- Error handling for missing baselines
- All callers updated to pass type
- Changes tested (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-5-report.md`

---
