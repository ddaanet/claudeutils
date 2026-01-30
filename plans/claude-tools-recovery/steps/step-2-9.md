# Cycle 2.9

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.9: Strengthen model reset command test

**Objective**: Mock filesystem, assert override file deleted

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test model reset deletes override file

**Expected failure:**
```
AssertionError: override file still exists after reset
```

**Why it fails:** Stub doesn't delete file

**Verify RED:** Run `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must fail (file not deleted)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create override file in fixture, run model reset, assert deleted

**Changes:**
- File: tests/test_model.py
  Action: Create/update test_model_reset_deletes_file:
    - Fixture: tmp_path with existing override file
    - Mock: Override file path to tmp_path
    - Run: `model reset`
    - Assert: Override file does not exist
    - Assert: Output confirms reset

**Verify GREEN:** `pytest tests/test_model.py::test_model_reset_deletes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Test verifies override file deletion

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts file deleted

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-9-notes.md

---
