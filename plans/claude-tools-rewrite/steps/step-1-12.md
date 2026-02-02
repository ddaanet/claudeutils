# Cycle 1.12

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.12: Keychain wrapper - add operation

**Objective**: Implement Keychain.add() wrapping `security add-generic-password`
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Keychain.add() calls security command with correct arguments

**Expected failure:**
```
AttributeError: 'Keychain' object has no attribute 'add'
```

**Why it fails:** add() method doesn't exist

**Verify RED:** `pytest tests/test_account_keychain.py::test_keychain_add -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add add() method to Keychain

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Add add(account, password) calling subprocess.run(["security", "add-generic-password", ...])
- File: tests/test_account_keychain.py
  Action: Test add() with mocked subprocess, verify command arguments

**Verify GREEN:** `pytest tests/test_account_keychain.py::test_keychain_add -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-12-notes.md

---
