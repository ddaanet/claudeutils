# Cycle 4.6

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-6-notes.md`

---

## Cycle 4.6: Handle missing stats-cache.json gracefully

**Objective**: get_api_usage() returns None when stats-cache.json doesn't exist (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks Path.exists() to return False, asserts get_api_usage() returns None without raising exception

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: '~/.claude/stats-cache.json'
```

**Why it fails:** No file existence check or exception handling

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_missing_file -xvs
- Must fail with FileNotFoundError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Check Path.exists() before reading, return None if doesn't exist

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Add if not stats_file.exists(): return None at start of get_api_usage()

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_missing_file -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-6-notes.md

---
