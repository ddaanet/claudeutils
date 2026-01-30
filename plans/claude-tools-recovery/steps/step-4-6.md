# Cycle 4.6

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.6: Integration test - account mode switching round-trip

**Objective**: Test plan → api → plan mode switches preserve state

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Switch plan → api → plan and verify state consistency

**Expected failure:**
```
AssertionError: round-trip state inconsistent
```

**Why it fails:** Integration not complete

**Verify RED:** Run `pytest tests/test_account.py::test_account_mode_roundtrip -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create round-trip integration test

**Changes:**
- File: tests/test_account.py
  Action: Create test_account_mode_roundtrip:
    - Fixture: tmp_path
    - Mock: Path.home() → tmp_path
    - Mock: Keychain (provider credentials)
    - Run: `account plan`
    - Assert: Mode file == "plan"
    - Run: `account api`
    - Assert: Mode file == "api", .env exists with credentials
    - Run: `account plan`
    - Assert: Mode file == "plan", .env still exists (or removed depending on design)

**Verify GREEN:** `pytest tests/test_account.py::test_account_mode_roundtrip -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: Mode switching works bidirectionally

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Round-trip preserves state correctly

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-6-notes.md

---
