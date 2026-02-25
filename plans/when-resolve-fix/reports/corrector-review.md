# Review: when-resolve module bug fixes

**Scope**: resolver.py, cli.py, test_when_resolver.py, test_when_cli.py, test_when_resolver_errors.py, test_when_resolver_hyphenated.py
**Date**: 2026-02-25T00:00:00
**Mode**: review + fix

## Summary

Four bugs fixed: double-to prefix, cross-operator matching, fail-fast batch, and mandatory operator. The implementation is clean and correct. Removing the `operator` parameter from `resolve()` is the right architectural move — the operator was providing false selection power given that collisions are caught at index-write time by precommit validation. All 28 tests pass and changed files lint clean.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_strip_operator` docstring narrates Examples/Returns rather than stating non-obvious contract**
   - Location: `src/claudeutils/when/cli.py:14-22`
   - Note: The old docstring listed `Accepts:` / `Returns:` examples that restated what the code said. Function name and 3-line body are self-documenting. The non-obvious fact is that "when/how" prefix recognition is case-insensitive but the returned remainder is verbatim.
   - **Status**: FIXED

2. **`removeprefix("to ")` case assumption undocumented**
   - Location: `src/claudeutils/when/resolver.py:192-193`
   - Note: `removeprefix("to ")` only strips lowercase `"to "`. Safe in practice because callers always pass lowercase (memory-index entries use `/how`, cli.py strips the operator and returns the remainder as-is, and callers use lowercase invocations), but the assumption was implicit.
   - **Status**: FIXED

3. **`test_how_to_prefix_not_doubled` comment misattributed the transformation chain**
   - Location: `tests/test_when_resolver.py:255-256`
   - Note: Comment said "cli.py splits to operator=`'how'`, query=`'to X'`" but the test calls `resolve()` directly — it's testing the resolver's `removeprefix` behavior, not the CLI split. Comment was accurate about what happens but described it at the wrong layer.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/when/cli.py:14-16` — Replaced narrating `Accepts:`/`Returns:` docstring with single-sentence doc stating the non-obvious (case-insensitive operator check, verbatim remainder).
- `src/claudeutils/when/resolver.py:192-195` — Extended comment to document the lowercase-only guarantee and why it's safe.
- `tests/test_when_resolver.py:255-256` — Corrected comment to describe what the test actually exercises (resolver `removeprefix`, not CLI split).

## Requirements Validation

Validating against the 4 stated bugs:

| Bug | Status | Evidence |
|-----|--------|----------|
| Bug 1: Double-to prefix | Satisfied | `resolver.py:196` strips `"to "` prefix; `test_how_to_prefix_not_doubled` covers |
| Bug 2: Cross-operator matching | Satisfied | Candidates are bare triggers, no operator prefix in matching path; `test_cross_operator_matching` covers |
| Bug 3: Fail-fast batch | Satisfied | `cli.py:38-59` accumulates errors, prints successes first, exits 1 only on error; `test_batch_accumulates_errors` + `test_batch_all_succeed_exit_zero` cover |
| Bug 4: Operator optional | Satisfied | `_strip_operator` passes bare triggers to resolver; `test_bare_query_accepted` + `test_bare_trigger_no_operator` cover |

---

## Positive Observations

- **Simplification is correct**: Removing `operator` from `resolve()` eliminates false selection power. Collision detection belongs at index-write time (precommit validator), not query time.
- **Error accumulation** (`results`/`errors` lists, successes-first, stdout not stderr) correctly follows LLM-native output decision (`agents/decisions/cli.md`).
- **`_load_matched_entry` simplified cleanly**: Old version reconstructed operator from candidate string. New version matches on bare trigger directly — right approach.
- **`_handle_no_match` correctly shows actual operator**: `trigger_to_op` dict preserves index-declared operators, so suggestions show `/how X` for how-entries.
- **Test rename in `test_when_resolver_errors.py`**: `test_operator_parameter_disambiguates` → `test_duplicate_trigger_returns_first_match` accurately reflects new semantics and documents the collision assumption.
- **Test prose quality**: New tests have minimal docstrings stating behavior. Narrating docstrings removed.
- **All 28 tests pass; changed files lint clean.**
