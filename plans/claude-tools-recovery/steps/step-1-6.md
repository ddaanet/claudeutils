# Cycle 1.6

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.6: Test keychain wrapper add operation

**Objective**: Mock subprocess for keychain add, assert correct command construction

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain.add() constructs correct security command

**Expected failure:**
```
AssertionError: subprocess.run not called with expected add-generic-password args
```

**Why it fails:** Stub doesn't call subprocess

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_add -v`
- Must fail with mock call assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess, assert add-generic-password command

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_keychain_add:
    - Mock: `patch("claudeutils.account.keychain.subprocess.run")`
    - Call: `Keychain.add(service="test-service", account="test-account", password="test-pass")`
    - Assert: subprocess.run called with ["security", "add-generic-password", "-s", "test-service", "-a", "test-account", "-w", "test-pass"]

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_add -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain add command construction

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts subprocess called with add args

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-6-notes.md

---
