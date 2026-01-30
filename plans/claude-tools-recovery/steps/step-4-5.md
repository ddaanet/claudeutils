# Cycle 4.5

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.5: Integration test - full account status flow

**Objective**: End-to-end test with mocked filesystem and keychain

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Full account status flow with all components

**Expected failure:**
```
AssertionError: integration not complete (one component still stubbed)
```

**Why it fails:** Not all wiring complete until previous cycles

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_integration -v`
- Must fail (at least one assertion fails)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create comprehensive integration test

**Changes:**
- File: tests/test_account.py
  Action: Create test_account_status_integration:
    - Fixture: tmp_path with mode, provider, .env files
    - Mock: Path.home() → tmp_path
    - Mock: Keychain queries (OAuth present, API key present)
    - Run: `account status`
    - Assert: Output contains mode, provider, OAuth status, API key status
    - Assert: Output contains consistency validation results

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_integration -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Full account status flow works end-to-end

**Error Conditions**: RED passes → STOP (wiring incomplete); GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: All components integrated, realistic flow

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-5-notes.md

---
