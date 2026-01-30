# Cycle 3.11

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.11: Wire model list command to read config

**Objective**: Read LiteLLM config and display model names

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.7 should fail

**Expected failure:**
```
AssertionError: expected model names, got empty or hardcoded
```

**Why it fails:** Command doesn't read config

**Verify RED:** Run `pytest tests/test_model.py::test_model_list_output -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update model list command to read LiteLLM config

**Changes:**
- File: claudeutils/model/cli.py
  Action: Update list_models() command:
    - Read: LiteLLM config YAML file
    - Parse: model_list entries
    - Output: Model names (and tiers if applicable)

**Verify GREEN:** `pytest tests/test_model.py::test_model_list_output -v`
- Must pass

**Verify no regression:** `pytest tests/test_model.py`
- All tests pass

---

**Expected Outcome**: Command reads config and displays models

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation reads config, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-11-notes.md

---
