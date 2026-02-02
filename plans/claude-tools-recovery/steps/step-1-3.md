# Cycle 1.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.3: Strengthen LiteLLMProvider with localhost URL

**Objective**: Verify LiteLLM provider returns specific localhost URL (not empty)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_providers.py::test_litellm_provider_env_vars should verify specific URL value

**Expected failure:**
```
AssertionError: assert env_vars["ANTHROPIC_BASE_URL"] == "http://localhost:4000"
(current returns empty string)
```

**Why it fails:** LiteLLMProvider.claude_env_vars() returns empty string for base URL

**Verify RED:**
```bash
pytest tests/test_account_providers.py::test_litellm_provider_env_vars -v
```
- Edit test to assert `env_vars["ANTHROPIC_BASE_URL"] == "http://localhost:4000"`
- Test should FAIL (stub returns "")

---

**GREEN Phase:**

**Implementation:** Update LiteLLMProvider to return localhost URL constant

**Changes:**
- File: src/claudeutils/account/providers.py
  Action: Replace empty ANTHROPIC_BASE_URL with "http://localhost:4000", keep LITELLM_API_KEY as "none" (doesn't need real key)
- File: tests/test_account_providers.py
  Action: Assert ANTHROPIC_BASE_URL == "http://localhost:4000"

**Verify GREEN:**
```bash
pytest tests/test_account_providers.py::test_litellm_provider_env_vars -v
```
- Test passes with correct URL

**Verify no regression:**
```bash
pytest tests/test_account_providers.py -v
```
- All provider tests pass

---

**Expected Outcome**: LiteLLM provider test verifies correct base URL value
**Error Conditions**: URL mismatch → verify localhost port convention
**Validation**: Test asserts specific URL, not just key presence
**Success Criteria**: LiteLLM returns http://localhost:4000 base URL
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-3-notes.md

---
