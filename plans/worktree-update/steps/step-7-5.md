# Cycle 7.5

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.5: Phase 2 submodule resolution — fetch if needed (with object check)

**Objective:** Fetch worktree's submodule commit if unreachable in local repo.

**RED Phase:**

**Test:** `test_merge_submodule_fetch`
**Assertions:**
- Before fetching: check object reachability with `git -C agent-core cat-file -e <wt-commit>`
- If object exists locally (exit 0): skip fetch (optimization)
- If object doesn't exist locally (exit ≠ 0): fetch from worktree
- Fetch command: `git -C agent-core fetch <wt-path>/agent-core HEAD`
- After fetch: object becomes reachable (can proceed to merge)
- Only fetch when needed (not unconditional)

**Expected failure:** AssertionError: unconditional fetch, or no object reachability check

**Why it fails:** Fetch logic not implemented, or always runs regardless of object existence

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_submodule_fetch -v`

---

**GREEN Phase:**

**Implementation:** Add conditional fetch based on object reachability

**Behavior:**
- From 7.4: have `wt_commit` and `needs_merge` flag
- If `needs_merge == False`: skip entirely (already ancestor)
- Check object reachability: `git -C agent-core cat-file -e <wt-commit>` with `check=False`
- If exit code 0: object exists, skip fetch
- If exit code ≠ 0: object missing, run `git -C agent-core fetch <wt-path>/agent-core HEAD`
- Fetch makes object available for merge in 7.6

**Approach:** Conditional fetch based on cat-file check, optimization for local objects

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add object reachability check in `merge` command
  Location hint: After ancestry check from 7.4
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `cat-file -e` to check if object exists
  Location hint: Use subprocess with check=False
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditional fetch if object missing
  Location hint: Only run fetch when cat-file exit code ≠ 0

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_submodule_fetch -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_merge_submodule_ancestry -v`
- Cycle 7.4 test still passes

---
