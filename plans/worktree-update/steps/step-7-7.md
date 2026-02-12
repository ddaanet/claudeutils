# Cycle 7.7

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.7: Phase 3 parent merge — initiate merge

**Objective:** Initiate parent merge and detect conflicts.

**RED Phase:**

**Test:** `test_merge_parent_initiate`
**Assertions:**
- Run `git merge --no-commit --no-ff <slug>` (capture stdout and stderr)
- When merge succeeds (no conflicts): exit code 0, proceed to commit
- When conflicts occur: exit code ≠ 0, get conflict list from `git diff --name-only --diff-filter=U`
- No automatic commit (--no-commit flag ensures manual conflict handling possible)
- Non-fast-forward merge enforced (--no-ff preserves merge structure)

**Expected failure:** AssertionError: wrong git command, or auto-commit on success, or no conflict detection

**Why it fails:** Parent merge initiation not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_parent_initiate -v`

---

**GREEN Phase:**

**Implementation:** Add parent merge initiation with conflict detection

**Behavior:**
- Run `git merge --no-commit --no-ff <slug>` with `check=False` (capture exit code and output)
- If exit code 0: merge clean, proceed to commit (skip conflict handling)
- If exit code ≠ 0: conflicts occurred, get conflict list
- Conflict list: `git diff --name-only --diff-filter=U`
- Store conflict list for 7.8-7.11 auto-resolution logic

**Approach:** Subprocess with error handling, conflict detection via diff filter

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add parent merge initiation in `merge` command (Phase 3 start)
  Location hint: After Phase 2 submodule resolution
- File: `src/claudeutils/worktree/cli.py`
  Action: Run merge with --no-commit --no-ff flags
  Location hint: Use subprocess with check=False, capture exit code
- File: `src/claudeutils/worktree/cli.py`
  Action: Get conflict list if exit code ≠ 0
  Location hint: Run `git diff --name-only --diff-filter=U`

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_parent_initiate -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 and Phase 2 tests still pass

---
