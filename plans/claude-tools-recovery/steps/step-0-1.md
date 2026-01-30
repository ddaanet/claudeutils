# Cycle 0.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 0.1: Delete exit-code-only account status test

**Objective**: Remove test_account_status_basic that only checks exit_code == 0

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Verify test file doesn't contain the vacuous test

**Expected failure:**
```
AssertionError: test_account_status_basic still exists in test_account.py
```

**Why it fails:** Test hasn't been deleted yet

**Verify RED:** Read tests/test_account.py and grep for "test_account_status_basic"
- Must find the function definition
- If not found, STOP - test may already be deleted

---

**GREEN Phase:**

**Implementation:** Delete test_account_status_basic function from tests/test_account.py

**Changes:**
- File: tests/test_account.py
  Action: Remove test_account_status_basic function (including decorator and docstring)

**Verify GREEN:** Read tests/test_account.py
- Must NOT contain "test_account_status_basic"

**Verify no regression:** `pytest tests/test_account.py`
- All remaining tests pass

---

**Expected Outcome**: Vacuous test removed, remaining tests pass

**Error Conditions**: Test not found → STOP (may be already deleted); Regression → STOP

**Validation**: Test deleted ✓, No regressions ✓

**Success Criteria**: Test file doesn't contain vacuous test, other tests still pass

**Report Path**: plans/claude-tools-recovery/reports/cycle-0-1-notes.md

---
