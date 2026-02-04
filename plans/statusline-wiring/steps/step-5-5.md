# Cycle 5.5

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-5-5-notes.md`

---

## Cycle 5.5: Wrap CLI in try/except and always exit 0

**Objective**: statusline() catches all exceptions, logs to stderr, always exits 0 (R5, D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_cli.py mocks one of the data functions to raise Exception, asserts CLI exits 0 and logs error to stderr (not stdout)

**Expected failure:**
```
SystemExit: 1
```

**Why it fails:** CLI doesn't catch exceptions yet, lets them propagate

**Verify RED:** pytest tests/test_statusline_cli.py::test_statusline_exits_zero_on_error -xvs
- Must fail with non-zero exit code
- If passes with exit 0, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap entire statusline() body in try/except, catch all exceptions, log to stderr with click.echo(err=True), always return (implicit exit 0)

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Add try/except around entire function body, except Exception as e: click.echo(f"Error: {e}", err=True), ensure no explicit exit(1) calls

**Verify GREEN:** pytest tests/test_statusline_cli.py::test_statusline_exits_zero_on_error -xvs
- Must pass (exit code 0, error on stderr)

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-5-5-notes.md

---

**Light Checkpoint** (end of Phase 5)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 5 implementations against design. Check for stubs.

---
