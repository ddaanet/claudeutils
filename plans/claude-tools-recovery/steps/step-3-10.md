# Cycle 3.10

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.10: Wire account api command to write files and generate .env

**Objective**: Write mode file and generate claude-env with credentials

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.6 should fail

**Expected failure:**
```
AssertionError: claude-env file not created
```

**Why it fails:** Command doesn't generate .env

**Verify RED:** Run `pytest tests/test_account.py::test_account_api_switch -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update account api command to write mode and generate .env

**Changes:**
- File: claudeutils/account/cli.py
  Action: Update api() command:
    - Write: (Path.home() / ".claude" / "account-mode").write_text("api\n")
    - Get: provider.claude_env_vars()
    - Write: (Path.home() / ".claude" / ".env") with env vars
    - Output: Confirmation message

**Verify GREEN:** `pytest tests/test_account.py::test_account_api_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Command writes mode file and generates .env

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation writes both files, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-10-notes.md

---
