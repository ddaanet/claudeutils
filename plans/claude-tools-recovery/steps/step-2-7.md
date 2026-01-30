# Cycle 2.7

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.7: Strengthen model list command test

**Objective**: Mock LiteLLM config, assert output contains model names

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test model list displays models from LiteLLM config

**Expected failure:**
```
AssertionError: expected model names in output, got empty or hardcoded list
```

**Why it fails:** Stub doesn't read config

**Verify RED:** Run `pytest tests/test_model.py::test_model_list_output -v`
- Must fail (no model names or wrong names)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock LiteLLM config file, assert output contains model names

**Changes:**
- File: tests/test_model.py
  Action: Create/update test_model_list_output:
    - Fixture: tmp_path with LiteLLM config YAML containing model_list
    - Mock: Config path to point to fixture
    - Run: `model list`
    - Assert: Output contains model names from fixture (e.g., "claude-sonnet-4-5")

**Verify GREEN:** `pytest tests/test_model.py::test_model_list_output -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Test verifies LiteLLM config reading and model display

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts model names from config in output

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-7-notes.md

---
