# Cycle 2.5

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.5: Strengthen account plan command test

**Objective**: Mock filesystem, assert mode file written and output confirms switch

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account plan writes mode file and outputs confirmation

**Expected failure:**
```
AssertionError: mode file not written or contains wrong value
```

**Why it fails:** Stub doesn't write file

**Verify RED:** Run `pytest tests/test_account.py::test_account_plan_switch -v`
- Must fail (file not written or wrong content)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock filesystem, run account plan, assert mode file and output

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_plan_switch:
    - Fixture: tmp_path
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Run: `account plan` via CliRunner
    - Assert: tmp_path/.claude/account-mode file exists
    - Assert: File content == "plan\n"
    - Assert: Output contains "Switched to plan mode" or similar

**Verify GREEN:** `pytest tests/test_account.py::test_account_plan_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies mode file write and confirmation output

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts file written with correct mode value

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-5-notes.md

---
