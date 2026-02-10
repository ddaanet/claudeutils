# Cycle 2.4: Jobs conflict status advancement

**Status:** GREEN_VERIFIED
**Timestamp:** 2026-02-10

## Phase Summary

This cycle implements deterministic jobs.md conflict resolution with status ordering.

## RED Phase

**Test written:** Added two test cases to `tests/test_session_conflicts.py`:
- `test_resolve_jobs_conflict_advances_status`: Verifies status advancement when theirs has higher status
- `test_resolve_jobs_conflict_outlined_status_ordering`: Verifies "outlined" status ordering

**Expected failure:** ImportError - function doesn't exist
**Actual result:** ✓ Test failed as expected with ImportError

## GREEN Phase

**Implementation:** Created `resolve_jobs_conflict(ours: str, theirs: str) -> str` function in `src/claudeutils/worktree/conflicts.py`

**Algorithm:**
1. Defined status ordering tuple: `("requirements", "designed", "outlined", "planned", "complete")`
2. Used regex pattern `^\| ([^\|]+) \| ([^\|]+) \|` with MULTILINE flag to parse table rows
3. Built plan→status maps for both ours and theirs
4. Compared status indices: if theirs status index > ours status index, advance ours
5. Reconstructed jobs.md with updated statuses using regex substitution

**Test results:** ✓ Both tests pass
**Regression check:** ✓ Full suite: 763/764 passed, 1 xfail (known)

## REFACTOR Phase

**Lint:** Initial run found PLC0206 (extract dictionary without .items())
- Fixed: Changed `for plan in theirs_status_map:` to `for plan, theirs_status in theirs_status_map.items()`
- Result: ✓ Lint OK

**Precommit:** ✓ Precommit OK

## Files Modified

- `src/claudeutils/worktree/conflicts.py` - Added resolve_jobs_conflict function (55 lines)
- `tests/test_session_conflicts.py` - Added two test cases (49 lines)

## Verification

- RED verified: Test fails with expected ImportError
- GREEN verified: Tests pass; no regressions (763/764 passed)
- Refactoring: Lint and precommit pass
- Commit: 9d7e4d9 clean and complete

## Decision Made

None - straightforward implementation following algorithm hints from step definition.

## Notes

- Status ordering includes all five states as specified: requirements, designed, outlined, planned, complete
- Preserves all other jobs.md content unchanged
- Plans not in both versions are ignored (merge doesn't add new plans)
- Notes column preserved exactly
