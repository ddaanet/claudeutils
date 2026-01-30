# Cycle 2.8

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.8: Strengthen model set command test

**Objective**: Mock filesystem, assert override file written with model name

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test model set writes override file with specified model

**Expected failure:**
```
AssertionError: override file not written or contains wrong model
```

**Why it fails:** Stub doesn't write file

**Verify RED:** Run `pytest tests/test_model.py::test_model_set_writes_file -v`
- Must fail (file not written)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock override file path, run model set, assert file content

**Changes:**
- File: tests/test_model.py
  Action: Create/update test_model_set_writes_file:
    - Fixture: tmp_path for override file
    - Mock: Override file path to tmp_path
    - Run: `model set claude-opus-4`
    - Assert: Override file exists
    - Assert: File content == "claude-opus-4\n"
    - Assert: Output confirms model set

**Verify GREEN:** `pytest tests/test_model.py::test_model_set_writes_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Test verifies override file write with model name

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts file written with correct model

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-8-notes.md

---
