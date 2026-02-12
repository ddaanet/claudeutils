# Cycle 1.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.1: `wt_path()` basic path construction with CLI group registration

**Objective:** Register worktree CLI group and extract path computation into testable function for the simplest case (repository not in worktree container).

**Prerequisite:** Read `src/claudeutils/cli.py` lines 1-50 — understand Click group registration pattern and existing command structure. Read `src/claudeutils/worktree/cli.py` lines 1-100 — understand existing worktree creation logic and path handling patterns.

**RED Phase:**

**Test:** `test_wt_path_not_in_container`
**Assertions:**
- Import succeeds: `from claudeutils.worktree.cli import worktree` does not raise ImportError
- Group is callable: `isinstance(worktree, click.Group)` is True
- `wt_path("feature-a")` returns Path ending with `claudeutils-wt/feature-a`
- Returned path parent directory name ends with `-wt`
- Returned path is absolute (not relative)
- Container directory does not exist yet (creation happens later)

**Expected failure:** ImportError (group not registered in main CLI) or NameError (function `wt_path` not defined)

**Why it fails:** `cli.add_command(worktree)` not yet added to main CLI, and `wt_path()` function doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`

---

**GREEN Phase:**

**Implementation:** Register worktree CLI group and extract path computation into standalone `wt_path(slug)` function

**Behavior:**
- Import statement added to main CLI imports section
- Command registered via `cli.add_command(worktree)` call
- Underscore prefix automatically hides from help (Click convention)
- New `wt_path(slug)` function takes slug as string input, returns Path object
- Detects current directory is NOT in `-wt` container (parent name doesn't end with `-wt`)
- Constructs container name: `<current-repo-name>-wt`
- Returns: `<parent-of-repo>/<repo-name>-wt/<slug>`

**Approach:** Follow existing command registration pattern in `src/claudeutils/cli.py`, then port bash `wt-path()` function logic from justfile (lines 100-120)

**Changes:**
- File: `src/claudeutils/cli.py`
  Action: Add import `from claudeutils.worktree.cli import worktree` at top
  Location hint: With other command imports
- File: `src/claudeutils/cli.py`
  Action: Add `cli.add_command(worktree)` registration call
  Location hint: After other command registrations
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new function `wt_path(slug: str) -> Path` before `new` command definition
  Location hint: At module level, before command functions
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement logic — detect parent directory, check for `-wt` suffix, construct container path if not in container
  Location hint: Function body uses `Path.cwd()`, `.parent.name`, string operations

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_cli_*.py -v`
- All existing CLI tests pass

---
