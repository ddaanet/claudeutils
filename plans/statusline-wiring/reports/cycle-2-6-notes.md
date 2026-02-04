# Cycle 2.6: Calculate context tokens from current_usage

**Timestamp:** 2026-02-04 (execution)

## Execution Summary

| Item | Result |
|------|--------|
| Status | GREEN_VERIFIED |
| Test command | `just test tests/test_statusline_context.py::test_calculate_context_tokens_from_current_usage -xvs` |
| RED result | FAIL as expected (ImportError during collection) |
| GREEN result | PASS |
| Regression check | 14/14 passed (all statusline tests) |
| Refactoring | none |
| Files modified | tests/test_statusline_context.py, src/claudeutils/statusline/context.py |
| Stop condition | none |
| Decision made | none |

## Details

### RED Phase
- Created test: `test_calculate_context_tokens_from_current_usage` in tests/test_statusline_context.py
- Expected failure: ImportError - function doesn't exist yet
- Actual failure: ImportError during collection (function not importable)
- Status: VERIFIED - test fails as expected

### GREEN Phase
- Implemented: `calculate_context_tokens(input_data: StatuslineInput) -> int`
- Logic: Sums 4 token fields from current_usage when present, returns 0 if None
- File: src/claudeutils/statusline/context.py
- Test result: PASS (test_calculate_context_tokens_from_current_usage)
- Status: VERIFIED

### Regression Check
- Command: `just test tests/test_statusline_*.py`
- Result: 14/14 tests passed (includes 5 existing tests + 9 new tests from earlier cycles + this new test)
- Status: VERIFIED - no regressions

### Refactoring
- Lint: PASS (just lint)
- Precommit: PASS (just precommit) - no warnings
- Status: None needed - code is clean

## Code Changes

### tests/test_statusline_context.py
- Added import for `calculate_context_tokens`
- Added imports for all required model types
- Added test function with setup of StatuslineInput, ContextUsage, and ContextWindowInfo objects
- Test validates that function returns sum of 4 token fields (200 from 100+50+25+25)

### src/claudeutils/statusline/context.py
- Added import of StatuslineInput model
- Added `calculate_context_tokens()` function with:
  - Type hints for input and output
  - Docstring with purpose and behavior
  - Guard against None current_usage (returns 0)
  - Sum of 4 token fields: input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens
