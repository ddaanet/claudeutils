# Cycle 4.3

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-3-notes.md`

---

## Cycle 4.3: Handle missing switchback plist gracefully

**Objective**: read_switchback_plist() returns None when plist doesn't exist (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_account_switchback.py mocks Path.exists() to return False, asserts read_switchback_plist() returns None

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: '~/Library/LaunchAgents/...'
```

**Why it fails:** read_switchback_plist() doesn't check if file exists before reading

**Verify RED:** pytest tests/test_account_switchback.py::test_read_switchback_plist_missing -xvs
- Must fail with FileNotFoundError
- If passes, STOP - file existence check may already exist

---

**GREEN Phase:**

**Implementation:** Check Path.exists() before attempting to load plist, return None if doesn't exist

**Changes:**
- File: src/claudeutils/account/switchback.py
  Action: Add if not plist_path.exists(): return None at start of read_switchback_plist()

**Verify GREEN:** pytest tests/test_account_switchback.py::test_read_switchback_plist_missing -xvs
- Must pass

**Verify no regression:** pytest tests/
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-3-notes.md

---
