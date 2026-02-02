# Cycle 1.5

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.5: AccountState validation - API mode requires key

**Objective**: Detect inconsistency when mode=api but no API key available
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** validate_consistency() returns issue when API mode without key

**Expected failure:**
```
AssertionError: assert [] == ['API mode requires API key in environment or helper enabled']
```

**Why it fails:** API mode validation not implemented

**Verify RED:** `pytest tests/test_account_state.py::test_validate_api_requires_key -xvs`
- Must fail with assertion mismatch
- If passes, STOP - validation may already exist

---

**GREEN Phase:**

**Implementation:** Add API mode key validation check

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In validate_consistency(), add check: if mode == "api" and not (api_in_claude_env or has_api_key_helper), append issue
- File: tests/test_account_state.py
  Action: Test API mode without key or helper returns specific issue

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_api_requires_key -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-5-notes.md

---
