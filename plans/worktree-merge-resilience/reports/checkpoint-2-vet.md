# Vet Review: Phase 2 Checkpoint — Submodule Conflict Handling

**Scope**: Phase 2 changes — `_phase2_resolve_submodule` check=False handling + two new tests
**Date**: 2026-02-18T17:22:14Z
**Mode**: review + fix

## Summary

Phase 2 correctly switches from `_git()` (check=True) to `subprocess.run(check=False)` for submodule merge, satisfying D-6. MERGE_HEAD preservation on conflict matches D-7. The two new tests verify the behavioral contract. Three issues found: dead subprocess calls in the conflict pipeline test, a misleading comment about expected exit code, and two E501 lint violations + 130-line overrun on the 400-line file limit. All fixed by extracting a shared setup helper that deduplicates the two conflict tests.

**Overall Assessment**: Needs Minor Changes (all fixed)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Test file exceeds 400-line limit by 130 lines**
   - Location: `tests/test_worktree_merge_submodule.py` (530 lines)
   - Problem: File limit is 400 lines per precommit check. `just dev` confirms `❌ 530 lines (exceeds 400 line limit)`. The two conflict tests (`test_submodule_conflict_does_not_abort_pipeline` and `test_merge_resume_after_submodule_resolution`) have ~45 lines of nearly identical setup code (agent-core commit, worktree creation, conflicting changes, pointer update, main-side conflict, pointer update). Extracting a shared `_setup_submodule_conflict` helper eliminates this duplication and brings the file under 400 lines.
   - **Status**: FIXED

### Minor Issues

1. **Dead subprocess.run calls in `test_submodule_conflict_does_not_abort_pipeline`**
   - Location: `tests/test_worktree_merge_submodule.py:316-321, 342-347`
   - Problem: Two `subprocess.run(...).stdout.strip()` calls capture rev-parse HEAD output but assign to nothing. Neither `base_commit` nor `wt_commit` is used later in this test — the variables are computed but only the side-effect of the git commit matters. Dead computation.
   - **Status**: FIXED (removed by shared helper extraction)

2. **Misleading comment in `test_merge_resume_after_submodule_resolution`**
   - Location: `tests/test_worktree_merge_submodule.py:443`
   - Problem: Comment says "First merge: should fail with submodule conflict (exit 3)" but the assertion is `in (0, 3)`. The submodule conflict leaves MERGE_HEAD in agent-core, but Phase 3 auto-resolves `agent-core` with `--ours` and Phase 4 commits — so exit 0 is a valid outcome. The comment misrepresents the expected behavior.
   - **Status**: FIXED

3. **E501 line-too-long violations (2 lines)**
   - Location: `tests/test_worktree_merge_submodule.py:510, 523`
   - Problem: Lines 510 (93 chars) and 523 (90 chars) exceed 88-char limit per ruff E501.
   - **Status**: FIXED (removed by shared helper extraction)

## Fixes Applied

- `tests/test_worktree_merge_submodule.py` — Added `_git()` helper wrapping subprocess.run (reduces repeated multi-line subprocess call blocks). Extracted `_setup_submodule_conflict()` helper encapsulating ~45 shared setup lines from both conflict tests. Removed dead subprocess.run calls (unassigned rev-parse HEAD in conflict test). Corrected misleading "exit 3" comment (→ "exit 0 or 3"). Both E501 violations eliminated. File reduced from 530 to 397 lines, passing precommit.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-6: `_git` must not raise on conflict | Satisfied | `merge.py:170-176`: `subprocess.run(check=False)` + return on non-zero |
| D-7: No data loss (MERGE_HEAD preserved) | Satisfied | `merge.py:175-176`: early return leaves MERGE_HEAD in agent-core; test asserts `merge_head_check.returncode == 0` |
| FR-1: Submodule conflict pass-through | Satisfied | `_phase2_resolve_submodule` returns without abort; state machine routes `submodule_conflicts` → Phase 3 on resume |
| Idempotent resume | Satisfied | `test_merge_resume_after_submodule_resolution` verifies second merge succeeds after manual resolution |

---

## Positive Observations

- `check=False` + early return is minimal and correct — no exception path, MERGE_HEAD stays in place
- Existing skip logic (wt_commit == local_commit early return) remains correct as no-op on already-resolved submodule
- Test uses real git repos (no subprocess mocking for git ops in the conflict tests), matching project testing convention
- `_update_submodule_pointer` helper prevents repeated git-add + git-commit boilerplate
- Assertions are behavioral (MERGE_HEAD presence, ancestor check, exit code range) not structural
