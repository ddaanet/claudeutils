# Cycle 6.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.1: Refactor `rm` to use `wt_path()` and add uncommitted changes warning

**Objective:** Update `rm` command to use `wt_path()` for consistent path resolution and warn about dirty trees.

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` — understand current `rm` command implementation.

**RED Phase:**

**Test:** `test_rm_command_path_resolution`
**Assertions:**
- `claudeutils _worktree rm test-slug` resolves to sibling container path `<repo>-wt/test-slug`
- Path resolution consistent with `new` command (uses same `wt_path()` function)
- When worktree has uncommitted changes: warning printed before removal
- Warning contains count of uncommitted files: "Warning: worktree has N uncommitted files"
- Removal proceeds after warning (not blocked)

**Expected failure:** AssertionError: wrong path used, or no warning on dirty tree

**Why it fails:** Command uses hardcoded path logic, doesn't check for uncommitted changes

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_command_path_resolution -v`

---

**GREEN Phase:**

**Implementation:** Refactor to use `wt_path()` and add dirty tree check

**Behavior:**
- Replace path construction with `wt_path(slug)` call (no create_container flag for removal)
- Check if worktree path exists on filesystem
- If exists: run `git -C <wt-path> status --porcelain` to check for uncommitted changes
- If output non-empty: count lines, print warning (don't block removal)
- Proceed with removal logic

**Approach:** Replace path logic, add subprocess status check, conditional warning

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace path construction in `rm` command with `wt_path(slug)` call
  Location hint: Near start of function
- File: `src/claudeutils/worktree/cli.py`
  Action: Add dirty tree check using git status
  Location hint: After path resolution, before removal steps
- File: `src/claudeutils/worktree/cli.py`
  Action: Print warning if uncommitted changes found
  Location hint: Conditional on status --porcelain output

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_command_path_resolution -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All existing `rm` command tests still pass

---
