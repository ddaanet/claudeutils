# Cycle 4.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.1: Test keychain not accessible error

**Objective**: Verify clear error message when keychain unavailable

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain operations raise clear error when security command unavailable

**Expected failure:**
```
FAILED - Expected KeychainError with clear message, got generic error
```

**Why it fails:** Error handling not implemented

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_unavailable -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Catch subprocess errors and raise KeychainError with helpful message

**Changes:**
- File: claudeutils/account/keychain.py
  Action: Update Keychain.find():
    - Catch: FileNotFoundError (security not found)
    - Raise: KeychainError("macOS keychain not available. Are you on macOS?")

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_unavailable -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Clear error message for missing keychain

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Error message is clear and helpful

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-1-notes.md

---
