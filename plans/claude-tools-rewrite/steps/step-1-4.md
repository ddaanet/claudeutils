# Cycle 1.4

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.4: AccountState validation - plan mode requires OAuth

**Objective**: Detect inconsistency when mode=plan but oauth_in_keychain=False
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** validate_consistency() returns issue when plan mode missing OAuth

**Expected failure:**
```
AssertionError: assert [] == ['Plan mode requires OAuth credentials in keychain']
```

**Why it fails:** validate_consistency() returns empty list (stub)

**Verify RED:** `pytest tests/test_account_state.py::test_validate_plan_requires_oauth -xvs`
- Must fail with assertion mismatch
- If passes, STOP - validation may already exist

---

**GREEN Phase:**

**Implementation:** Add plan mode OAuth validation check

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In validate_consistency(), add check: if mode == "plan" and not oauth_in_keychain, append issue
- File: tests/test_account_state.py
  Action: Test plan mode with oauth_in_keychain=False returns specific issue

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_plan_requires_oauth -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-4-notes.md

---
