# Review: handoff-cli-tool RC10 fixes

**Scope**: Uncommitted changes since `2efa60ddc49fd480ef06adc587f45b0cc4832524`
**Date**: 2026-03-25
**Mode**: review + fix

## Summary

Changes implement fixes for the two major and thirteen minor findings from the RC10 deliverable review. M-1 (`load_state()` backward compat) and M-2 (handoff CLI missing error handling) are both addressed with correct, minimal fixes. Minor fixes cover backreference safety in `overwrite_status`, test specificity improvements, a new submodule regression test, and integration test plan directory infrastructure.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **New submodule test lacks `match=` on `pytest.raises`**
   - Location: `tests/test_session_commit_pipeline.py:205`
   - Note: `test_submodule_clean_error_shows_full_path` uses bare `pytest.raises(CleanFileError)` without `match=`. RC10 m-7 explicitly targets this pattern. The test has manual assertions afterward on `err.clean_files`, but consistency with the codebase pattern requires `match=`.
   - **Status**: FIXED

2. **RC10 m-12 un-parenthesized except clauses not addressed**
   - Location: `src/claudeutils/worktree/cli.py:104, 176`
   - Note: `except FileNotFoundError, subprocess.CalledProcessError:` and `except subprocess.CalledProcessError, OSError:` — parentheses removed during S-2 extraction refactoring. These were raised in RC10 m-12. The changeset under review only addressed m-13 (dead `return None`) via `noqa: RET503`, not m-12. The un-parenthesized except clauses are pre-existing in this diff scope and not introduced by the current changes.
   - **Status**: DEFERRED — RC10 m-12 not addressed in this fix cycle. Pre-existing issue requiring follow-up.

## Fixes Applied

- `tests/test_session_commit_pipeline.py:205` — Added `match="no uncommitted changes"` to bare `pytest.raises(CleanFileError)` in new submodule test

## Requirements Validation

| RC10 Finding | Status | Evidence |
|---|---|---|
| M-1: `load_state()` crashes on pre-m-7 state files | Satisfied | `pipeline.py:45-47`: filter to `__dataclass_fields__` before unpack |
| M-2: Handoff CLI missing session.md error handling | Satisfied | `cli.py:54-58`: try/except `(OSError, ValueError)` → `_fail(code=2)` |
| m-1: Submodule CleanFileError paths lack repo context | Satisfied | `test_session_commit_pipeline.py:200-212`: regression test verifies path includes submodule prefix |
| m-2: `overwrite_status` backreference injection | Satisfied | `pipeline.py:77-80`: function callback replaces string replacement template |
| m-3: `_build_repo_section` heading/content gap | Satisfied | `git_cli.py:32`: `header + "\n" + "\n\n".join(parts)` |
| m-6: `len(data.completed) > 0` redundancy | Satisfied | `test_session_parser.py`: pattern removed (not in this diff — pre-existing fix from prior cycle) |
| m-7: Bare `pytest.raises(CleanFileError)` (test_session_commit.py:217) | Satisfied | `test_session_commit.py:217`: `match=` added |
| m-8: Bare `pytest.raises(CalledProcessError)` (test_worktree_merge_errors.py:83) | Satisfied | `test_worktree_merge_errors.py:83-84`: `match=` added |
| m-10: Disjunctive assertion weakens specificity | Satisfied | `test_session_status.py:263`: specific `"In-tree:"` assertion |
| m-11: Integration test missing plan directory | Satisfied | `test_session_integration.py:37-39`: `plans/widget/` created in fixture |
| m-12: Un-parenthesized except clauses | DEFERRED | Not addressed in this changeset |
| m-13: Dead `return None` after `_fail` | Satisfied | `worktree/cli.py`: dead return removed, `noqa: RET503` added |

## Deferred Items

- **RC10 m-12: Un-parenthesized except clauses** (`worktree/cli.py:104, 176`) — Not introduced by this changeset; not addressed in this fix cycle. Parenthesized form is canonical Python. Requires a follow-up edit.

---

## Positive Observations

- `load_state()` field filtering uses `HandoffState.__dataclass_fields__` — correct introspection, stays correct if fields are added or removed without requiring updates.
- `replacement_func` callback is the canonical fix for backreference injection; uses `m.group()` calls to avoid the template evaluation entirely.
- `test_overwrite_status_backreference_in_text` exercises both `\g<1>` and `\g<3>` patterns — tests the actual failure mode, not just one variant.
- `test_load_state_ignores_unknown_fields` writes raw JSON with the removed field and asserts `not hasattr(result, "step_reached")` — tests the right invariant directly.
- Integration test plan directory addition (m-11 fix) means plan state rendering is now exercised in the integration path.
- `test_handoff_missing_session_file` verifies `"Traceback" not in result.output`, explicitly confirming the S-3 conformance property that motivated the M-2 fix.
