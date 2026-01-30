# Cycle 2.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.4: Strengthen account status test - consistency validation

**Objective**: Create inconsistent state fixture, assert output shows validation warnings

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays consistency warnings for mismatched state

**Expected failure:**
```
AssertionError: expected validation warning in output, not found
```

**Why it fails:** Stub doesn't run validation

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_validation -v`
- Must fail (no validation output)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create inconsistent fixture (mode=api + OAuth in keychain), assert warning

**Changes:**
- File: tests/test_account.py
  Action: Create test_account_status_validation:
    - Fixture: tmp_path/.claude/account-mode = "api"
    - Mock: OAuth token in keychain (mode=api shouldn't have OAuth)
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account status`
    - Assert: Output contains validation warning or inconsistency message

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_validation -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies validation logic runs and outputs warnings

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts validation warning present

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-4-notes.md

---
