# Cycle 3.2

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.2: Handle missing config files gracefully

**Objective**: Test get_account_state() uses defaults when config files missing
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_state.py should test factory returns default state when files missing

**Expected failure:**
```
FileNotFoundError or returns None instead of default state
```

**Why it fails:** Factory doesn't handle missing file case

**Verify RED:**
```bash
pytest tests/test_account_state.py::test_get_account_state_missing_files -v
```
- Create test with empty tmp_path (no .claude dir)
- Mock Path.home() to return tmp_path
- Assert returns AccountState with mode="plan", provider="anthropic" defaults
- Test should FAIL if factory raises exception

---

**GREEN Phase:**

**Implementation:** Add default fallback when config files don't exist

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In get_account_state(), wrap file reads in try/except FileNotFoundError, use defaults
- File: tests/test_account_state.py
  Action: Create test file, add test with missing files, assert default state

**Verify GREEN:**
```bash
pytest tests/test_account_state.py::test_get_account_state_missing_files -v
```
- Test passes with default state

**Verify no regression:**
```bash
pytest tests/test_account_state.py -v
```
- All state tests pass

---

**Expected Outcome**: State factory handles missing files with defaults
**Error Conditions**: Exception raised → add try/except around file reads
**Validation**: Test verifies default state returned
**Success Criteria**: Factory robust to missing configuration
**Report Path**: plans/claude-tools-recovery/reports/cycle-3-2-notes.md

---
