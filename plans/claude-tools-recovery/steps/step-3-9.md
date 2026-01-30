# Cycle 3.9

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.9: Wire account plan command to write file

**Objective**: Write mode file instead of returning stub output

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.5 should fail

**Expected failure:**
```
AssertionError: mode file not written
```

**Why it fails:** Command doesn't write file

**Verify RED:** Run `pytest tests/test_account.py::test_account_plan_switch -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update account plan command to write mode file

**Changes:**
- File: claudeutils/account/cli.py
  Action: Update plan() command:
    - Write: (Path.home() / ".claude" / "account-mode").write_text("plan\n")
    - Output: "Switched to plan mode" message

**Verify GREEN:** `pytest tests/test_account.py::test_account_plan_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Command writes mode file

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation writes file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-9-notes.md

---
