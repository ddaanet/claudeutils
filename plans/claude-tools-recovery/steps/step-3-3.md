# Cycle 3.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.3: Wire AccountState .env file check

**Objective**: Check ~/.claude/.env existence instead of hardcoded value

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.3 should fail

**Expected failure:**
```
AssertionError: expected 'API key in .env: Yes', got hardcoded value
```

**Why it fails:** AccountState doesn't check .env file

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_env -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update AccountState to check .env file existence

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state():
    - Check: (Path.home() / ".claude" / ".env").exists()
    - Set: AccountState.api_in_claude_env = True/False

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_env -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: AccountState checks .env file existence

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation checks file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-3-notes.md

---
