# Cycle 1.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: Register `_worktree` CLI group and verify hidden from help

**Objective:** Register the worktree CLI group in main CLI and verify underscore prefix hides it from help output.

**Prerequisite:** Read `src/claudeutils/cli.py` lines 1-50 — understand Click group registration pattern and existing command structure.

**RED Phase:**

**Test:** `test_worktree_group_registered`
**Assertions:**
- Import succeeds: `from claudeutils.worktree.cli import worktree` does not raise ImportError
- Group is callable: `isinstance(worktree, click.Group)` is True
- Help output does NOT contain "_worktree" string (hidden due to underscore prefix)
- Direct invocation works: `claudeutils _worktree --help` exits 0 with help text

**Expected failure:** ImportError (group not registered in main CLI) or AttributeError (worktree not added to cli)

**Why it fails:** `cli.add_command(worktree)` not yet added to `src/claudeutils/cli.py`

**Verify RED:** `pytest tests/test_worktree_cli.py::test_worktree_group_registered -v`

---

**GREEN Phase:**

**Implementation:** Register worktree CLI group in main CLI module

**Behavior:**
- Import statement added to main CLI imports section
- Command registered via `cli.add_command(worktree)` call
- Underscore prefix automatically hides from help (Click convention)

**Approach:** Follow existing command registration pattern in `src/claudeutils/cli.py` (other commands use same `add_command()` pattern)

**Changes:**
- File: `src/claudeutils/cli.py`
  Action: Add import `from claudeutils.worktree.cli import worktree` at top
  Location hint: With other command imports
- File: `src/claudeutils/cli.py`
  Action: Add `cli.add_command(worktree)` registration call
  Location hint: After other command registrations (e.g., after statusline, commit commands)

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_worktree_group_registered -v`
- Must pass

**Verify no regression:** `pytest tests/test_cli_*.py -v`
- All existing CLI tests pass

---
