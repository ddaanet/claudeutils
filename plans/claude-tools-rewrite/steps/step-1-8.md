# Cycle 1.8

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.8: AnthropicProvider implementation

**Objective**: Implement AnthropicProvider with claude_env_vars returning ANTHROPIC_API_KEY
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** AnthropicProvider.claude_env_vars() returns ANTHROPIC_API_KEY from keychain

**Expected failure:**
```
AttributeError: module 'claudeutils.account.providers' has no attribute 'AnthropicProvider'
```

**Why it fails:** AnthropicProvider class doesn't exist

**Verify RED:** `pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create AnthropicProvider class implementing Provider

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Create AnthropicProvider class with name="anthropic", claude_env_vars() returning {"ANTHROPIC_API_KEY": key}
- File: src/claudeutils/account/__init__.py
  Action: Add `from .providers import AnthropicProvider`
- File: tests/test_account_providers.py
  Action: Test AnthropicProvider.claude_env_vars() with mock KeyStore

**Verify GREEN:** `pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-8-notes.md

---
