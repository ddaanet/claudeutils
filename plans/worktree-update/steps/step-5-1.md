# Cycle 5.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.1: Refactor `new` to use `wt_path()` — sibling paths and branch reuse

**Objective:** Update `new` command to use `wt_path()` for sibling container paths and detect existing branches for reuse.

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` — understand current `new` command implementation (uses `wt/<slug>` paths, creates branches unconditionally).

**RED Phase:**

**Test:** `test_new_command_sibling_paths`
**Assertions:**
- `claudeutils _worktree new test-wt` creates worktree at `<repo>-wt/test-wt` (not `wt/test-wt`)
- Worktree path is sibling to repo directory
- Container directory created if doesn't exist
- When branch "existing-branch" already exists: `new existing-branch` reuses branch without error (no `-b` flag passed to git)
- When branch doesn't exist: normal branch creation with `-b` flag

**Expected failure:** AssertionError: worktree created at old `wt/<slug>` location, or error when reusing existing branch

**Why it fails:** Command uses hardcoded `wt/` path, doesn't check for existing branches

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_command_sibling_paths -v`

---

**GREEN Phase:**

**Implementation:** Refactor `new` command to use `wt_path()` function and detect existing branches

**Behavior:**
- Replace hardcoded `wt/<slug>` path construction with `wt_path(slug, create_container=True)` call
- Before creating branch: check `git rev-parse --verify <slug>` exit code
- If branch exists (exit 0): use `git worktree add <path> <slug>` (no `-b` flag)
- If branch doesn't exist (exit 1): use existing logic with `-b` flag
- Path output at end uses actual sibling path from `wt_path()`

**Approach:** Replace path logic, add branch detection subprocess call, conditional git worktree add command

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace path construction in `new` command with `wt_path(slug, create_container=True)` call
  Location hint: Near start of `new` function, where path is determined
- File: `src/claudeutils/worktree/cli.py`
  Action: Add branch existence check using subprocess to run `git rev-parse --verify <slug>`
  Location hint: Before git worktree add command
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditional git command based on branch existence
  Location hint: Replace unconditional branch creation with conditional logic

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_command_sibling_paths -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All existing `new` command tests still pass

---
