# Cycle 3.6

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.6: Wire LiteLLM provider localhost URL

**Objective**: Return localhost URL instead of empty string

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.3 should fail

**Expected failure:**
```
AssertionError: expected LITELLM_BASE_URL='http://localhost:4000', got ''
```

**Why it fails:** Provider returns empty

**Verify RED:** Run `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update LiteLLMProvider.claude_env_vars() to return localhost URL

**Changes:**
- File: claudeutils/account/providers.py
  Action: Update LiteLLMProvider.claude_env_vars():
    - Return: {"LITELLM_BASE_URL": "http://localhost:4000"}

**Verify GREEN:** `pytest tests/test_account.py::test_litellm_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: LiteLLM provider returns localhost URL

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation returns localhost, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-6-notes.md

---
