# Cycle 1.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.1: Test AnthropicProvider keystore interaction

**Objective**: Verify AnthropicProvider calls keystore method (not just checks key presence)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_providers.py::test_anthropic_provider_env_vars should verify mock keystore method called

**Expected failure:**
```
AssertionError: Expected 'get_anthropic_api_key' to be called once. Called 0 times.
```

**Why it fails:** Test doesn't verify keystore method invocation

**Verify RED:**
```bash
pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -v
```
- Add `mock_keystore.get_anthropic_api_key.assert_called_once()` to test
- Test should FAIL if assertion missing or mock not called

---

**GREEN Phase:**

**Implementation:** Add mock call verification to test (implementation already calls it)

**Changes:**
- File: tests/test_account_providers.py
  Action: Add `mock_keystore.get_anthropic_api_key.assert_called_once()` after env_vars call

**Verify GREEN:**
```bash
pytest tests/test_account_providers.py::test_anthropic_provider_env_vars -v
```
- Test passes with mock call verification

**Verify no regression:**
```bash
pytest tests/test_account_providers.py -v
```
- All provider tests pass

---

**Expected Outcome**: Test verifies keystore method called, not just key presence
**Error Conditions**: If mock not called → implementation needs fixing
**Validation**: Mock call assertion added and passes
**Success Criteria**: Test verifies behavioral interaction with keystore
**Report Path**: plans/claude-tools-recovery/reports/cycle-1-1-notes.md

---
