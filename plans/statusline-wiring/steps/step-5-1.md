# Cycle 5.1

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-5-1-notes.md`

---

## Cycle 5.1: Parse JSON stdin into StatuslineInput in CLI

**Objective**: statusline() CLI command reads stdin, parses JSON into StatuslineInput model (D1)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py uses Click CliRunner to invoke statusline with JSON stdin, asserts JSON parsing succeeds without error

**Expected failure:**
```
AssertionError: exit_code == 0, but no real output (still returns "OK" stub)
```

**Why it fails:** CLI doesn't import or use StatuslineInput yet

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_parses_json -xvs
- Must fail with stub behavior (output == "OK" instead of real statusline)
- If passes with real output, STOP - StatuslineInput parsing may already exist

---

**GREEN Phase:**

**Implementation:** Update statusline() to parse JSON into StatuslineInput model (no output yet, just parse)

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import StatuslineInput, replace json.loads() with StatuslineInput.model_validate_json(input_data)

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_parses_json -xvs
- Must pass (no exception raised)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-1-notes.md

---
