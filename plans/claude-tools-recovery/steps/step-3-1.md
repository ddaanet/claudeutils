# Cycle 3.1

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.1: Wire AccountState factory to read filesystem

**Objective**: Replace hardcoded AccountState with real file reading

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.1 should now fail

**Expected failure:**
```
AssertionError: expected 'Mode: plan', got 'Mode: <hardcoded>'
```

**Why it fails:** AccountState still returns hardcoded values

**Verify RED:** Run `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must fail with fixture assertion
- If passes, STOP - implementation may already be real

---

**GREEN Phase:**

**Implementation:** Update AccountState factory to read ~/.claude/account-mode and account-provider files

**Changes:**
- File: claudeutils/account/state.py
  Action: Update create_account_state() or AccountState constructor:
    - Read: Path.home() / ".claude" / "account-mode"
    - Read: Path.home() / ".claude" / "account-provider"
    - Parse: Strip whitespace, set AccountState.mode and AccountState.provider
    - Handle: Missing files → default values or None

**Verify GREEN:** `pytest tests/test_account.py::test_account_status_reads_files -v`
- Must pass

**Verify no regression:** `pytest tests/test_account.py`
- All tests pass

---

**Expected Outcome**: AccountState reads real files instead of hardcoded values

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation reads filesystem, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-1-notes.md

---
