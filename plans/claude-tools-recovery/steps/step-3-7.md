# Cycle 3.7

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.7: Wire Keychain.find() to subprocess

**Objective**: Call subprocess.run for security find-generic-password

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.5 should fail

**Expected failure:**
```
AssertionError: subprocess.run not called
```

**Why it fails:** Keychain.find() is stub

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_find -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update Keychain.find() to call subprocess with security command

**Changes:**
- File: claudeutils/account/keychain.py
  Action: Update Keychain.find():
    - Call: subprocess.run(["security", "find-generic-password", "-s", service, "-a", account, "-w"], capture_output=True, text=True, check=True)
    - Return: result.stdout.strip()
    - Handle: CalledProcessError → raise KeychainError

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_find -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Keychain.find() calls subprocess

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation calls subprocess, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-7-notes.md

---
