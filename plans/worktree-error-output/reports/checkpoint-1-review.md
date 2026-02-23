# Review: Phase 1 Checkpoint — `_fail()` helper

**Scope**: `_fail()` implementation and 3 test cases for it
**Date**: 2026-02-23
**Mode**: review + fix

## Summary

`_fail()` is correctly implemented: stdout via `click.echo()` (no `err=True`), `Never` return type, configurable exit code. Tests cover the critical behavioral contract (stdout not stderr, exit codes). Two test functions capture `capsys` without using it, creating misleading fixture parameters. The `_fail()` docstring narrates the code rather than explaining non-obvious behavior.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Narration docstring on `_fail()`**
   - Location: `src/claudeutils/worktree/cli.py:39`
   - Note: `"""Print error message to stdout and exit with code."""` restates what the code does — eliminated per project conventions (docstrings only for non-obvious behavior, comments explain *why*)
   - **Status**: FIXED

2. **Unused `capsys` fixture in `test_fail_default_code`**
   - Location: `tests/test_worktree_utils.py:242`
   - Note: `capsys` is captured but never used. Implies intent to verify stdout that isn't verified. Either use it or drop it.
   - **Status**: FIXED

3. **Unused `capsys` fixture in `test_fail_custom_code`**
   - Location: `tests/test_worktree_utils.py:250`
   - Note: Same as above — `capsys` parameter misleads without asserting output.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/worktree/cli.py:39` — Removed narration docstring from `_fail()`
- `tests/test_worktree_utils.py:242` — Removed unused `capsys` parameter from `test_fail_default_code`
- `tests/test_worktree_utils.py:250` — Removed unused `capsys` parameter from `test_fail_custom_code`

## Design Anchoring

| Design requirement | Status | Evidence |
|---|---|---|
| `_fail()` outputs to stdout (not stderr) | Satisfied | `click.echo(msg)` — no `err=True`; verified by `test_fail_writes_to_stdout` asserting `captured.err == ""` |
| `_fail()` has `Never` return type | Satisfied | `cli.py:9` imports `Never`, `cli.py:38` annotates return type |
| `_fail()` configurable exit code, default 1 | Satisfied | `code: int = 1` parameter; `test_fail_default_code` and `test_fail_custom_code` verify |
| Consolidates `click.echo()` + `raise SystemExit(N)` | Satisfied | Implementation is correct; future phases will use it at call sites |

---

## Positive Observations

- `test_fail_writes_to_stdout` is the gold-standard test: verifies both the exit code AND that output goes to stdout with no stderr leakage — exactly the behavioral contract that matters for LLM-native conventions.
- `Never` return type is correct and complete — enables type checkers to understand `_fail()` terminates.
- `_fail()` raises `SystemExit` directly (not `sys.exit()`) which is the correct pattern for Click-based CLI tools.
