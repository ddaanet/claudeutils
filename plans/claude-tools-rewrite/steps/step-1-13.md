# Cycle 1.13

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.13: Keychain wrapper - delete operation

**Objective**: Implement Keychain.delete() wrapping `security delete-generic-password`
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Keychain.delete() calls security command to remove entry

**Expected failure:**
```
AttributeError: 'Keychain' object has no attribute 'delete'
```

**Why it fails:** delete() method doesn't exist

**Verify RED:** `pytest tests/test_account_keychain.py::test_keychain_delete -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add delete() method to Keychain

**Changes:**
- File: src/claudeutils/account/keychain.py
  Action: Add delete(account) calling subprocess.run(["security", "delete-generic-password", ...])
- File: tests/test_account_keychain.py
  Action: Test delete() with mocked subprocess

**Verify GREEN:** `pytest tests/test_account_keychain.py::test_keychain_delete -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-13-notes.md

---

**Checkpoint**
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review AccountState model design, Provider strategy clarity, Keychain wrapper safety. Commit fixes.

---
