# Cycle 1.7: rm branch-only cleanup

**Execution timestamp:** 2026-02-10 16:45 UTC

## Status

`STOP_CONDITION: precommit-failed`

## RED Phase

**Test command:** `just test`

**Result:** FAIL as expected

Test `test_rm_branch_only` fails because `rm` doesn't handle branch-only cleanup (when worktree directory is missing externally but branch remains).

Error: Git still tracks worktree registration after manual directory deletion, preventing branch deletion.

## GREEN Phase

**Result:** PASS after 1 attempt

Implementation strategy:
- Added `git worktree prune` call when worktree directory doesn't exist
- Prune cleans up stale worktree registrations
- Branch deletion with `-D` flag succeeds after prune

Key insight: Git maintains internal worktree list separately from filesystem. Manually deleting directory leaves stale registration. Prune removes these phantom entries.

Modified `rm` subcommand:
- Check if worktree directory exists
- If missing: call `git worktree prune` to clean stale registration
- Then delete branch with `-D` (force) flag

Result: Test passes, branch is removed cleanly after manual directory deletion.

## Regression Check

`just test` shows: 755/756 passed, 1 xfail (known preprocessor bug)

No regressions introduced.

## Refactoring

`just lint` passed after reformatting.

Line count increased to 403 in `tests/test_worktree_cli.py` (exceeds 400-line limit).

## STOP CONDITION

**Precommit validation failed:**

```
❌ tests/test_worktree_cli.py:      403 lines (exceeds 400 line limit)
```

File `tests/test_worktree_cli.py` now 403 lines, exceeding 400-line hard limit.

This requires file split refactoring (beyond cycle scope). Escalating to sonnet refactor agent.

## Files Modified

- `src/claudeutils/worktree/cli.py` (rm subcommand updated with prune logic)
- `tests/test_worktree_cli.py` (new test_rm_branch_only test added)

## WIP Commit

```
d079e5f WIP: Cycle 1.7: rm branch-only cleanup
```

Staged and committed before precommit failure. Ready for rollback if refactoring fails.

## Decision Made

Implementation is correct and tested. Line limit violation requires structural change (file split), not implementation fix. Refactoring scope: split test file into logical modules or consolidate existing tests.
