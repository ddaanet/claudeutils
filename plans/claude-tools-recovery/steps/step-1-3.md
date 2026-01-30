# Cycle 1.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.3: Strengthen LiteLLM provider test

**Objective**: Assert LiteLLMProvider returns localhost URL without keychain dependency

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test LiteLLMProvider.claude_env_vars() returns localhost URL

**Expected failure:**
```
AssertionError: expected LITELLM_BASE_URL='http://localhost:4000', got LITELLM_BASE_URL=''
```

**Why it fails:** Stub returns empty or hardcoded "OK"

**Verify RED:** Run `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must fail with localhost URL assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Assert localhost URL in env vars (no keychain mock needed)

**Changes:**
- File: tests/test_account.py
  Action: Update test_litellm_provider_credentials:
    - Assert: `env_vars["LITELLM_BASE_URL"] == "http://localhost:4000"`
    - No keychain mock (LiteLLM doesn't use credentials)

**Verify GREEN:** `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies localhost URL without keychain

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts localhost URL

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-3-notes.md

---
