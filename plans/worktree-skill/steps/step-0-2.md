# Cycle 0.2

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-2-notes.md`

---

## Cycle 0.2: Click Group Structure

**Objective:** Establish `_worktree` command group with help output.

**RED Phase:**
**Test:** `test_worktree_command_group`
**Assertions:**
- Running `claudeutils _worktree --help` via Click's CliRunner displays usage text
- Help output includes the command name `_worktree`
- Exit code is 0
**Expected failure:** `AttributeError` or import error (no `worktree` Click group exists)
**Why it fails:** The `cli.py` module has no Click command group definition.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_worktree_command_group -v`

---

**GREEN Phase:**
**Implementation:** Define Click command group with basic structure.
**Behavior:**
- Click group named `worktree` responds to `--help`
- Help text displays command group information
- Returns exit code 0 for help invocation
**Approach:** Use Click's `@click.group()` decorator on a function named `worktree`. Add a docstring for help text.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add Click group definition with decorator and docstring
  Location hint: Top level of module after imports
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_worktree_command_group -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-2-notes.md

---
