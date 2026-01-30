# Cycle 3.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.2: Wire AccountState OAuth keychain check

**Objective**: Query keychain for OAuth token instead of returning hardcoded status

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.2 should fail

**Expected failure:**
```
AssertionError: expected 'OAuth: Yes', got 'OAuth: <hardcoded>'
```

**Why it fails:** AccountState doesn't query keychain

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_oauth -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update AccountState to query keychain for OAuth token

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state() or property:
    - Call: Keychain.find(service="claude-oauth", account=<username>) or similar
    - Set: AccountState.oauth_in_keychain = True if found, False if not
    - Handle: KeychainError → False

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_oauth -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: AccountState queries keychain for OAuth token

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation queries keychain, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-2-notes.md

---
