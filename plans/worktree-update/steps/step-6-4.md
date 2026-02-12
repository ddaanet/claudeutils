# Cycle 6.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.4: Post-removal cleanup — orphaned directories and empty container

**Objective:** Clean up orphaned worktree directories and empty containers after git removal.

**RED Phase:**

**Test:** `test_rm_post_removal_cleanup`
**Assertions:**
- After git worktree removal, if `<wt-path>` still exists (orphaned): directory removed with `shutil.rmtree()`
- After directory removal, if container is empty: container directory removed with `os.rmdir()`
- Empty check uses `os.listdir()` returning empty list
- Non-empty container NOT removed (other worktrees present)
- Cleanup idempotent (running twice has same effect as once)

**Expected failure:** AssertionError: orphaned directories remain, or non-empty container removed, or FileNotFoundError

**Why it fails:** No filesystem cleanup after git commands

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_post_removal_cleanup -v`

---

**GREEN Phase:**

**Implementation:** Add filesystem cleanup logic after git removal

**Behavior:**
- After git worktree remove commands: check if `<wt-path>` still exists
- If exists (orphaned): use `shutil.rmtree()` to remove directory tree
- After path cleanup: get container directory (parent of `<wt-path>`)
- Check if container empty: `not os.listdir(container_path)`
- If empty: remove container with `os.rmdir()`
- If not empty or doesn't exist: skip container removal

**Approach:** Filesystem checks with conditional cleanup, use pathlib for path operations

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add orphaned directory cleanup in `rm` command
  Location hint: After git worktree remove commands
- File: `src/claudeutils/worktree/cli.py`
  Action: Check if `<wt-path>` exists, remove with `shutil.rmtree()` if present
  Location hint: Use `Path.exists()` and `shutil.rmtree()`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add container cleanup logic
  Location hint: After path cleanup
- File: `src/claudeutils/worktree/cli.py`
  Action: Check if container empty, remove with `os.rmdir()` if empty
  Location hint: Use `os.listdir()` for empty check, `os.rmdir()` for removal

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_post_removal_cleanup -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous Cycle 6 tests still pass

---
