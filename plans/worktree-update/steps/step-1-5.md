# Cycle 1.5

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.5: Container creation — directory materialization

**Objective:** Create container directory when it doesn't exist (filesystem side effect).

**RED Phase:**

**Test:** `test_wt_path_creates_container`
**Assertions:**
- Before calling `wt_path()`, container directory doesn't exist
- After calling `wt_path("slug", create_container=True)`, container directory exists on filesystem
- Created directory has correct name (`<repo-name>-wt`)
- Created directory is empty (no files inside)
- Directory permissions are default (0o755 on Unix)

**Expected failure:** AssertionError: container directory doesn't exist after function call, or NameError: `create_container` parameter doesn't exist

**Why it fails:** `wt_path()` currently only computes paths, doesn't create directories

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_creates_container -v`

---

**GREEN Phase:**

**Implementation:** Add optional container creation to `wt_path()` function

**Behavior:**
- Add `create_container: bool = False` parameter to function signature
- When `create_container=True` and not in container, create the container directory
- Use `Path.mkdir(parents=True, exist_ok=True)` for idempotent creation
- Only create when NOT already in container (no-op if in container)

**Approach:** Conditional directory creation after path computation, only when flag is True and container doesn't exist

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `create_container` parameter to `wt_path()` signature
  Location hint: After `slug` parameter, with default `False`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add directory creation logic after path computation (when not in existing container)
  Location hint: At end of function, conditional on parameter

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_creates_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous tests still pass (default `create_container=False` preserves existing behavior)

---
