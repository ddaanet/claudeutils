# Cycle 1.11

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.11: Keychain wrapper - find operation

**Objective**: Implement Keychain.find() wrapping `security find-generic-password`
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Keychain.find() returns password when keychain entry exists

**Expected failure:**
```
AttributeError: module 'claudeutils.account' has no attribute 'Keychain'
```

**Why it fails:** Keychain class doesn't exist

**Verify RED:** `pytest tests/test_account_keychain.py::test_keychain_find_success -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create Keychain class with find() method

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Create Keychain class with find() calling subprocess.run(["security", "find-generic-password", ...])
- File: src/claudeutils/account/__init__.py
  Action: Add `from .keychain import Keychain`
- File: tests/test_account_keychain.py
  Action: Test find() with mocked subprocess returning success

**Verify GREEN:** `pytest tests/test_account_keychain.py::test_keychain_find_success -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-11-notes.md

---
