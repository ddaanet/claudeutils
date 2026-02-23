# Review: Phase 3 Checkpoint (Final) — `err=True` removal

**Scope**: `src/claudeutils/worktree/cli.py`, `tests/test_worktree_rm_guard.py`
**Date**: 2026-02-23T15:54:28Z
**Mode**: review + fix

## Summary

Phase 3 completed the `err=True` removal migration. All 12 original `err=True` sites (8 error+exit, 4 warning-only) have been eliminated. `_fail()` is defined and used consistently at 8 of those error+exit sites. Two pre-existing echo+exit patterns in `clean_tree` and `merge` that were never `err=True` sites remain as bare `click.echo()` + `raise SystemExit(1)` — minor inconsistency with the `_fail()` convention.

`just dev` passes. 1188/1189 tests pass (1 xfail is pre-existing, unrelated).

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`clean_tree` and `merge` use bare echo+raise instead of `_fail()`**
   - Location: `cli.py:169-171` (`clean_tree`), `cli.py:230-231` (`merge`)
   - Note: Both sites already output to stdout (no `err=True`) — D-1 is satisfied. However they use the pre-`_fail()` pattern (explicit `click.echo()` + `raise SystemExit(1)`) instead of the now-established helper. Inconsistency with the 8 sites converted in step 3.1.
   - **Status**: FIXED

## Fixes Applied

- `cli.py:169-171` — Replaced `click.echo("\n".join(dirty))` + `raise SystemExit(1)` with `_fail("\n".join(dirty))`
- `cli.py:230-231` — Replaced `click.echo(f"git error: ...")` + `raise SystemExit(1) from None` with `_fail(f"git error: ...")`

## Design Anchoring

Verified against `plans/worktree-error-output/outline.md` and design requirements:

- **D-1 / Key Decision 1 (all output to stdout)**: `grep "err=True" cli.py` returns empty — satisfied.
- **Key Decision 3 (`_fail()` helper)**: All echo+exit pairs now use `_fail()`. Satisfied post-fix.
- **Key Decision 4 (warnings stay as plain `click.echo()`)**: 4 warning-only sites use `click.echo()` without exit — satisfied.
- **Temp file lifecycle**: `new()` `finally` block cleans up `temp_session_file` on all exit paths including `_fail()` calls. The `_fail()` at line 192 fires before temp file creation (correct). The `_fail()` at line 199 fires after temp file creation — `finally` cleans it up correctly.

## Lifecycle Audit (D-7)

**Stateful objects:**

- **Temp session file** (`new()` lines 193–208): `NamedTemporaryFile(delete=False)` with `finally` cleanup. All paths — success, `_fail()`, and unhandled exceptions — reach the `finally` block. No leak.
- **Worktree directory** (`_setup_worktree_safe`): Exception-safe via try/catch that calls `shutil.rmtree(path)` on failure. Pre-existing `session.md not found` error at line 204 leaves a partial worktree if setup succeeded — pre-existing issue, out of scope for this migration.
- **MERGE_HEAD** (`merge` command): Managed by `merge.py`, which is OUT-OF-SCOPE (already stdout, not modified). Not audited here.

**SystemExit calls — no path exits 0 with error state active:**

| Site | Exit code | Pre-exit state | Assessment |
|------|-----------|----------------|------------|
| `_fail()` (line 40) | 1 or 2 | varies by caller | All error sites — correct |
| `clean_tree` (line 171, post-fix) | 1 via `_fail` | dirty lines printed | Correct — signals failure |
| `merge` (line 231, post-fix) | 1 via `_fail` | git error printed | Correct — signals failure |

No path exits 0 with an error state active.

## Test Quality

`tests/test_worktree_rm_guard.py`:

- All 11 tests assert on `result.output` (stdout) — consistent with the stdout migration.
- `test_delete_branch_exits_1_on_failure` asserts `"deletion failed" in capsys.readouterr().out` — correctly updated in step 3.1 from `.err` to `.out`.
- Assertions are behavioral: exit codes, output substrings, filesystem state checks.
- `test_rm_no_destructive_suggestions` validates FR-5 (no destructive suggestions in output).
- `test_rm_guard_prevents_destruction` verifies all downstream operations are skipped on guard refusal — regression coverage.

## Implementation Quality

- `_fail()` signature (`msg: str, code: int = 1`) and return type (`Never`) are correct.
- `derive_slug` ValueError catch is tightly scoped to the `if task_name:` block.
- All 12 `err=True` sites removed; 8 error+exit converted to `_fail()`; 4 warning-only now plain `click.echo()`.

## Positive Observations

- `_fail() -> Never` prevents control-flow confusion at all call sites — no dead code after calls.
- `finally` block in `new()` is robust against all failure modes including the new `_fail()` calls.
- Step 3.1 correctly identified and updated `capsys.readouterr().err` → `.out` in the test file.
- Sequential migration phases (TDD for new behavior, mechanical for existing) kept each phase's scope clean.
