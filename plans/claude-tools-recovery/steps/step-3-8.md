# Cycle 3.8

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.8: Wire Keychain.add() to subprocess

**Objective**: Call subprocess.run for security add-generic-password

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.6 should fail

**Expected failure:**
```
AssertionError: subprocess.run not called
```

**Why it fails:** Keychain.add() is stub

**Verify RED:** Run `pytest tests/test_account.py::test_keychain_add -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update Keychain.add() to call subprocess

**Changes:**
- File: claudeutils/account/keychain.py
  Action: Update Keychain.add():
    - Call: subprocess.run(["security", "add-generic-password", "-s", service, "-a", account, "-w", password], check=True)

**Verify GREEN:** `pytest tests/test_account.py::test_keychain_add -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Keychain.add() calls subprocess

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation calls subprocess, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-8-notes.md

---
