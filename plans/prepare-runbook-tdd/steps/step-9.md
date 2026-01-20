# Step 9

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

---

## Step 9: Integration Test with TDD Runbook

**Objective**: Run modified `prepare-runbook.py` on existing TDD runbook and verify correct outputs.

**Script Evaluation**: Integration test (55 lines) - delegate to agent

**Execution Model**: Sonnet

**Implementation**:

Create and execute integration test script with the following requirements:
1. Run prepare-runbook.py on plans/tdd-integration/runbook.md
2. Verify agent uses tdd-task.md baseline (grep check)
3. Verify cycle files created, not step files (file count check)
4. Verify orchestrator plan exists (file existence check)
5. Exit with clear pass/fail status

Reference script template:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Integration Test: prepare-runbook.py with TDD Runbook ==="
echo ""

# Test runbook path
RUNBOOK="plans/tdd-integration/runbook.md"
echo "Test runbook: $RUNBOOK"
echo ""

# Run prepare-runbook.py
echo "Running prepare-runbook.py..."
python3 agent-core/bin/prepare-runbook.py "$RUNBOOK"
echo ""

# Verify outputs
echo "=== Verification ==="

# Check plan-specific agent uses tdd-task baseline
echo "1. Checking agent baseline..."
if grep -q "tdd-task.md" .claude/agents/tdd-integration-task.md; then
    echo "   ✓ Agent uses tdd-task.md baseline"
else
    echo "   ✗ ERROR: Agent does not use tdd-task baseline"
    exit 1
fi

# Check cycle files created (not step files)
echo "2. Checking cycle files..."
CYCLE_COUNT=$(ls plans/tdd-integration/steps/cycle-*.md 2>/dev/null | wc -l | tr -d ' ')
STEP_COUNT=$(ls plans/tdd-integration/steps/step-*.md 2>/dev/null | wc -l | tr -d ' ')

echo "   Cycle files: $CYCLE_COUNT"
echo "   Step files: $STEP_COUNT"

if [ "$CYCLE_COUNT" -gt 0 ] && [ "$STEP_COUNT" -eq 0 ]; then
    echo "   ✓ Cycle files created, no step files"
else
    echo "   ✗ ERROR: Expected cycle files, found $CYCLE_COUNT cycles and $STEP_COUNT steps"
    exit 1
fi

# Check orchestrator plan exists
echo "3. Checking orchestrator plan..."
if [ -f "plans/tdd-integration/orchestrator-plan.md" ]; then
    echo "   ✓ Orchestrator plan created"
else
    echo "   ✗ ERROR: Orchestrator plan not found"
    exit 1
fi

echo ""
echo "=== Integration Test: PASSED ==="
```

**Expected Outcome**: Script passes all verification checks.

**Unexpected Result Handling**:
- If any check fails → report which check failed, expected vs actual, and STOP

**Error Conditions**:
- Script execution failure → Report error and STOP
- Verification failure → Report expected vs actual and STOP

**Validation**:
- Agent uses `tdd-task.md` baseline (grep check)
- Cycle files created, not step files (file count check)
- Orchestrator plan exists (file existence check)
- Script returns exit code 0

**Success Criteria**:
- Integration test script executes without errors
- All 3 verification checks pass
- Output shows "Integration Test: PASSED"

**Report Path**: `plans/prepare-runbook-tdd/reports/step-9-report.md`

---
