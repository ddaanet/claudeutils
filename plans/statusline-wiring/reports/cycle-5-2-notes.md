# Cycle 5.2: Call context.py functions in CLI orchestration

**Timestamp**: 2026-02-04

## Execution Summary

- **Status**: GREEN_VERIFIED
- **Test command**: `pytest tests/test_statusline_cli.py::test_statusline_calls_context_functions -xvs`
- **RED result**: FAIL as expected (AttributeError: module has no attribute 'get_git_status')
- **GREEN result**: PASS
- **Regression check**: 25/25 passed (all statusline tests pass)
- **Refactoring**: Formatting only (linting applied via `just lint`)
- **Files modified**:
  - `src/claudeutils/statusline/cli.py`
  - `tests/test_statusline_cli.py`
- **Stop condition**: None
- **Decision made**: Used context manager syntax for patch grouping (applied by formatter)

## Details

### RED Phase
Created test `test_statusline_calls_context_functions()` that mocks the three context functions and verifies they are called when statusline() executes. Test failed as expected with `AttributeError` because functions were not yet imported in cli.py.

### GREEN Phase
Added imports and function calls to `src/claudeutils/statusline/cli.py`:
- Imported `get_git_status()`, `get_thinking_state()`, `calculate_context_tokens()` from context module
- Called all three functions in statusline() after parsing input
- Stored results in local variables (no output yet, per spec)

### Regression Check
Ran full statusline test suite (`tests/test_statusline_*.py`): All 25 tests pass, including:
- Existing `test_statusline_parses_json()` still passes
- New `test_statusline_calls_context_functions()` passes
- All context, api_usage, models, plan_usage, display, and structure tests pass

### Refactoring
Ran `just lint` which applied formatting:
- Reformatted test file with context manager syntax (multiple patch statements grouped)
- Reformatted cli.py with context manager syntax
- No lint errors

Ran `just precommit`: Passed validation.

### Implementation Notes
- Test uses mocking to verify function calls without executing git/file operations
- Minimal implementation stores function results in local variables as specified
- No changes to output behavior (still outputs "OK")
- Context functions already fully implemented in cycle 4, ready to wire
