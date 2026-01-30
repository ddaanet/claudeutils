# Cycle 1.5

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.5: Test keychain wrapper find operation

**Objective**: Mock subprocess for keychain find, assert correct command construction

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test Keychain.find() constructs correct security command

**Expected failure:**
```
AssertionError: subprocess.run not called with expected security find-generic-password args
```

**Why it fails:** Stub doesn't call subprocess

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_find -v`
- Must fail with mock call assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess, assert find-generic-password command with service/account

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_keychain_find:
    - Mock: `patch("claudeutils.account.keychain.subprocess.run")`
    - Return: MagicMock with stdout containing password
    - Call: `Keychain.find(service="test-service", account="test-account")`
    - Assert: subprocess.run called with ["security", "find-generic-password", "-s", "test-service", "-a", "test-account", "-w"]
    - Assert: Returns password from stdout

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_find -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain find command construction

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts subprocess called with correct args

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-5-notes.md

---
