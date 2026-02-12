# Cycle 7.6

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.6: Phase 2 submodule resolution — merge and commit

**Objective:** Merge worktree's submodule commit into local submodule and commit.

**RED Phase:**

**Test:** `test_merge_submodule_merge_commit`
**Assertions:**
- When merge needed (from 7.4): run `git -C agent-core merge --no-edit <wt-commit>`
- After merge: stage submodule with `git add agent-core`
- Commit with message: `🔀 Merge agent-core from <slug>`
- Only commit if staged changes exist (check `git diff --cached --quiet`)
- When no merge needed: skip merge and commit (no-op)

**Expected failure:** AssertionError: no merge performed, or wrong commit message, or commit when no changes

**Why it fails:** Submodule merge logic not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_submodule_merge_commit -v`

---

**GREEN Phase:**

**Implementation:** Add submodule merge and commit logic

**Behavior:**
- From 7.4-7.5: have `needs_merge` flag and `wt_commit` (fetched if needed)
- If `needs_merge == False`: skip entirely
- Run `git -C agent-core merge --no-edit <wt-commit>`
- Stage: `git add agent-core`
- Check if staged: `git diff --cached --quiet agent-core` (exit ≠ 0 means changes)
- If staged changes: `git commit -m "🔀 Merge agent-core from <slug>"`
- If no staged changes: skip commit

**Approach:** Conditional merge based on flag, staging check before commit

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule merge in `merge` command
  Location hint: After fetch logic from 7.5
- File: `src/claudeutils/worktree/cli.py`
  Action: Run merge, stage, check for staged changes, commit
  Location hint: Sequential subprocess calls conditional on `needs_merge` flag

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_submodule_merge_commit -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 2 tests still pass

---
