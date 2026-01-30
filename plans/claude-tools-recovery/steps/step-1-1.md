# Cycle 1.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.1: Strengthen Anthropic provider keychain test

**Objective**: Add mock keychain query and assert non-empty API key in claude_env_vars()

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test AnthropicProvider.claude_env_vars() returns actual keychain value

**Expected failure:**
```
AssertionError: expected ANTHROPIC_API_KEY='sk-ant-test123', got ANTHROPIC_API_KEY=''
```

**Why it fails:** Stub implementation returns empty string

**Verify RED:** Run `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must fail with empty credential assertion
- If passes, STOP - implementation may already be real

---

**GREEN Phase:**

**Implementation:** Mock subprocess.run for keychain query, assert non-empty API key

**Changes:**
- File: tests/test_account.py
  Action: Update test_anthropic_provider_credentials (or create if missing):
    - Import: `from unittest.mock import patch, MagicMock`
    - Mock: `patch("claudeutils.account.providers.subprocess.run")`
    - Return: keychain password "sk-ant-test123"
    - Assert: `env_vars["ANTHROPIC_API_KEY"] == "sk-ant-test123"`
    - Assert: subprocess called with correct service/account args

**Verify GREEN:** `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All existing tests pass

---

**Expected Outcome**: Test verifies keychain integration with mocked subprocess

**Error Conditions**: Test passes on RED → STOP; GREEN doesn't pass → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts on keychain value, not empty string

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-1-notes.md

---
