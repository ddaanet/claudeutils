# Cycle 4.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Cycle 4.4: Missing task error handling

**Objective:** Raise clear error when task name doesn't exist in session.md.

**RED Phase:**

**Test:** `test_focus_session_missing_task`
**Assertions:**
- Given session.md without task named "nonexistent-task"
- `focus_session("nonexistent-task", session_path)` raises ValueError
- Error message contains task name: "Task 'nonexistent-task' not found in session.md"
- Error message is actionable (helps user understand what went wrong)

**Expected failure:** No error raised (returns empty string or None) or wrong exception type

**Why it fails:** Function doesn't validate task existence before processing

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_missing_task -v`

---

**GREEN Phase:**

**Implementation:** Add task existence validation to `focus_session()` function

**Behavior:**
- After parsing session.md, check if task was found
- If task extraction returns None or empty: raise ValueError with clear message
- Message includes task name for debugging
- Validation happens before any section filtering (fail fast)

**Approach:** Check task extraction result, raise ValueError if None/empty with f-string message

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add task validation check in `focus_session()` function
  Location hint: After task extraction attempt, before blocker/reference filtering
- File: `src/claudeutils/worktree/cli.py`
  Action: Raise ValueError if task not found, with message including task name
  Location hint: Conditional check on task extraction result

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_missing_task -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 4 tests still pass

---

# Phase 5: Update `new` Command and Task Mode

**Complexity:** High (8 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_new.py`

**Description:** Refactor `new` command using extracted functions, add `--task` mode combining slug derivation and focused session generation.

**Dependencies:** Phases 1, 2, 4 (needs `wt_path()`, `add_sandbox_dir()`, `focus_session()`)

---
