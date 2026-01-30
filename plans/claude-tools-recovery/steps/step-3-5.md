# Cycle 3.5

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.5: Wire OpenRouter provider keychain retrieval

**Objective**: Query keychain for API key and set base URL

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.2 should fail

**Expected failure:**
```
AssertionError: expected OPENROUTER_API_KEY='sk-or-test456', got ''
```

**Why it fails:** Provider doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update OpenRouterProvider.claude_env_vars() to query keychain and set base URL

**Changes:**
- File: claudeutils/account/providers.py
  Action: Update OpenRouterProvider.claude_env_vars():
    - Call: Keychain.find(service="openrouter-api-key", account=<account>)
    - Return: {"OPENROUTER_API_KEY": <keychain_value>, "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1"}

**Verify GREEN:** `pytest tests/test_account.py::test_openrouter_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: OpenRouter provider queries keychain and sets base URL

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation queries keychain, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-5-notes.md

---
