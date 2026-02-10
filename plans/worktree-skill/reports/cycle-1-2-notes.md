# Cycle 1.2: new with collision detection

**Status:** GREEN_VERIFIED
**Timestamp:** 2026-02-10 14:35 UTC

## Phase Results

### RED Phase
- **Test command:** `python -m pytest tests/test_worktree_cli.py::test_new_collision_detection tests/test_worktree_cli.py::test_new_directory_collision -v`
- **Result:** FAIL as expected
- **Failure type:** Both tests failed:
  - `test_new_collision_detection`: Error message present but missing specific keywords ("existing" or "collision" check)
  - `test_new_directory_collision`: Command exit code 0 (success) when it should have exited with 1 (error)

### GREEN Phase
- **Test command:** `python -m pytest tests/test_worktree_cli.py::test_new_collision_detection tests/test_worktree_cli.py::test_new_directory_collision -v`
- **Result:** PASS
- **Implementation:** Added collision detection to `new` subcommand:
  - Check for existing directory at `wt/{slug}` before attempting creation
  - Check for existing branch using `git rev-parse --verify {slug}`
  - Report specific error message to stderr for each collision type
  - Exit with code 1 on collision, 0 on success

### Regression Check
- **Full suite:** `python -m pytest tests/test_worktree_cli.py -v`
- **Result:** 8/8 tests passed
- **Full project:** `just test`
- **Result:** 750/751 passed, 1 xfail (known preprocessor bug)
- **Status:** No regressions introduced

## Refactoring

### Lint & Format
- **Command:** `just lint`
- **Status:** PASS
- **Changes:** Formatter wrapped long lines in test function signatures for readability

### Precommit Validation
- **Command:** `just precommit`
- **Status:** PASS
- **Warnings:** None

## Files Modified

- `src/claudeutils/worktree/cli.py` — Added collision detection logic to `new` command
- `tests/test_worktree_cli.py` — Added two new test cases: `test_new_collision_detection` and `test_new_directory_collision`

## Implementation Details

**Directory collision check:** Uses `Path.exists()` for simple filesystem check.

**Branch collision check:** Uses `git rev-parse --verify {slug}` which returns exit code 0 if branch exists, non-zero otherwise. This is more reliable than parsing `git branch` output.

**Error messages:** Distinct messages for each collision type help users understand what went wrong.

## Decision Made

None — implementation followed cycle specification directly.

## Stop Condition

None — cycle completed successfully.
