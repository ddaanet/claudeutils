# Cycle 1.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.3: Container detection — in `-wt` parent

**Objective:** Detect when repository is already inside a worktree container directory.

**RED Phase:**

**Test:** `test_wt_path_in_container`
**Assertions:**
- When `Path.cwd().parent.name` ends with `-wt`, `wt_path("feature-b")` returns sibling path (not nested container)
- Returned path is `<parent-container>/<slug>` (parent already is the container)
- Path does NOT contain nested `-wt/-wt` structure
- Container name matches parent directory name exactly

**Expected failure:** AssertionError: path contains nested `-wt/-wt` or doesn't recognize existing container

**Why it fails:** Container detection logic not yet implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_in_container -v`

---

**GREEN Phase:**

**Implementation:** Add container detection branch to `wt_path()` function

**Behavior:**
- Check if `Path.cwd().parent.name.endswith('-wt')`
- If true: current directory is already in a container, return `parent/<slug>`
- If false: use existing logic from 1.2 (create new container path)

**Approach:** Conditional branch at function start — container check determines path construction strategy

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add container detection conditional at start of `wt_path()` function
  Location hint: Before existing path construction logic from 1.2

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_in_container -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_wt_path_not_in_container -v`
- Cycle 1.2 test still passes (existing behavior preserved)

---
