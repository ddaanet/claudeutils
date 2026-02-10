# Cycle 3.9: Idempotent merge - resume after conflict resolution

**Status:** RED_VERIFIED, GREEN_VERIFIED, Quality warnings found

**Test:** `test_merge_idempotent_resume_after_conflict_resolution`
**Test file:** `tests/test_worktree_merge.py`

## RED Phase Result

**Expected:** Test fails with merge conflicts detected, requiring manual resolution

**Actual:** PASS ✓
- Test creates source code conflict (non-session file)
- First merge invocation exits 1 with "Merge conflicts detected"
- MERGE_HEAD is set, confirming merge in progress state
- Test verifies expected failure behavior

## GREEN Phase Result

**Expected:** After manual staging, merge resumes and completes successfully

**Actual:** PASS ✓
- Implemented MERGE_HEAD detection in Phase 1 (line 426-433 in commands.py)
  - Check if merge already in progress before requiring clean tree
  - Allows dirty tree if MERGE_HEAD exists (manual resolution state)
- Implemented MERGE_HEAD detection in Phase 3 (line 682-689 in commands.py)
  - Skip `git merge` command if merge already active
  - Proceed directly to conflict checking and commit
- Test verifies merge completes without re-invoking git merge
- Merge commit is created with correct gitmoji
- Both branches' changes are integrated into final commit
- MERGE_HEAD is cleared after successful completion

## Regression Check

**Result:** PASS ✓
- Full test suite: 774/775 passed, 1 xfail (known preprocessor bug)
- All worktree merge tests pass
- No regressions introduced

## Refactoring

**Complexity warnings found:**
- `src/claudeutils/worktree/commands.py:417` (cmd_merge function)
  - C901: cyclomatic complexity 27 (limit 10)
  - PLR0912: too many branches 35 (limit 12)
  - PLR0915: too many statements 115 (limit 50)
- `src/claudeutils/worktree/commands.py`: 788 lines (exceeds 400 line limit)
- `tests/test_worktree_merge.py`: 872 lines (exceeds 400 line limit)

**Architectural observation:**
The cmd_merge function has grown to encompass three complex phases with extensive submodule handling, conflict resolution, and idempotency logic. The function now coordinates:
- Phase 1: Pre-checks with idempotent state detection
- Phase 2: Submodule resolution with ancestry checking and merge verification
- Phase 3: Parent merge with conflict detection, automatic resolution, and precommit gating

The current implementation is correct but violates structural limits. Refactoring required before proceeding to next phase.

## Files Modified

- `src/claudeutils/worktree/commands.py` — Added MERGE_HEAD detection for idempotent merge
- `tests/test_worktree_merge.py` — Added idempotent resume test

## Design Decisions

- **D-8:** Idempotent merge is architectural requirement (from design)
- **NFR-1:** Resume after conflicts (from design)
- **Implementation:** Use `git rev-parse --verify MERGE_HEAD` to detect in-progress merge state
- **Phase 1 change:** Allow dirty tree if merge in progress (user staging manual resolution)
- **Phase 3 change:** Skip git merge if MERGE_HEAD exists, proceed to conflict checking

## Stop Condition

**Status:** STOP - Quality check warnings found

- Precommit validation found complexity and line limit violations
- Per TDD protocol: escalate to refactor agent for architectural resolution
- Do NOT attempt inline refactoring during TDD cycle

## Next Steps

1. Escalate warnings to refactor agent (sonnet)
2. After refactoring: continue with Cycle 3.10 (merge with automatic --ours resolution)
