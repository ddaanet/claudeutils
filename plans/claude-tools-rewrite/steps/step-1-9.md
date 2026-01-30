# Cycle 1.9

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.9: OpenRouterProvider implementation

**Objective**: Implement OpenRouterProvider with OPENROUTER_API_KEY and ANTHROPIC_BASE_URL
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** OpenRouterProvider.claude_env_vars() returns both API key and base URL

**Expected failure:**
```
AttributeError: module 'claudeutils.account.providers' has no attribute 'OpenRouterProvider'
```

**Why it fails:** OpenRouterProvider class doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create OpenRouterProvider class

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create OpenRouterProvider with claude_env_vars() returning OPENROUTER_API_KEY and ANTHROPIC_BASE_URL
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import OpenRouterProvider`
- File: tests/test_account_providers.py
  Action: Test OpenRouterProvider.claude_env_vars() includes both env vars

**Verify GREEN:** `pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-9-notes.md

---
