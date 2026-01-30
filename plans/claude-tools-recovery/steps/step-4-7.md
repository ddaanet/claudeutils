# Cycle 4.7

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.7: Integration test - model override flow

**Objective**: Test set → list → reset model override

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Full model override lifecycle

**Expected failure:**
```
AssertionError: override not visible in list or not cleared by reset
```

**Why it fails:** Integration not complete

**Verify RED:** Run `pytest tests/test_model.py::test_model_override_flow -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create model override integration test

**Changes:**
- File: tests/test_model.py
  Action: Create test_model_override_flow:
    - Fixture: tmp_path for override file and config
    - Mock: Config and override paths
    - Run: `model set claude-opus-4`
    - Assert: Override file exists with model name
    - Run: `model list`
    - Assert: Output shows override is active (if design includes this)
    - Run: `model reset`
    - Assert: Override file deleted
    - Run: `model list`
    - Assert: No override shown

**Verify GREEN:** `pytest tests/test_model.py::test_model_override_flow -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Full model override lifecycle works

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Set/list/reset flow is consistent

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-7-notes.md

---
