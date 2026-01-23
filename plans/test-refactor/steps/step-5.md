# Step 5

**Plan**: `/Users/david/code/claudeutils/plans/test-refactor/runbook.md`
**Common Context**: See plan file for context

---

## Step 5: Delete test_markdown.py and validate

**Objective**: Remove test_markdown.py and verify all 154 tests still pass

**Script Evaluation**: Direct execution (simple bash commands)

**Execution Model**: Haiku

**Implementation**:
```bash
cd /Users/david/code/claudeutils

# Run tests FIRST to verify everything works
pytest tests/test_markdown*.py -v --tb=short

# If tests pass, check counts
TEST_COUNT=$(pytest tests/test_markdown*.py --collect-only -q 2>&1 | grep -E "^[0-9]+ test" | awk '{print $1}')
echo "Test count: $TEST_COUNT"

# Verify test count is 154
if [ "$TEST_COUNT" != "154" ]; then
  echo "ERROR: Expected 154 tests, got $TEST_COUNT"
  exit 1
fi

# Delete test_markdown.py
rm tests/test_markdown.py

# Run tests again to verify still pass
pytest tests/test_markdown*.py -v --tb=short

# Check line counts
echo ""
echo "Final line counts:"
wc -l tests/test_markdown*.py

# Run full line limit check
./scripts/check_line_limits.sh
```

**Expected Outcome**: All 154 tests pass, all test files ≤ 400 lines, line limit check passes

**Unexpected Result Handling**:
- If tests fail before deletion: Stop and report - Step 3/4 introduced issues
- If tests fail after deletion: Rollback - some tests weren't properly redistributed
- If line limits still exceeded: Stop and report - Step 4 incomplete

**Error Conditions**:
- Test failures → Escalate to sonnet for analysis
- Line limit failures → Escalate to user

**Validation**:
- All 154 tests pass
- No test files exceed 400 lines
- test_markdown.py deleted
- Line limit check passes

**Success Criteria**:
- All tests passing (154/154 markdown tests minimum)
- All markdown test files ≤ 400 lines
- Line limit check passes
- No regressions in functionality

**Report Path**: `/Users/david/code/claudeutils/plans/test-refactor/reports/step-5.md`

---
