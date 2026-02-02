# Cycle 1.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.2: Strengthen OpenRouterProvider with keychain retrieval

**Objective**: Add keystore to OpenRouterProvider and test credential retrieval
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_providers.py::test_openrouter_provider_env_vars should verify non-empty credentials

**Expected failure:**
```
AssertionError: assert env_vars["OPENROUTER_API_KEY"] != ""
(current returns empty string)
```

**Why it fails:** OpenRouterProvider.claude_env_vars() returns hardcoded empty strings

**Verify RED:**
```bash
pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -v
```
- Edit test to add `assert env_vars["OPENROUTER_API_KEY"] != ""`
- Test should FAIL (stub returns "")

---

**GREEN Phase:**

**Implementation:** Add keystore to OpenRouterProvider and retrieve credentials

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Add `__init__(self, keystore: KeyStore)`, add `get_openrouter_api_key()` to KeyStore protocol, call it in `claude_env_vars()`
- File: tests/test_account_providers.py
  Action: Create mock keystore with `get_openrouter_api_key()` returning "test-openrouter-key", verify values

**Verify GREEN:**
```bash
pytest tests/test_account_providers.py::test_openrouter_provider_env_vars -v
```
- Test passes with real keychain values from mock

**Verify no regression:**
```bash
pytest tests/test_account_providers.py -v
```
- All provider tests pass

---

**Expected Outcome**: OpenRouterProvider test uses mock keychain and verifies retrieval
**Error Conditions**: Keychain mock setup incorrect → adjust mock pattern
**Validation**: Test has behavioral assertion for credential retrieval
**Success Criteria**: OpenRouterProvider retrieves credentials from keystore
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-2-notes.md

---
