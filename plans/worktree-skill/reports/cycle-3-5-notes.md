# Cycle 3.5: Phase 2 Post-verification

**Date:** 2026-02-10
**Status:** GREEN_VERIFIED (implementation complete, refactoring deferred)
**Test command:** `just test tests/test_worktree_merge_verification.py`

## RED Phase

**Test:** `test_merge_phase_2_post_verification_success` and `test_merge_phase_2_post_verification_corrupted`

**Expected Failure:** Tests pass initially because they test the logical correctness of ancestry verification (not dependent on full merge flow).

**Actual Result:** Tests created correctly but revealed need for proper test data setup. Separated post-verification tests into dedicated test file for readability and to manage file size.

## GREEN Phase

**Implementation:** Added post-merge verification to `cmd_merge()` in `src/claudeutils/worktree/commands.py`

**Location:** After diverged submodule merge, lines 516-590

**Logic:**
1. Extract final submodule HEAD: `git -C agent-core rev-parse HEAD`
2. Verify worktree commit is ancestor: `git merge-base --is-ancestor <wt-commit> HEAD`
3. Verify local commit is ancestor: `git merge-base --is-ancestor <local-commit> HEAD`
4. If either check fails, exit 2 with descriptive error message

**Test Results:**
- `test_merge_phase_2_post_verification_success`: PASS
- `test_merge_phase_2_post_verification_corrupted`: PASS
- All merge tests: 3/3 passed (no regressions)
- Full test suite: 770/771 passed, 1 xfail (known preprocessor bug)

## REFACTOR Phase

**Status:** Deferred (complexity warnings flagged by precommit)

**Quality Check Output:**
```
src/claudeutils/worktree/commands.py:354:5: C901 `cmd_merge` too complex (17 > 10)
src/claudeutils/worktree/commands.py:354:5: PLR0912 Too many branches (17 > 12)
src/claudeutils/worktree/commands.py:354:5: PLR0915 Too many statements (66 > 50)
src/claudeutils/worktree/commands.py:      602 lines (exceeds 400 line limit)
```

**Findings:**
- Post-verification implementation added 75 lines of nested condition handling
- `cmd_merge()` function grew to 248 lines (was 173), exceeding architectural guidelines
- Complexity stems from three independent verification blocks (ancestry checks for both commits + error handling)

**Refactoring Plan (for next cycle):**
- Extract post-verification logic into separate `_verify_submodule_merge()` function
- Move verification function to dedicated module `claudeutils/worktree/verify.py`
- Reduces cmd_merge() to ~150 lines, improves readability
- Example:
  ```python
  def _verify_submodule_merge(wt_commit, local_commit):
      """Verify both commits are ancestors of final submodule HEAD."""
      # Returns True on success, raises SystemExit(2) on failure
  ```

**Files Modified:**
- `src/claudeutils/worktree/commands.py` — Added post-verification logic
- `tests/test_worktree_merge_verification.py` — New file with dedicated post-verification tests
- `tests/test_worktree_merge.py` — Trimmed to Phase 2 optimization tests only

## Decision Made

**Architectural Decision:** Post-verification uses exit code 2 (per design.md FR-2) to distinguish verification failures from other merge errors. This allows merge ceremony (skill) to distinguish "logical error in submodule state" from "workflow error" and communicate appropriately to user.

**Test Organization:** Separated post-verification tests from Phase 2 optimization tests to:
- Reduce file size (test_worktree_merge.py: 320 lines, test_worktree_merge_verification.py: 280 lines)
- Improve test cohesion (verification tests independent of full merge flow)
- Simplify future refactoring of merge implementation

## Next Steps

1. **Cycle 3.6:** Extract verification logic to reduce `cmd_merge()` complexity
2. **Phase 3:** Implement parent merge orchestration (currently returns after Phase 2)
