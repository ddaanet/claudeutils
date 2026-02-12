# Cycle 7.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.4: Phase 2 submodule resolution — ancestry check

**Objective:** Determine if worktree's submodule commit needs merging (or is already ancestor).

**RED Phase:**

**Test:** `test_merge_submodule_ancestry`
**Assertions:**
- Extract worktree's submodule commit: `git ls-tree <slug> -- agent-core` returns commit SHA
- Compare to local: `git -C agent-core rev-parse HEAD` returns local commit SHA
- When commits identical: skip submodule merge (no-op)
- When worktree commit is ancestor of local: skip merge (already merged)
- When worktree commit is NOT ancestor: proceed to merge (Cycle 7.5-7.6)
- Ancestry check uses `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`

**Expected failure:** AssertionError: no ancestry check, or wrong merge decision

**Why it fails:** Submodule ancestry logic not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_submodule_ancestry -v`

---

**GREEN Phase:**

**Implementation:** Add submodule ancestry check logic

**Behavior:**
- Extract worktree's submodule commit: `git ls-tree <slug> -- agent-core | awk '{print $3}'`
- Get local submodule commit: `git -C agent-core rev-parse HEAD`
- If commits identical: skip submodule merge
- Check ancestry: `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>` with `check=False`
- If exit code 0 (is ancestor): skip submodule merge
- If exit code ≠ 0 (not ancestor): proceed to merge (flag for 7.5-7.6)

**Approach:** Subprocess calls to extract commits and check ancestry, conditional branching

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule commit extraction in `merge` command
  Location hint: After Phase 1 checks (Phase 2 start)
- File: `src/claudeutils/worktree/cli.py`
  Action: Extract worktree submodule commit from ls-tree
  Location hint: Parse `git ls-tree <slug> -- agent-core` output
- File: `src/claudeutils/worktree/cli.py`
  Action: Get local submodule commit
  Location hint: `git -C agent-core rev-parse HEAD`
- File: `src/claudeutils/worktree/cli.py`
  Action: Compare commits and check ancestry
  Location hint: Use merge-base --is-ancestor, capture exit code

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_submodule_ancestry -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 and 7.4 tests still pass

---
