# Cycle 3.2: Fetch plan usage from OAuth API with cache

**Timestamp**: 2026-02-04

## Execution Summary

- **Status**: GREEN_VERIFIED
- **Test command**: `just test tests/test_statusline_plan_usage.py::test_get_plan_usage -xvs`
- **RED result**: FAIL as expected (ModuleNotFoundError: No module named 'claudeutils.statusline.plan_usage')
- **GREEN result**: PASS (test passes with implementation)
- **Regression check**: 18/18 tests passed (all statusline tests pass)
- **Refactoring**: Format with `just lint` and `just precommit` — both passed
- **Files modified**:
  - `src/claudeutils/statusline/plan_usage.py` (created)
  - `src/claudeutils/statusline/models.py` (added PlanUsageData model)
  - `tests/test_statusline_plan_usage.py` (added test_get_plan_usage test)
- **Stop condition**: None
- **Decision made**: Used typing.cast() for proper type hints with dict.get() return values

## Detailed Execution

### RED Phase Verification

Created test that imports `get_plan_usage` from the non-existent `plan_usage` module. Test failed as expected with:
```
ModuleNotFoundError: No module named 'claudeutils.statusline.plan_usage'
```

### GREEN Phase Verification

1. **Added PlanUsageData model** to `src/claudeutils/statusline/models.py`:
   - `hour5_pct: float` — 5-hour usage percentage
   - `hour5_reset: str` — 5-hour reset time (HH:MM format)
   - `day7_pct: float` — 7-day usage percentage

2. **Created plan_usage.py** with `get_plan_usage()` function:
   - Calls `UsageCache()` to fetch OAuth API usage data
   - Parses 5h/7d percentages and reset times
   - Returns `PlanUsageData | None`
   - Catches exceptions gracefully (KeyError, TypeError, ValueError)

3. **Test verification**:
   - `test_get_plan_usage` passes successfully
   - Mocks `UsageCache.get()` to return mock usage dictionary
   - Asserts all three PlanUsageData fields are correctly extracted

### Regression Testing

All 18 statusline tests pass:
- test_statusline_context.py (7 tests)
- test_statusline_display.py (4 tests)
- test_statusline_models.py (3 tests)
- test_statusline_plan_usage.py (2 tests: TTL + get_plan_usage)
- test_statusline_structure.py (1 test)

No regressions introduced.

### Lint & Precommit

- `just lint` passed after fixing:
  - Type hints for dict.get() values using typing.cast()
  - Docstring formatting
  - Exception specificity (changed generic Exception to KeyError, TypeError, ValueError)

- `just precommit` passed validation

## Implementation Notes

**Type Hints Challenge**: dict.get() returns `object` type, causing mypy errors. Resolved by:
1. Declaring `percent_5h: Any = usage_data.get(...)`
2. Using `float(cast("float", percent_5h))` in return statement
3. This satisfies mypy's strict typing while maintaining runtime correctness

**Error Handling**: The function gracefully returns `None` on any parsing error, supporting the fail-safe pattern (D8).

## Success Criteria

- ✅ RED phase: Test failed with expected ModuleNotFoundError
- ✅ GREEN phase: Test passes with implementation
- ✅ No regressions: All 18 statusline tests pass
- ✅ Lint/precommit: Both validation passes
- ✅ Proper type hints and error handling
