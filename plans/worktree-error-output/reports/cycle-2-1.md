# Cycle 2.1 Report: Catch `derive_slug` ValueError in `new()`

**Status:** ✓ COMPLETE

## RED Phase
- Test file: `tests/test_worktree_new_creation.py`
- Test name: `test_new_invalid_task_name_clean_error`
- Expected: ValueError from `derive_slug("task_with_underscore")` → exit code 1 with traceback
- Verified: Test fails with exit code 1 (not 2), confirming unhandled exception

## GREEN Phase
- **File modified:** `src/claudeutils/worktree/cli.py`
- **Change:** Wrapped `slug = branch or derive_slug(task_name)` in try/except ValueError
- **Behavior:**
  - ValueError caught before propagation
  - Error message displayed via `_fail(str(e), code=2)`
  - Clean output: one-line error, no traceback
  - Exit code: 2 (validation failure)

## Verification
- Test `test_new_invalid_task_name_clean_error` passes ✓
- Full test suite: 1188/1189 passed (1 xfail expected) ✓
- No regression detected ✓

## Commit
- Hash: d15bf631
- Message: 🧪 Catch derive_slug ValueError in new() with clean exit code 2

## Dependencies
- ✓ Depends on Cycle 1.1 (`_fail()` helper): Already implemented in prior cycle

## Next Step
Ready for Phase 3: Drop `err=True` from all 12 sites in cli.py
