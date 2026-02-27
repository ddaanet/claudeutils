# Review: merge-learnings-delta FR-1 + FR-2 implementation

**Scope**: `src/claudeutils/worktree/remerge.py` (FR-2 reporting), `tests/test_learnings_consolidation.py` (FR-1 + FR-2 tests)
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

Both files are clean implementations that satisfy their requirements. All 9 tests pass and `just precommit` exits clean. The reporting logic in `remerge.py` correctly computes kept/appended/dropped counts. The test file covers all 5 pure-function scenarios, both integration merge directions, and both reporting branches (output on change, silence on noop).

One minor issue found: `base_segs` is computed by parsing `base_content` a second time when the same content was already parsed inline as an argument to `diff3_merge_segments`. No bugs, but the variable name suggests it has wider use than it does. Identified and FIXED.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`base_segs` double-parse**
   - Location: `src/claudeutils/worktree/remerge.py:66`
   - Note: `base_content` is parsed into `parse_segments(base_content)` inline on line 40 (as the first arg to `diff3_merge_segments`) and then re-parsed into `base_segs` on line 66 for the `dropped` computation. The second parse produces an identical result but adds a redundant function call. The fix is to capture the parsed base at the call site instead of re-parsing.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/remerge.py:40,66` — Capture `parse_segments(base_content)` into `base_segs` before the `diff3_merge_segments` call and pass `base_segs` as the argument, eliminating the second parse on line 66.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: consolidation+new scenario | Satisfied | `test_consolidation_with_new_entries` |
| FR-1: consolidation-only scenario | Satisfied | `test_consolidation_no_new_entries` |
| FR-1: modified-consolidated-away scenario | Satisfied | `test_modified_consolidated_away_entry` |
| FR-1: modified-surviving scenario | Satisfied | `test_modified_surviving_entry` |
| FR-1: no-consolidation baseline | Satisfied | `test_no_consolidation_both_added` |
| FR-1: integration branch→main direction | Satisfied | `test_branch_to_main_consolidation` |
| FR-1: integration main→branch direction | Satisfied | `test_main_to_branch_consolidation` |
| FR-2: report format when segments change | Satisfied | `test_reports_counts_when_segments_change` asserts exact string |
| FR-2: silent when no-op | Satisfied | `test_silent_on_noop` asserts no `"learnings.md:"` prefix in stdout |
| NFR-1: reporting does not cause merge failure | Satisfied | reporting block unreachable on conflict path (conflicts raise SystemExit(3) before reporting) |
| NFR-2: no new dependencies | Satisfied | only `parse_segments` (existing) used |

---

## Positive Observations

- Conflict path correctly exits before reaching the reporting block — NFR-1 satisfied by structure, not by defensive code.
- `test_silent_on_noop` uses a non-trivially-different scenario (other files changed, learnings unchanged) rather than testing identical trees — produces genuine merge state without shortcutting via early returns.
- `test_modified_consolidated_away_entry` asserts conflict presence rather than full merge result — appropriate because the conflict path is the signal; body content is secondary.
- Pure-function tests use dict literals directly, keeping setup proportional to the scenario complexity.
- `dropped` computation correctly targets entries that were in `base` AND `theirs` but absent from merged — this precisely captures "theirs still had it but ours consolidated it away," excluding entries deleted by both sides.
