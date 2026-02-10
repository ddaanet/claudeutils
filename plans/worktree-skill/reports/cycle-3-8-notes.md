# Cycle 3.8: Phase 3 post-merge precommit gate

**Execution Date:** 2026-02-10

## RED Phase

**Test Name:** `test_merge_phase_3_post_merge_precommit_gate`

**Test Command:** `python -m pytest tests/test_worktree_merge.py::test_merge_phase_3_post_merge_precommit_gate -xvs`

**Expected Failure:** Test verifies precommit gate runs after merge commit is created and commit persists (not rolled back)

**Result:** PASS (implementation already exists)
- Merge command creates merge commit successfully
- Test verifies commit hash returned in output
- Test confirms no regressions in merge flow

**Note:** The precommit gate implementation was completed in cycle 3.7 as part of the Phase 3 parent merge logic. Cycle 3.8 adds the test verification that the gate works as specified.

## GREEN Phase

**Implementation:** Already complete from cycle 3.7

The precommit gate is implemented in `cmd_merge()` at lines 742-757 of `src/claudeutils/worktree/commands.py`:

```python
# Run precommit validation (mandatory correctness gate)
precommit_result = subprocess.run(
    ["just", "precommit"],
    capture_output=True,
    text=True,
    check=False,
)

if precommit_result.returncode != 0:
    click.echo("Precommit validation failed:", err=True)
    click.echo(precommit_result.stdout, err=True)
    click.echo(precommit_result.stderr, err=True)
    raise SystemExit(1)

# Output merge commit hash
click.echo(merge_commit)
```

**Behavior:**
- After merge commit is created (line 740), precommit runs (line 743)
- Precommit failure (non-zero exit) is reported to stderr (lines 750-753)
- On failure, merge exits 1 without rolling back commit
- On success, merge commit hash is output to stdout and exits 0
- This validates that the merge result passes all correctness checks

**Test Result:** PASS
- Merge succeeds with precommit passing
- Merge commit is created and persists
- Merge commit hash is returned to caller

## Regression Check

**Full test suite:** 773/774 passed, 1 xfail (known preprocessor bug)

**New test:** test_merge_phase_3_post_merge_precommit_gate — PASS

No regressions introduced. All existing merge tests continue to pass.

## Refactoring

**Lint results:** PASS (ruff formatting applied)

**Precommit results:** WARNINGS found (same as cycle 3.7, not introduced by this cycle)
- src/claudeutils/worktree/commands.py:
  - C901: cmd_merge complexity 24 > 10
  - PLR0912: Too many branches 31 > 12
  - PLR0915: Too many statements 105 > 50
  - File line limit: 757 lines (exceeds 400 limit)
- tests/test_worktree_merge.py:
  - File line limit: 719 lines (exceeds 400 limit)

**Note:** These warnings are from Phase 2-3 accumulated logic in cmd_merge function. Cycle 3.8 adds only one small test function (+68 lines in test file). The warnings require architectural refactoring (split cmd_merge into separate Phase 2 and Phase 3 functions). This was identified in cycle 3.7 as a required optimization.

## Files Modified

- tests/test_worktree_merge.py (added test_merge_phase_3_post_merge_precommit_gate)

No implementation changes (feature already complete from 3.7).

## Stop Condition

**Status:** QUALITY_CHECK_WARNINGS

Precommit validation found complexity and line limit warnings (same as cycle 3.7). These warnings are pre-existing from Phase 2-3 implementation and require architectural refactoring (split cmd_merge into Phase 2 and Phase 3 functions).

Per TDD protocol Step 4: When precommit warnings are found, escalate to refactor agent for design input.

## Decision Made

Confirmed precommit gate implementation is correct:
- Runs after merge commit created (not before)
- Reports failures to stderr
- Does NOT roll back merge commit
- Exits 1 on precommit failure, 0 on success
- Supports user fix flow: amend commit, re-run merge (idempotent)

---

**Test Status:** GREEN ✓
**Regression Check:** PASS ✓
**Lint:** PASS ✓
**Precommit:** WARNINGS (pre-existing, not from this cycle)
