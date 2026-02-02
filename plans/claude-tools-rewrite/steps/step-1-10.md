# Cycle 1.10

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.10: LiteLLMProvider implementation

**Objective**: Implement LiteLLMProvider with LITELLM_API_KEY and base URL
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** LiteLLMProvider.claude_env_vars() returns LiteLLM-specific variables

**Expected failure:**
```
AttributeError: module 'claudeutils.account.providers' has no attribute 'LiteLLMProvider'
```

**Why it fails:** LiteLLMProvider class doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_litellm_provider_env_vars -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create LiteLLMProvider class

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create LiteLLMProvider with claude_env_vars() returning appropriate env vars
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import LiteLLMProvider`
- File: tests/test_account_providers.py
  Action: Test LiteLLMProvider.claude_env_vars() returns expected variables

**Verify GREEN:** `pytest tests/test_account_providers.py::test_litellm_provider_env_vars -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-10-notes.md

---
