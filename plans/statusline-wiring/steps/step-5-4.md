# Cycle 5.4

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-5-4-notes.md`

---

## Cycle 5.4: Format and output two-line statusline with real data

**Objective**: statusline() uses StatuslineFormatter to format and print two lines (R1)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py provides full JSON stdin with all fields, mocks all data functions, asserts output contains two lines with model emoji, directory, git branch, cost, context tokens

**Expected failure:**
```
AssertionError: "OK" == "<line1>\\n<line2>"
```

**Why it fails:** CLI still outputs "OK" stub

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_outputs_two_lines -xvs
- Must fail with output mismatch (stub vs real output)
- If passes, STOP - real output may already exist

---

**GREEN Phase:**

**Implementation:** Replace click.echo("OK") with StatuslineFormatter calls to format line 1 and line 2, print both lines

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Import StatuslineFormatter, create formatter instance, format line 1 (model + dir + git + cost + context), format line 2 (mode + usage), click.echo() both lines

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_outputs_two_lines -xvs
- Must pass (two-line output with real data)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-4-notes.md

---
