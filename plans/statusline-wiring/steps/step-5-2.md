# Cycle 5.2

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-5-2-notes.md`

---

## Cycle 5.2: Call context.py functions in CLI orchestration

**Objective**: statusline() calls get_git_status(), get_thinking_state(), calculate_context_tokens() (D4 thin CLI)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py mocks context module functions, asserts statusline() calls all three functions

**Expected failure:**
```
AssertionError: mock not called
```

**Why it fails:** CLI doesn't call context functions yet

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_calls_context_functions -xvs
- Must fail with mock not called
- If passes, STOP - context calls may already exist

---

**GREEN Phase:**

**Implementation:** Add calls to context.py functions in statusline() (store results in local vars, no output yet)

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import context functions, call get_git_status(), get_thinking_state(), calculate_context_tokens(input_data)

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_calls_context_functions -xvs
- Must pass (all mocks called)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-2-notes.md

---
