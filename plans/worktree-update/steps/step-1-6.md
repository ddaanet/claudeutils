# Cycle 1.6

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.6: Edge cases — special characters, root directory, deep nesting

**Objective:** Handle edge cases in path computation (unusual but valid scenarios).

**RED Phase:**

**Test:** `test_wt_path_edge_cases`
**Assertions:**
- Slug with special characters preserved in path: `wt_path("fix-bug#123")` includes `#123` in path
- From root directory: `wt_path("test")` doesn't crash, constructs valid path
- From deeply nested directory (5+ levels): path construction still works correctly
- Empty container case: if manually in empty `-wt` directory, sibling path still computed

**Expected failure:** Various: ValueError on special chars, error on root directory, incorrect path from deep nesting

**Why it fails:** Edge cases not yet handled in path computation logic

**Verify RED:** `pytest tests/test_worktree_cli.py::test_wt_path_edge_cases -v`

---

**GREEN Phase:**

**Implementation:** Add edge case handling to `wt_path()` function

**Behavior:**
- Special characters in slug: preserve as-is (filesystem will handle)
- Root directory: detect via `Path.cwd() == Path("/")`, construct reasonable container path
- Deep nesting: existing logic already handles (uses `.parent` which works at any depth)
- Error on truly invalid slug (e.g., empty string, only whitespace): raise ValueError

**Approach:** Add validation at function start, handle root directory special case, rely on pathlib for deep nesting

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add slug validation at function start (check for empty/whitespace)
  Location hint: First lines of function
- File: `src/claudeutils/worktree/cli.py`
  Action: Add root directory detection and handling
  Location hint: Before container detection logic

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_wt_path_edge_cases -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All previous tests still pass

---

# Phase 2: Sandbox Registration

**Complexity:** Medium (4 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** JSON manipulation for sandbox permissions — add worktree container to allowed directories.

**Dependencies:** Phase 1 (needs `wt_path()` for container determination)

---
