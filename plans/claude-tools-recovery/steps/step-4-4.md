# Cycle 4.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.4: Test provider missing keychain entry error

**Objective**: Verify clear error with setup instructions when API key missing

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account api with missing provider keychain shows setup instructions

**Expected failure:**
```
FAILED - Expected setup instructions, got generic error
```

**Why it fails:** Error message not helpful

**Verify RED:** Run `pytest tests/test_account.py::test_missing_provider_key -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Catch KeychainError and show setup instructions

**Changes:**
- File: claudeutils/account/cli.py
  Action: Update api() command:
    - Catch: KeychainError when getting provider credentials
    - Output: "API key not found. Run: claudeutils account add-key --provider <name>"

**Verify GREEN:** `pytest tests/test_account.py::test_missing_provider_key -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Clear setup instructions on missing key

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Error includes actionable setup command

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-4-notes.md

---
