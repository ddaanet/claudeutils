# Session Handoff: 2026-02-24

**Status:** Bug fixed — dirty worktree no longer blocks merge.

## Completed This Session

**Fix wt merge dirty-tree guard:**
- Removed `_check_clean_for_merge(path=wt_path(slug), label="worktree")` from `_phase1_validate_clean_trees` in `src/claudeutils/worktree/merge.py` — merge operates on branch ref, not working tree
- Added `test_phase1_allows_dirty_worktree` to `tests/test_worktree_merge_correctness.py` — verifies dirty worktree (modified tracked file) + clean main passes phase 1
- Deleted `test_merge_theirs_clean_tree` from `tests/test_worktree_clean_tree.py` — was testing the removed behavior

## Pending Tasks

## Next Steps

Merge this worktree back to main (`wt merge wt-merge-dirty-tree`).
