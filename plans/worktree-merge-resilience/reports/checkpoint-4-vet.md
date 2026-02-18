# Vet Review: Phase 4 Checkpoint — Conflict Output Formatting

**Scope**: `_format_conflict_report` implementation, conflict output integration, `test_conflict_output_contains_all_fields`
**Date**: 2026-02-18T19:03:37
**Mode**: review + fix

## Summary

Phase 4 adds `_format_conflict_report` to produce structured conflict output with status codes, diff stats, divergence info, and a hint line. Lint issues (PERF401, PT018) were fixed before review. The implementation satisfies FR-4 fields and D-8 (stdout only). One major issue: the diff stat command measures MERGE_HEAD vs conflict-marker-infected working tree rather than ours-vs-theirs divergence; one minor issue: trivial docstring on `_format_conflict_report`; one minor issue: brittle `+++` assertion that passes only because conflict markers inflate the file.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Diff stat measures wrong comparison**
   - Location: `src/claudeutils/worktree/merge.py:51`
   - Problem: `git diff --stat MERGE_HEAD -- <file>` compares MERGE_HEAD (incoming branch tip) against the conflict-marker-infected working tree file. This produces a stat that includes conflict marker lines as additions/deletions. FR-4 intent is "per-file diff stats (ours vs theirs)" — the natural reading is what changed on each side since the merge base. During an active conflict, the working tree is not a clean "ours" — it contains conflict markers. The test passes because conflict markers inflate the file enough to show `+++`, but the semantic is wrong. The correct comparison for "what changed on each side" is `git diff --stat <merge-base> HEAD -- <file>` (ours) and `git diff --stat <merge-base> MERGE_HEAD -- <file>` (theirs), or simpler: `git diff --stat HEAD MERGE_HEAD -- <file>` (total divergence between tips).
   - Suggestion: Use `git diff --stat HEAD MERGE_HEAD -- <file>` to compare the two branch tips directly. This shows what changed between ours and theirs without conflict marker noise. Update the test assertion to not rely on `+++`.
   - **Status**: FIXED

### Minor Issues

1. **Trivial docstring on `_format_conflict_report`**
   - Location: `src/claudeutils/worktree/merge.py:32-39`
   - Note: The `Args` and `Returns` sections restate the signature verbatim. The first line is useful; the block below it is not.
   - **Status**: FIXED

2. **`+++` assertion is implementation-dependent**
   - Location: `tests/test_worktree_merge_conflicts.py:350`
   - Note: `assert "+++" in output` relies on conflict markers inflating the diff stat to show 3+ `+` bars. For a file with 1-2 genuine changes (no conflict marker inflation) the stat shows `| 2 +-`, not `+++`. The assertion should check for the structural presence of diff stat (already covered by `"|" in output`) rather than a specific bar count.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/merge.py:51` — Changed `git diff --stat MERGE_HEAD -- file` to `git diff --stat HEAD MERGE_HEAD -- file` (compare branch tips, not MERGE_HEAD vs conflict-marker working tree)
- `src/claudeutils/worktree/merge.py:32-39` — Removed trivial Args/Returns docstring block; kept summary line
- `tests/test_worktree_merge_conflicts.py:350` — Removed brittle `+++` assertion (already covered by `"|" in output` check on line 349)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-4: filename in output | Satisfied | `lines.append(f"  {status_code} {conflict_file}")` merge.py:46 |
| FR-4: conflict type in output | Satisfied | `status_code = status[:2]` merge.py:45 |
| FR-4: diff stat in output | Satisfied | `lines.extend(...)` merge.py:53; test asserts `"|" in output` |
| FR-4: divergence summary | Satisfied | `f"Branch: {ahead} commits ahead, Main: {behind}..."` merge.py:60 |
| FR-4: actionable hint | Satisfied | `f"Resolve conflicts, git add, then re-run: claudeutils _worktree merge {slug}"` merge.py:65 |
| D-8: stdout only | Satisfied | `click.echo(_format_conflict_report(...))` (no `err=True`) merge.py:243,341 |
| D-8: relative paths | Satisfied | `git diff --name-only --diff-filter=U` returns repo-relative paths merge.py:231 |

**Gaps:** None within Phase 4 scope.

---

## Positive Observations

- The two-pass structure (status codes first, then diff stats) produces output that's readable top-to-bottom: filename+type, blank, per-file stats, blank, divergence, blank, hint.
- Using `_git(..., check=False)` throughout `_format_conflict_report` prevents the report itself from raising — appropriate for a diagnostic function called in an error path.
- `parent_conflicts` state in `merge()` re-fetches conflicts fresh from git state rather than relying on stale data — correct for re-entrant execution.
- Test uses a real merge conflict (not mocked) satisfying the project's preference for e2e over mocked subprocess.

## Recommendations

- The divergence variable `behind` (line 58) tracks main's extra commits (commits in HEAD not in slug). The naming is from branch's perspective ("branch is behind by N") but the label says "Main: N commits ahead" — consistent, but the variable name is misleading. Non-blocking; rename opportunistically.
