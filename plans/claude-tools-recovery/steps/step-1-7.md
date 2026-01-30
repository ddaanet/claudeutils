# Cycle 1.7

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.7: Test keychain entry not found

**Objective**: Mock CalledProcessError from keychain, verify error handling

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain.find() raises KeychainError when entry not found

**Expected failure:**
```
FAILED - KeychainError not raised on entry not found
```

**Why it fails:** Stub doesn't detect missing entry

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_not_found -v`
- Must fail (no error raised or wrong type)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess CalledProcessError, assert KeychainError raised

**Changes:**
- File: tests/test_account.py
  Action: Create test_keychain_not_found:
    - Mock: `patch("claudeutils.account.keychain.subprocess.run")` raises CalledProcessError(returncode=44)
    - Call: `Keychain.find(service="missing", account="missing")`
    - Assert: Raises KeychainError with appropriate message

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_not_found -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies error on missing keychain entry

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts KeychainError raised

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-7-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review provider/keychain test quality. Commit fixes.
3. Functional review: Verify tests mock real I/O (subprocess), assert on behavior (not just structure).

---
