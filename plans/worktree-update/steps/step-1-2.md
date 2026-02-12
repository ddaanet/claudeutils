# Cycle 1.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.2: `wt_path()` basic path construction — not in container

**Objective:** Extract path computation into testable function for the simplest case (repository not in worktree container).

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` lines 1-100 — understand existing worktree creation logic and path handling patterns.

**RED Phase:**

**Test:** `test_wt_path_not_in_container`
**Assertions:**
- `wt_path("feature-a")` returns Path ending with `claudeutils-wt/feature-a`
- Returned path parent directory name ends with `-wt`
- Returned path is absolute (not relative)
- Container directory does not exist yet (creation happens later)

**Expected failure:** NameError: function `wt_path` not defined

**Why it fails:** Function doesn't exist yet, needs extraction from CLI code

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`

---

**GREEN Phase:**

**Implementation:** Extract path computation into standalone `wt_path(slug)` function

**Behavior:**
- Takes slug as string input, returns Path object
- Detects current directory is NOT in `-wt` container (parent name doesn't end with `-wt`)
- Constructs container name: `<current-repo-name>-wt`
- Returns: `<parent-of-repo>/<repo-name>-wt/<slug>`

**Approach:** Port bash `wt-path()` function logic from justfile (lines 100-120) — same container detection and path construction rules

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new function `wt_path(slug: str) -> Path` before `new` command definition
  Location hint: At module level, before command functions
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement logic — detect parent directory, check for `-wt` suffix, construct container path if not in container
  Location hint: Function body uses `Path.cwd()`, `.parent.name`, string operations

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All existing worktree tests pass

---
