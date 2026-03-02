## 2026-03-02: Submodule conflict check runs after parent merge commit

### Bug

`_phase4_merge_commit_and_precommit` (merge.py:347-357) checks for submodule MERGE_HEAD AFTER creating the parent merge commit. By then, parent MERGE_HEAD is consumed. When user resolves submodule conflict and re-runs `claudeutils _worktree merge`, `_detect_merge_state` sees no MERGE_HEAD + branch already merged → state `"merged"` → phase 4 creates a regular 1-parent commit on top of the real merge.

Result: two commits instead of one. `_is_merge_of(slug)` checks HEAD (the fixup commit, 1 parent), returns false, so `_update_session_and_amend` skips the amend.

### Evidence

ups-topic-injection merge: `2dee5252` (real merge, 2 parents) → `07040e89` (submodule fixup, 1 parent). rm checked `07040e89`, amend didn't trigger.

### Fix

Move submodule conflict check before the parent merge commit in phase 4. Sequence should be:
1. `remerge_learnings_md()` / `remerge_session_md()`
2. `_append_lifecycle_delivered()`
3. **Check submodule MERGE_HEAD — exit 3 if unresolved**
4. Create merge commit (staging includes submodule pointer)
5. Run precommit

This ensures the submodule resolution is staged into the merge commit, producing a single 2-parent commit.

### Affected code

- `src/claudeutils/worktree/merge.py` lines 347-357 (move before line 305)
- Test: merge with submodule conflict → resolve → re-run → verify single merge commit with 2 parents
