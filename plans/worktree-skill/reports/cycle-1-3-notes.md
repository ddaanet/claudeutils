# Cycle 1.3: new with submodule initialization

**Timestamp:** 2026-02-10T21:35 UTC
**Status:** GREEN_VERIFIED

## Test Specification

- **Test name:** `test_worktree_cli.py::test_new_submodule_init`
- **Test file:** `tests/test_worktree_cli.py` (lines 275-394)

## RED Phase

**Result:** FAIL as expected ✓

Test created with assertion checking that submodule directory is populated after worktree creation. Initial implementation of `new` command did not initialize submodules, so test failed with:
```
AssertionError: Submodule directory is empty
assert 0 > 0
```

## GREEN Phase

**Result:** PASS ✓

Implementation added to `new` command in `src/claudeutils/worktree/cli.py`:

1. After `git worktree add` succeeds, retrieve project root via `git rev-parse --show-toplevel`
2. Check if `agent-core` directory exists in parent repo (indicates submodule present)
3. If present and initialized (has `.git`), run `git submodule update --init --reference <agent-core>` in the new worktree
4. The `--reference` flag uses local objects, avoiding remote fetches

Test now passes: submodule directory exists after worktree creation.

## Regression Check

**Result:** No regressions ✓

Full test suite: 751/752 passed (1 known xfail for unrelated preprocessor bug)

## Code Quality

**Formatting:** PASS ✓
- Reformatted via `just lint`
- Line limits: file is 391 lines (under 400 limit)

**Precommit validation:** PASS ✓
- All checks passed
- No linting errors

## Files Modified

1. `src/claudeutils/worktree/cli.py` — Added submodule initialization logic to `new` command (+33 lines)
2. `tests/test_worktree_cli.py` — Added `test_new_submodule_init` test (+120 lines)

## Refactoring

No refactoring performed. Code follows project conventions.

## Decision Made

Submodule initialization approach:
- Uses local agent-core repo as reference to avoid remote fetches
- Gracefully handles missing agent-core (continues without error)
- Initializes on every new worktree creation (no state check)

## Stop Condition

None. Cycle completed successfully.
