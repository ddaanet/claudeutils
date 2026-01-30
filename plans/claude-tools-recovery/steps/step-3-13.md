# Cycle 3.13

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.13: Wire model reset command to delete override file

**Objective**: Delete override file

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.9 should fail

**Expected failure:**
```
AssertionError: file still exists
```

**Why it fails:** Command doesn't delete file

**Verify RED:** Run `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update model reset command to delete override file

**Changes:**
- File: claudeutils/model/cli.py
  Action: Update reset_model() command:
    - Delete: Override file if exists
    - Output: Confirmation message

**Verify GREEN:** `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Command deletes override file

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation deletes file, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-13-notes.md

---
