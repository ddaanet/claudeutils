# Cycle 2.2

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.2: LiteLLMModel Pydantic model

**Objective**: Create LiteLLMModel with name, litellm_model, tiers, pricing fields
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** LiteLLMModel can be instantiated with required fields

**Expected failure:**
```
AttributeError: module 'claudeutils.model' has no attribute 'LiteLLMModel'
```

**Why it fails:** LiteLLMModel class doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_litellm_model_creation -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create LiteLLMModel Pydantic model

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create LiteLLMModel(BaseModel) with name, litellm_model, tiers, arena_rank, input_price, output_price, api_key_env, api_base
- File: src/claudeutils/model/__init__.py
  Action: Add `from .config import LiteLLMModel`
- File: tests/test_model_config.py
  Action: Test instantiating LiteLLMModel with valid data

**Verify GREEN:** `pytest tests/test_model_config.py::test_litellm_model_creation -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-2-notes.md

---
