# Review: Phase 4 — Recall CLI Code

**Scope**: src/claudeutils/when/cli.py, tests/test_when_cli.py, agent-core/bin/when-resolve.py
**Date**: 2026-02-23T00:00:00
**Mode**: review + fix

## Summary

Phase 4 rewrites the `when` CLI command from two-arg syntax (`operator query...`) to one-arg syntax (`"when query"` / `"how query"`) and adds batched multi-query recall. The implementation is clean and correct. Three TDD cycles are complete, all 8 tests pass, and `just dev` is green. One misleading error message edge case and one inaccurate docstring warrant fixes.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Misleading error message for single-word operator-only input**
   - Location: src/claudeutils/when/cli.py:44-46
   - Note: When a user passes `"when"` as a query (operator word only, no body), `_parse_operator_query` returns `None` because `len(parts) < 2`. The error fires: `"Error: Query must start with a valid operator (how, when)."` — but the input does start with a valid operator. The body is missing, not the prefix. The message is wrong for this specific input shape.
   - **Status**: FIXED

2. **`when-resolve.py` docstring says "commands" (plural) for a single command**
   - Location: agent-core/bin/when-resolve.py:2
   - Note: `when_cmd` is one Click command handling both `when` and `how` operators via the query prefix. "the when/how CLI commands" implies two commands; the reality is one command with two recognized operator prefixes.
   - **Status**: FIXED

3. **`test_query_variadic_argument` first sub-test duplicates `test_single_arg_query_parsed`**
   - Location: tests/test_when_cli.py:73-80
   - Note: Both tests invoke `["when", "when writing mock tests"]` and assert resolve() is called with `operator="when"`, `query="writing mock tests"`. `test_single_arg_query_parsed` was introduced as the Cycle 4.1 RED test; `test_query_variadic_argument`'s first case covers identical ground. The test name and docstring for `test_query_variadic_argument` now describe "dot prefix preservation" as its primary purpose — the first sub-test no longer pulls its weight.
   - **Status**: FIXED

## Fixes Applied

- src/claudeutils/when/cli.py:44-46 — Changed error message to distinguish "no operator prefix" from "operator without query body" so both cases get accurate messages
- agent-core/bin/when-resolve.py:2 — Fixed docstring to say "when CLI command" (singular) matching the actual implementation
- tests/test_when_cli.py:70-80 — Removed redundant single-prefixed-query sub-test from `test_query_variadic_argument`; dot-prefix and double-dot-prefix sub-tests remain

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-12: One-arg syntax | Satisfied | cli.py:30-31 — `queries` variadic arg, operator parsed from each string |
| FR-12: Multiple queries batched with `\n---\n` | Satisfied | cli.py:59 — `"\n---\n".join(results)` |
| FR-12: Invalid prefix rejected with error mentioning "when" or "how" | Satisfied | cli.py:44-48 — error message includes operator list, exits non-zero |
| FR-12: Existing 5 tests migrated to new invocation syntax | Satisfied | all 5 prior tests updated in diff; same behavioral contract |

---

## Positive Observations

- `_parse_operator_query` is a clean single-responsibility function: splits on first space, validates, returns typed tuple or None. Correct to extract rather than inline into `when_cmd`.
- Case-insensitive operator normalisation (`.lower()` at parse time and at return) means the resolved operator is always lowercase regardless of input casing — correct for passing to `resolve()`.
- `sys.exit(1)` on error inside the query loop short-circuits immediately on first bad query rather than accumulating errors. Appropriate for CLI contract.
- Single-query backward compatibility: `"\n---\n".join([result])` produces no separator — no special-case code needed.
- `test_batched_recall_multiple_queries` independently verifies both the separator presence (multi-query) and separator absence (single-query) cases.
- `test_invalid_prefix_rejected` correctly verifies resolve() is never called on invalid prefix — not just exit code.
- `when-resolve.py` docstring example shows the new one-arg syntax with quoting (`"when <query>"`), which correctly conveys shell quoting requirement.
