# Cycle 3.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.4: Wire Anthropic provider keychain retrieval

**Objective**: Query keychain for API key instead of returning empty string

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 1.1 should fail

**Expected failure:**
```
AssertionError: expected ANTHROPIC_API_KEY='sk-ant-test123', got ''
```

**Why it fails:** Provider doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update AnthropicProvider.claude_env_vars() to query keychain

**Changes:**
- File: claudeutils/account/providers.py
  Action: Update AnthropicProvider.claude_env_vars():
    - Call: Keychain.find(service="anthropic-api-key", account=<account>)
    - Return: {"ANTHROPIC_API_KEY": <keychain_value>}
    - Handle: KeychainError → raise or return empty with error

**Verify GREEN:** `pytest tests/test_account.py::test_anthropic_provider_credentials -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Anthropic provider queries keychain for API key

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation queries keychain, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-4-notes.md

---
