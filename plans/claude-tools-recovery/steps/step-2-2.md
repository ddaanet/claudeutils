# Cycle 2.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.2: Strengthen account status test - keychain OAuth check

**Objective**: Mock keychain query for OAuth token, assert output shows OAuth status

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account status displays OAuth status from keychain query

**Expected failure:**
```
AssertionError: expected output to contain 'OAuth: Yes', got 'OAuth: <hardcoded>'
```

**Why it fails:** Stub doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_oauth -v`
- Must fail with OAuth status assertion
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock keychain find for OAuth token, assert output shows status

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_status_oauth:
    - Fixture: tmp_path with mode/provider files
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Mock: `patch("claudeutils.account.state.subprocess.run")` returns OAuth token
    - Run: `account status`
    - Assert: Output contains "OAuth: Yes" or "OAuth in keychain: Yes"

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_oauth -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies keychain OAuth query integration

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts OAuth status from mocked keychain

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-2-notes.md

---
