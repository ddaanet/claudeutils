# Cycle 3.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.1: Handle keychain command not found

**Objective**: Test Keychain handles FileNotFoundError when security command unavailable
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_keychain.py should test Keychain.find() handles FileNotFoundError gracefully

**Expected failure:**
```
FileNotFoundError not caught, test fails with unhandled exception
```

**Why it fails:** Keychain.find() doesn't catch subprocess FileNotFoundError

**Verify RED:**
```bash
pytest tests/test_account_keychain.py::test_keychain_command_not_found -v
```
- Create test with mock subprocess.run raising FileNotFoundError
- Assert Keychain().find() returns None (graceful degradation)
- Test should FAIL with uncaught exception

---

**GREEN Phase:**

**Implementation:** Add try/except to catch FileNotFoundError

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Wrap subprocess.run in try/except, catch FileNotFoundError, return None
- File: tests/test_account_keychain.py
  Action: Add test with FileNotFoundError mock, assert find() returns None

**Verify GREEN:**
```bash
pytest tests/test_account_keychain.py::test_keychain_command_not_found -v
```
- Test passes with None return

**Verify no regression:**
```bash
pytest tests/test_account_keychain.py -v
```
- All keychain tests pass

---

**Expected Outcome**: Keychain returns None when security command unavailable
**Error Conditions**: Still raises exception → verify try/except scope
**Validation**: Test verifies None return on FileNotFoundError
**Success Criteria**: Keychain error handling for missing command
**Report Path**: plans/claude-tools-recovery/reports/cycle-3-1-notes.md

---
