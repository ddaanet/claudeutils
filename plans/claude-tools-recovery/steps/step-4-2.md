# Cycle 4.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.2: Test config files missing defaults

**Objective**: Verify sensible defaults when account config files don't exist

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test AccountState with missing config files returns defaults

**Expected failure:**
```
FAILED - Expected default mode, got error or crash
```

**Why it fails:** Default handling not implemented

**Verify RED:** Run `pytest tests/test_account.py::test_missing_config_defaults -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Return defaults when config files missing

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state():
    - Catch: FileNotFoundError when reading mode/provider files
    - Default: mode="plan", provider="anthropic" (or None with clear indication)

**Verify GREEN:** `pytest tests/test_account.py::test_missing_config_defaults -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Sensible defaults when files missing

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Defaults allow account status to work

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-2-notes.md

---
