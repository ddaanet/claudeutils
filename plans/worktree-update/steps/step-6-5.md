# Cycle 6.5

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.5: Safe branch deletion — `-d` with fallback warning

**Objective:** Use safe branch deletion (`-d`) that checks merge status, warn on unmerged instead of force-deleting.

**RED Phase:**

**Test:** `test_rm_safe_branch_deletion`
**Assertions:**
- Branch deletion uses `git branch -d <slug>` (NOT `-D`)
- When branch fully merged: deletion succeeds, no warning
- When branch has unmerged changes: deletion fails, warning printed
- Warning message: "Branch <slug> has unmerged changes. Use: git branch -D <slug>"
- Warning includes manual command for user (no automatic force-delete)
- Exit code 0 even when branch deletion fails (warning, not error)

**Expected failure:** AssertionError: `-D` used instead of `-d`, or error raised on unmerged branch, or no warning printed

**Why it fails:** Command uses `-D` (force delete) or doesn't handle unmerged branch case

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_safe_branch_deletion -v`

---

**GREEN Phase:**

**Implementation:** Add safe branch deletion with graceful failure handling

**Behavior:**
- Run `git branch -d <slug>` with `check=False` (capture exit code)
- If exit code 0 (success): deletion complete
- If exit code ≠ 0 (unmerged): print warning message with manual `-D` command
- Do NOT run `git branch -D` automatically (user decision required)
- Continue execution (don't raise exception on unmerged)

**Approach:** Subprocess with error handling, conditional warning, no automatic force-delete

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add branch deletion in `rm` command
  Location hint: After directory cleanup
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `git branch -d <slug>` with `check=False`
  Location hint: Use subprocess.run, capture exit code
- File: `src/claudeutils/worktree/cli.py`
  Action: Check exit code, print warning if non-zero
  Location hint: Conditional on exit code, include manual `-D` command in message

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_safe_branch_deletion -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 6 tests still pass

---

# Phase 7: Add `merge` Command (4-Phase Ceremony)

**Complexity:** High (12 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Implement 4-phase merge ceremony — clean tree gate, submodule resolution, parent merge with auto-resolution, precommit validation.

**Dependencies:** Phase 1 (needs `wt_path()` for directory resolution)

---
