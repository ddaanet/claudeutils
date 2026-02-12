# Cycle 1.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.4: Sibling path when in container — multiple slugs

**Objective:** Verify sibling path logic works for multiple worktrees in same container.

**RED Phase:**

**Test:** `test_wt_path_siblings`
**Assertions:**
- When in container, `wt_path("wt-a")` and `wt_path("wt-b")` return different paths
- Both paths share same parent directory (the container)
- Paths differ only in final slug component
- Neither path creates nested containers

**Expected failure:** Test should pass immediately (logic from 1.3 already handles this), or fails if implementation incorrectly creates nested structure

**Why it might fail:** Path construction incorrectly nests containers for multiple calls

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_siblings -v`

---

**GREEN Phase:**

**Implementation:** Verify existing logic handles multiple sibling paths correctly

**Behavior:**
- Function is stateless (pure function of slug input)
- Each call with different slug returns different path with same parent
- No side effects or state that would interfere with multiple calls

**Approach:** Existing implementation from 1.3 should already satisfy this — verify with test

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Verify logic (likely no changes needed if 1.3 implemented correctly)
  Location hint: Review `wt_path()` function for stateless behavior

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_siblings -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous tests still pass

---
