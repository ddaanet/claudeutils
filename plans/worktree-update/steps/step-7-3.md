# Cycle 7.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.3: Phase 1 pre-checks — branch existence and worktree directory check

**Objective:** Verify branch exists and optionally warn about missing worktree directory.

**RED Phase:**

**Test:** `test_merge_branch_existence`
**Assertions:**
- When branch doesn't exist: exit 2 with message "Branch <slug> not found"
- When branch exists but worktree directory doesn't: warning printed, merge continues (branch-only merge valid)
- When both exist: no warning, merge proceeds
- Exit code 2 for fatal errors (branch missing), exit 1 for conflicts/precommit, exit 0 for success

**Expected failure:** AssertionError: no branch check, or error on missing worktree directory

**Why it fails:** Branch existence validation not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_branch_existence -v`

---

**GREEN Phase:**

**Implementation:** Add branch existence check and directory warning

**Behavior:**
- Run `git rev-parse --verify <slug>` with `check=False`
- If exit code ≠ 0: exit 2 with "Branch <slug> not found"
- Check if `<wt-path>` exists on filesystem
- If not exists: print warning "Worktree directory not found, merging branch only"
- Continue merge (branch-only merge is valid)

**Approach:** Subprocess with exit code check, filesystem check with conditional warning

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add branch existence check in `merge` command
  Location hint: After clean tree checks
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `git rev-parse --verify <slug>`, exit 2 on failure
  Location hint: Use subprocess with check=False
- File: `src/claudeutils/worktree/cli.py`
  Action: Add worktree directory check with warning
  Location hint: After branch check, use `Path(<wt-path>).exists()`

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_branch_existence -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 pre-check tests still pass

---
