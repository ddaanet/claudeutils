# Cycle 2.5

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-5-notes.md`

---

## Cycle 2.5: Handle missing or malformed settings.json

**Objective**: get_thinking_state() returns ThinkingState(enabled=False) when settings.json missing or invalid JSON
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks Path.exists() to return False, asserts get_thinking_state() returns ThinkingState(enabled=False)

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: '~/.claude/settings.json'
```

**Why it fails:** No exception handling for missing file

**Verify RED:** pytest tests/test_statusline_context.py::test_get_thinking_state_missing_file -xvs
- Must fail with FileNotFoundError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap file read and JSON parse in try/except, return ThinkingState(enabled=False) on FileNotFoundError or json.JSONDecodeError

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add try/except around Path.open and json.load, catch FileNotFoundError and json.JSONDecodeError, return ThinkingState(enabled=False)

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_thinking_state_missing_file -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-5-notes.md

---
