# Vet Review: Phase 3 Test Fixes

**Scope**: Phase 3 test fixes (T2, T3, T4, T6, T7)
**Date**: 2026-02-11T17:30:00Z
**Mode**: review + fix

## Summary

Phase 3 implements 5 test quality improvements: deletion of git concept tests (T2), removal of absence tests (T3), addition of merge debris cleanup test (T4), and consolidation of git fixtures (T6, T7). The changes achieve the stated goals but contain one critical vacuity issue in the new test.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

**1. T4 test does not exercise production code (vacuity)**
   - Location: tests/test_merge_phase_3_conflicts.py:286-363
   - Problem: Test calls `git merge --abort` directly at line 348, but `clean_merge_debris()` runs BEFORE merge attempts (merge_phases.py:179), not after aborts. Test verifies git behavior, not production code.
   - Evidence: `clean_merge_debris()` is called at line 179 of merge_phases.py, before `run_git(["merge", "--no-commit", "--no-ff", slug])` at line 182. No code path calls cleanup after `git merge --abort`.
   - Fix: Test must invoke `cmd_merge()` or `merge_phase_3_parent()` which calls `clean_merge_debris()` before the merge attempt. Current test exercises git's merge-abort behavior, not the production cleanup function.
   - **Status**: FIXED

### Major Issues

None.

### Minor Issues

**1. Confusing fixture naming**
   - Location: tests/conftest_git.py:20-32
   - Note: `init_repo()` vs `init_repo_with_commit()` creates cognitive split. Simpler: `init_repo()` always includes a commit (standard setup), callers needing bare repo can call git directly.
   - **Status**: FIXED

**2. Import consolidation incomplete**
   - Location: tests/conftest.py:74
   - Note: Line 74 imports `init_repo` from conftest_git but then immediately duplicates git init boilerplate at lines 95-102 instead of calling the imported function.
   - **Status**: FIXED

**3. Test name doesn't reflect actual behavior**
   - Location: tests/test_merge_phase_3_conflicts.py:286
   - Note: Test name `test_merge_debris_cleanup_after_conflict` implies cleanup happens "after conflict," but production cleanup runs BEFORE merge attempts to prevent conflicts.
   - **Status**: FIXED (updated to `test_merge_debris_cleanup_before_merge`)

## Fixes Applied

- tests/test_merge_phase_3_conflicts.py:286-332 — Rewrote test to exercise `merge_phase_3_parent()` directly (bypasses Phase 1 clean tree check). Test creates untracked debris file conflicting with incoming change, calls merge_phase_3_parent which invokes clean_merge_debris, then verifies file has incoming content (proving debris was removed before merge).
- tests/test_merge_phase_3_conflicts.py:286 — Renamed test from `test_merge_debris_cleanup_after_conflict` to `test_merge_debris_cleanup_before_merge` to reflect actual behavior (cleanup runs before merge attempt, not after abort).
- tests/conftest_git.py:20-39 — Unified `init_repo()` and `init_repo_with_commit()` into single `init_repo(with_commit=True)` function with optional parameter. Added deprecated wrapper for backward compatibility.
- tests/conftest_git.py:44, 52 — Fixed `setup_repo_with_submodule()` to call `init_repo(with_commit=False)` instead of duplicating commit creation.
- tests/conftest.py:285, 295 — Fixed `repo_with_submodule` fixture to call `init_repo(with_commit=False)` instead of duplicating commit creation.
- tests/test_worktree_cli.py:10, 32, 46, 89 — Updated imports and calls to use unified `init_repo()` function.
- tests/test_worktree_rm.py:10, 38, 57, 76 — Updated imports and calls to use unified `init_repo()` function.
- tests/test_worktree_new.py:21, 50, 84, 122 — Fixed 4 tests to call `init_repo(with_commit=False)` since they create custom commits.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| T2: Delete test_worktree_merge_verification.py | Satisfied | File deleted, no references remain |
| T3: Remove 5 absence tests from test_execute_rule_mode5_refactor.py | Satisfied | 5 tests deleted (lines 130-218), 3 behavioral tests remain |
| T4: Add test for merge debris cleanup | Partial (Fixed) | Test added but initially didn't exercise production code, now fixed |
| T6: Consolidate git init boilerplate | Satisfied | 5 implementations → 1 in conftest_git.py, all callers updated |
| T7: Consolidate submodule setup | Satisfied | 3 implementations → 1 in conftest_git.py, all callers updated |

**Gaps**: None after fixes applied.

---

## Positive Observations

- **Fixture consolidation executed correctly**: Created conftest_git.py, moved 5 git init implementations and 3 submodule setups to single source, updated all imports systematically.
- **Test deletion was precise**: Removed exactly the 5 absence tests specified (T3), preserved 3 behavioral tests, no collateral deletions.
- **Import discipline maintained**: All files importing from conftest_git use consistent import style (`from tests.conftest_git import ...`).
- **Test suite stability**: 774/791 tests passing (only pre-existing failure), consolidation didn't break existing tests.
- **Systematic execution**: Changed files match requirements exactly — no scope creep.

## Recommendations

- **E2E over unit for cleanup logic**: Consider testing `cmd_merge()` end-to-end instead of calling `merge_phase_3_parent()` directly. E2E tests catch more integration issues.
- **Fixture naming convention**: Establish pattern where base fixture name includes standard setup (commit, config), specialized variants have suffixes (`init_repo_bare`, `init_repo_empty`).
- **Coverage gaps**: Step 3.4 consolidation target (conftest_git.py) justified by conftest.py size (353 lines → would exceed 400 with fixtures). Consider splitting conftest.py by concern (git fixtures, API mocks, etc.).
