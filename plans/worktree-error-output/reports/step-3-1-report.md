# Step 3.1 Report: Convert error+exit sites to _fail()

## Objective
Replace all `click.echo(msg, err=True)` + `raise SystemExit(N)` pairs with `_fail(msg, N)` in `cli.py`.

## Changes Made

### File: `src/claudeutils/worktree/cli.py`

Converted 7 error+exit pairs to use `_fail()`:

1. **`new()` function (L198-200)**: Existing directory error
   - Changed: `click.echo(..., err=True)` + `raise SystemExit(1)` → `_fail(...)`

2. **`new()` function (L204-206)**: session.md not found error
   - Changed: `click.echo(..., err=True)` + `raise SystemExit(1)` → `_fail(...)`

3. **`_guard_branch_removal()` function (L254-260)**: Branch removal guard
   - Changed: Multi-line `click.echo(..., err=True)` + `raise SystemExit(2)` → Extract to `msg` variable, use `_fail(msg, 2)`

4. **`_delete_branch()` function (L268-270)**: Branch deletion failure
   - Changed: `click.echo(..., err=True)` + `raise SystemExit(1)` → `_fail(...)`

5. **`_check_confirm()` function (L275-280)**: Confirmation check
   - Changed: Multi-line `click.echo(..., err=True)` + `raise SystemExit(2)` → Extract to `msg` variable, use `_fail(msg, 2)`

6. **`_check_not_dirty()` function (L289-294)**: Uncommitted files in worktree
   - Changed: Multi-line `click.echo(..., err=True)` + `raise SystemExit(2)` → Extract to `msg` variable, use `_fail(msg, 2)`

7. **`_check_not_dirty()` function (L296-301)**: Uncommitted changes in submodule
   - Changed: Multi-line `click.echo(..., err=True)` + `raise SystemExit(2)` → Extract to `msg` variable, use `_fail(msg, 2)`

### File: `tests/test_worktree_rm_guard.py`

Updated test assertion in `test_delete_branch_exits_1_on_failure()`:
- Changed: `capsys.readouterr().err` → `capsys.readouterr().out`
- Reason: Error output migrated from stderr to stdout per D-8 design requirement

## Verification

### Remaining `err=True` sites (4):
All remaining sites are warnings without SystemExit, as expected:
- L83: Warning in `_initialize_environment()`
- L116: Warning in `_create_parent_worktree()`
- L311: Warning in `_update_session_and_amend()`
- L365: Warning in `rm()` (submodule deletion warning)

### Test Results
- All tests pass: 1188/1189 passed, 1 xfail (pre-existing)
- The xfail is unrelated (preprocessor bug in markdown handling)

## Commit
```
763b670d 🔀 Convert 7 error+exit pairs to _fail() in cli.py
```

## Status
✅ Step 3.1 complete. All error+exit pairs converted to use `_fail()` helper. Warning-only sites remain unchanged as per spec.
