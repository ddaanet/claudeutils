# Cycle 2.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.3: Strengthen account status test - API key in .env check

**Objective**: Mock .env file existence, assert output shows API key status

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays API key status from .env file check

**Expected failure:**
```
AssertionError: expected output to contain 'API key in .env: Yes', got hardcoded value
```

**Why it fails:** Stub doesn't check .env file

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_env -v`
- Must fail with .env status assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create .env file in fixture, assert output shows API key status

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_status_env:
    - Fixture: tmp_path with mode/provider files
    - Setup: Create tmp_path/.claude/.env file (can be empty)
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account status`
    - Assert: Output contains "API key in .env: Yes" or similar

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_env -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies .env file existence check

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts .env status from fixture

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-3-notes.md

---
