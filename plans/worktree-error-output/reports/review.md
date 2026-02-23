# Review: worktree-error-output — final quality review

**Scope**: Complete implementation of `_fail()` helper, `derive_slug` ValueError catch in `new()`, and `err=True` removal across `cli.py`
**Date**: 2026-02-23
**Mode**: review + fix

## Summary

The implementation satisfies all design requirements: `_fail()` is defined with correct `Never` return type, `err=True` is absent from the entire file, the `ValueError` from `derive_slug` is caught cleanly in `new()`, and all 11 `_fail()` call sites use the helper consistently. Tests cover all three new behavioral paths. `just dev` passes clean.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_fail()` call in `new()` uses keyword argument inconsistently**
   - Location: `src/claudeutils/worktree/cli.py:191`
   - Note: `_fail(str(e), code=2)` uses `code=` as keyword while all other call sites use positional: `_fail(msg, 2)`. Not wrong, but inconsistent with the established pattern across 5 other `_fail(msg, N)` calls.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/cli.py:191` — Changed `_fail(str(e), code=2)` to `_fail(str(e), 2)` to match positional style used at all other call sites.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| All `_worktree` error output to stdout | Satisfied | No `err=True` in cli.py (grep confirms zero matches) |
| `_fail(msg, code=1) -> Never` consolidates echo+exit | Satisfied | cli.py:38-40, `from typing import Never` imported |
| `derive_slug` ValueError caught in `new()`, clean exit 2 | Satisfied | cli.py:187-191, test at test_worktree_new_creation.py:326 |
| 4 warning sites: drop `err=True`, keep plain `click.echo()` | Satisfied | Lines 83, 116, 309, 363 are plain `click.echo()` |
| All error+exit pairs use `_fail()` | Satisfied | 10 `_fail()` call sites cover all previous echo+exit patterns |

---

## Positive Observations

- `_fail()` placement (before `derive_slug`, after imports) follows the runbook spec and keeps module organization clean.
- `Never` return type is correct — allows callers to omit `return` after `_fail()` calls without type errors.
- `test_fail_writes_to_stdout` explicitly checks `captured.err == ""` — the core design invariant (no stderr) is directly tested.
- `test_new_invalid_task_name_clean_error` checks for absence of `"Traceback"` and `"ValueError"` strings — catches regressions if the except is ever removed.
- The `merge` command's `_fail` usage (line 229) correctly handles the CalledProcessError case without introducing a bare `raise SystemExit`.

## Recommendations

None. Implementation is complete and conforms to the design.
