# Cycle 2.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.2: Test account status displays validation issues

**Objective**: Verify account status outputs consistency validation results
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py should test account status displays issues when state is inconsistent

**Expected failure:**
```
AssertionError: assert "Plan mode requires OAuth credentials" in result.output
```

**Why it fails:** get_account_state() may not check keychain, or CLI doesn't display validation issues

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_status_with_issues -v
```
- Create test with tmp_path, write mode="plan" to account-mode file
- Mock keychain query (via Keychain.find) to return None (no OAuth)
- Assert validation message in output
- Test should FAIL if CLI doesn't display issues

---

**GREEN Phase:**

**Implementation:** Update get_account_state() to query keychain and CLI to display validation

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In get_account_state(), create Keychain instance, call find() to check OAuth presence, set oauth_in_keychain field
- File: src/claudeutils/account/cli.py
  Action: Ensure status() calls `state.validate_consistency()` and displays issues (already exists from current implementation)
- File: tests/test_cli_account.py
  Action: Create test with mode=plan fixture, mock Keychain.find to return None, assert issue message

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_status_with_issues -v
```
- Test passes with validation output

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All account CLI tests pass

---

**Expected Outcome**: account status test verifies validation issues displayed
**Error Conditions**: Issue message not in output → check validate_consistency() call
**Validation**: Test creates inconsistent state, asserts error message
**Success Criteria**: CLI outputs consistency validation results
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-2-notes.md

---
