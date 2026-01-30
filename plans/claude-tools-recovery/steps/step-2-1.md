# Cycle 2.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.1: Strengthen account status test - mode and provider files

**Objective**: Mock filesystem with mode/provider files, assert output contains actual values

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays mode and provider from fixture files

**Expected failure:**
```
AssertionError: expected output to contain 'Mode: plan', got 'Mode: <hardcoded>'
```

**Why it fails:** Stub returns hardcoded output, doesn't read files

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must fail with fixture value assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock Path.home(), create tmp_path fixtures, assert output contains fixture values

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_status_reads_files:
    - Fixture: Use pytest tmp_path
    - Setup: Create tmp_path/.claude/account-mode with "plan\n"
    - Setup: Create tmp_path/.claude/account-provider with "anthropic\n"
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account status` via CliRunner
    - Assert: Output contains "Mode: plan"
    - Assert: Output contains "Provider: anthropic"

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies filesystem reading with mocked home directory

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts output contains fixture file values

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-1-notes.md

---
