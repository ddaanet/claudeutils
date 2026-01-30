# Cycle 2.6

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.6: Strengthen account api command test

**Objective**: Mock filesystem and keychain, assert mode file and claude-env generated

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test account api writes mode file and generates claude-env with credentials

**Expected failure:**
```
AssertionError: claude-env file not created or missing credentials
```

**Why it fails:** Stub doesn't generate claude-env

**Verify RED:** Run `pytest tests/test_account.py::test_account_api_switch -v`
- Must fail (claude-env not created or empty)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Mock keychain, run account api, assert mode file and claude-env

**Changes:**
- File: tests/test_account.py
  Action: Create/update test_account_api_switch:
    - Fixture: tmp_path
    - Mock: `patch("claudeutils.account.state.Path.home", return_value=tmp_path)`
    - Mock: `patch("claudeutils.account.providers.subprocess.run")` returns API key
    - Run: `account api`
    - Assert: tmp_path/.claude/account-mode == "api\n"
    - Assert: tmp_path/.claude/.env exists and contains ANTHROPIC_API_KEY (or provider key)
    - Assert: Output confirms switch

**Verify GREEN:** `pytest tests/test_account.py::test_account_api_switch -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Test verifies mode file and claude-env generation

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts both files written with correct content

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-6-notes.md

---
