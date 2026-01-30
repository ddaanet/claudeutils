# Cycle 1.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.4: Test Anthropic provider missing keychain entry

**Objective**: Mock missing keychain entry and verify error handling

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test AnthropicProvider handles missing keychain entry gracefully

**Expected failure:**
```
FAILED - KeychainError not raised when keychain entry missing
```

**Why it fails:** Stub doesn't query keychain, can't fail

**Verify RED:** Run `pytest tests/test_account.py::test_anthropic_missing_keychain -v`
- Must fail (KeychainError not raised or wrong error type)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock subprocess CalledProcessError (keychain not found), assert error raised

**Changes:**
- File: tests/test_account.py
  Action: Create test_anthropic_missing_keychain:
    - Mock: `patch("claudeutils.account.providers.subprocess.run")` raises CalledProcessError
    - Call: `provider.claude_env_vars()`
    - Assert: Raises KeychainError or returns empty with error message

**Verify GREEN:** `pytest tests/test_account.py::test_anthropic_missing_keychain -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies error handling for missing credentials

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts error on missing keychain entry

**Report Path**: plans/claude-tools-recovery/reports/cycle-1-4-notes.md

---
