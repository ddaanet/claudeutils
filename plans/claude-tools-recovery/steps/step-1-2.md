# Cycle 1.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.2: Strengthen OpenRouter provider keychain test

**Objective**: Add mock keychain query and assert non-empty API key + base URL

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test OpenRouterProvider.claude_env_vars() returns keychain value and base URL

**Expected failure:**
```
AssertionError: expected OPENROUTER_API_KEY='sk-or-test456', got OPENROUTER_API_KEY=''
```

**Why it fails:** Stub implementation returns empty string

**Verify RED:** Run `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must fail with empty credential or missing base URL assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock keychain, assert API key and OPENROUTER_BASE_URL

**Changes:**
- File: tests/test_account.py
  Action: Update test_openrouter_provider_credentials:
    - Mock: `patch("claudeutils.account.providers.subprocess.run")`
    - Return: keychain password "sk-or-test456"
    - Assert: `env_vars["OPENROUTER_API_KEY"] == "sk-or-test456"`
    - Assert: `env_vars["OPENROUTER_BASE_URL"] == "https://openrouter.ai/api/v1"`
    - Assert: subprocess called with correct service/account

**Verify GREEN:** `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain integration and base URL setting

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts keychain value and base URL, not empty

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-2-notes.md

---
