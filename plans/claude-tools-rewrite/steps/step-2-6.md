# Cycle 2.6

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.6: Load full LiteLLM config file

**Objective**: Read config.yaml and parse all model entries into list[LiteLLMModel]
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** load_litellm_config() returns list of models from YAML file

**Expected failure:**
```
AttributeError: module 'claudeutils.model.config' has no attribute 'load_litellm_config'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_load_litellm_config -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create load_litellm_config() reading file and parsing entries

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create load_litellm_config(path) reading file, splitting on model_list entries, parsing each
- File: tests/test_model_config.py
  Action: Test with tmp_path fixture containing sample config.yaml

**Verify GREEN:** `pytest tests/test_model_config.py::test_load_litellm_config -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-6-notes.md

---
