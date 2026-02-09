# Cycle 1.2: Implement fixture loading helper

**Timestamp:** 2026-02-09 01:20 UTC
**Status:** GREEN_VERIFIED

## Test Command

```bash
pytest tests/test_markdown_fixtures.py::test_load_fixture_pair -v
```

## Phase Results

### RED Phase

**Expected Failure:** AttributeError or NameError (helper function doesn't exist)

**Actual Result:** REGRESSION — Test passed on first run

The test passed immediately because the implementation was provided in this cycle. This is marked as `[REGRESSION]` in the cycle definition, indicating expected behavior when both test and implementation are written together.

The test validates:
- Function returns tuple of (input_lines, expected_lines)
- Lines preserve newlines (compatible with process_lines() API)
- FileNotFoundError raised when fixture files missing
- Proper type annotations: `tuple[list[str], list[str]]`

### GREEN Phase

**Expected Outcome:** Test passes after implementation

**Actual Result:** PASS

Test passed with implementation of `load_fixture_pair()`:

```python
def load_fixture_pair(
    name: str, fixtures_dir: Path | None = None
) -> tuple[list[str], list[str]]:
    """Load a fixture pair from .input.md and .expected.md files."""
    if fixtures_dir is None:
        fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"

    input_file = fixtures_dir / f"{name}.input.md"
    expected_file = fixtures_dir / f"{name}.expected.md"

    if not input_file.exists():
        raise FileNotFoundError(f"Input fixture not found: {input_file}")
    if not expected_file.exists():
        raise FileNotFoundError(f"Expected fixture not found: {expected_file}")

    input_lines = input_file.read_text().splitlines(keepends=True)
    expected_lines = expected_file.read_text().splitlines(keepends=True)

    return input_lines, expected_lines
```

Also added two error condition tests:
- `test_load_fixture_pair_missing_input` — Verifies FileNotFoundError for missing input
- `test_load_fixture_pair_missing_expected` — Verifies FileNotFoundError for missing expected

All three tests pass.

### Regression Check

**Result:** 413/413 tests passed

All existing tests pass. No regressions introduced. Cycle 1.1 fixture directory test still passes.

## Refactoring

### Formatting

- `just lint` reformatted imports (moved `pytest` import after `pathlib`)
- All style issues resolved

### Precommit Validation

- `just precommit` passed with no warnings
- No complexity or quality issues detected

## Files Modified

- `tests/test_markdown_fixtures.py` — Added `load_fixture_pair()` function and three tests

## Stop Condition

None. Cycle completed successfully.

## Decision Made

- **Line preservation:** Used `.splitlines(keepends=True)` to preserve newlines, matching `process_lines()` API expectations
- **Default fixtures_dir:** Made optional parameter with intelligent default to `tests/fixtures/markdown/`
- **Error messages:** Clear FileNotFoundError messages indicating which fixture file is missing
- **Type annotations:** Full type annotations with Python 3.9+ union syntax (`Path | None`)
- **Test approach:** Created temporary fixture files in test, cleaned up in finally block for proper isolation

## Summary

Fixture loading helper successfully implemented. Function provides:
- Type-safe fixture pair loading
- Newline preservation for API compatibility
- Clear error handling for missing files
- Sensible defaults for fixture directory

Ready for using this helper in subsequent cycles to load test fixtures for markdown processing tests.
