# Cycle 1.4: new with submodule branching

**Date:** 2026-02-10
**Status:** GREEN_VERIFIED
**Test Command:** `just test -xvs tests/test_worktree_new.py::test_new_submodule`

## Phases

### RED Phase

Created test `test_new_submodule` in `/Users/david/code/claudeutils/tests/test_worktree_new.py`:
- Verifies submodule is initialized in worktree after `new` command
- Checks that submodule branch matches worktree slug (test-feature)
- Confirms branch exists in submodule (not detached HEAD)

Test initially passed (git's default behavior creates the branch automatically when creating worktree), indicating the feature is already partially working via git's default submodule handling.

### GREEN Phase

Implemented submodule branching in `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py`:
- Added explicit branch creation after submodule initialization
- After `git submodule update --init`, run `git -C {submodule_path} checkout -B {slug}`
- Used `-B` flag to handle case where branch already exists (force reset to current HEAD)
- Added error handling: exit 1 with stderr on branch creation failure

Code change (lines 189-199 in cli.py):
- Check if submodule directory exists
- Create/checkout branch matching worktree slug
- Report stderr and exit 1 if branch creation fails

Test passes with implementation: Branch is properly set to worktree slug after initialization.

### Regression Check

Full test suite: 751/752 passed (1 xfail for known preprocessor bug)
- No new test failures introduced
- All existing worktree tests still pass
- `test_new_submodule` in test_worktree_new.py passes

### Refactoring

**Line limit fix:** Original test_worktree_cli.py exceeded 400-line limit at 531 lines
- Created new file `test_worktree_new.py` for `new` subcommand tests
- Extracted 4 tests: `test_new_collision_detection`, `test_new_directory_collision`, `test_new_basic_flow`, `test_new_submodule_branching` (renamed to `test_new_submodule`)
- Extracted helper functions to new file: `_init_git_repo`, `_setup_repo_with_submodule`
- Original file reduced from 531 to 112 lines (well under limit)
- New file 289 lines (under limit)

**Code formatting:** Lint and precommit pass with no changes needed

**Final state:**
- `tests/test_worktree_cli.py`: 112 lines (under 400)
- `tests/test_worktree_new.py`: 289 lines (under 400)
- All tests passing
- All precommit checks passing

## Files Modified

- `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py` — Added submodule branch creation logic
- `/Users/david/code/claudeutils/tests/test_worktree_cli.py` — Removed `new` command tests and helpers
- `/Users/david/code/claudeutils/tests/test_worktree_new.py` — Created new test file for `new` subcommand

## Stop Conditions

None encountered. Cycle completed successfully.

## Decisions Made

**-B vs -b flag:** Used `-B` instead of `-b` for `git checkout` because git's worktree mechanism automatically creates and checks out the submodule on the parent branch. Forcing reset with `-B` ensures idempotent behavior.

**Test file split:** Split test files to keep each under 400-line limit. Separated `new` subcommand tests into dedicated file (`test_worktree_new.py`) while keeping import/ls tests in original file.
