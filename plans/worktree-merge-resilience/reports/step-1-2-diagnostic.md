# Step 1.2 Regression Diagnostic

## Root Cause

`_detect_merge_state(slug)` returned `"merged"` for branches pointing to the same commit as HEAD (branch tip == HEAD), because `git merge-base --is-ancestor A B` returns exit 0 when A == B (every commit is its own ancestor).

This caused `merge()` to route directly to Phase 4, skipping Phase 1 validation and Phase 2 submodule resolution.

## Affected Tests

Three tests created branches at HEAD with no unique commits:

- `test_merge_ours_clean_tree`: `git branch test-slug` at HEAD → state "merged" → Phase 1 skipped → dirty-tree check never ran → test expected "Clean tree required" in output
- `test_merge_branch_existence`: `git branch branch-only` at HEAD → state "merged" → Phase 1 skipped → "Worktree directory not found" warning never printed
- `test_merge_submodule_fetch`: `git branch fetch-test` at HEAD (before `worktree new`, no commits to branch after) → state "merged" → Phase 2 skipped → `merge-base --is-ancestor` call for submodule never made

## Why `_detect_merge_state` Was Not Changed

`test_detect_state_merged` explicitly creates a branch at HEAD, merges it (no-op "Already up to date"), then asserts `_detect_merge_state` returns `"merged"`. Changing `_detect_merge_state` to use strict ancestor check would break this test.

The "merged" detection is correct per its contract: a branch at HEAD is already an ancestor of HEAD. The routing in `merge()` was wrong.

## Fix

Changed `merge()` routing for `"merged"` state to run Phase 1 and Phase 2 before Phase 4:

```python
if state == "merged":
    _phase1_validate_clean_trees(slug)   # added
    _phase2_resolve_submodule(slug)      # added
    _phase4_merge_commit_and_precommit(slug)
```

Phase 3 (parent merge) is correctly skipped — the branch is already merged, no merge commit needed. But Phase 1 (validation + clean tree + warnings) and Phase 2 (submodule reconciliation) must still run.

## Verification

```
pytest tests/ -k "merge" --ignore=tests/test_worktree_merge_conflicts.py
# 64/64 passed

pytest tests/ --ignore=tests/test_worktree_merge_conflicts.py
# 1030/1046 passed, 16 skipped
```

All previously passing tests continue to pass. All 3 regressions fixed.
