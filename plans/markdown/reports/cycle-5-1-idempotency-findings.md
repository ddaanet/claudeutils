# Cycle 5.1: Parametrized Idempotency Test - Findings Report

**Cycle:** 5.1: Add parametrized idempotency test
**Status:** STOP_CONDITION - Idempotency failures detected
**Timestamp:** 2026-02-09

## Summary

The parametrized idempotency test was successfully added and RED phase verified. However, test execution revealed real idempotency bugs in the markdown preprocessor:

- **Test created:** `test_preprocessor_idempotency` (16 parametrized instances)
- **RED verified:** Test fails as expected - not all fixtures are idempotent
- **Failure location:** Fixture `02-inline-backticks` (but likely others)
- **Root cause:** The `fix_backtick_spaces()` function has idempotency issues with escaped backtick sequences

## Test Details

**Test file:** `tests/test_markdown_fixtures.py`
**Test added:** Lines 158-173
**Parametrization:** All 16 markdown fixtures (same discovery as existing fixture test)

```python
@pytest.mark.parametrize("fixture_name", _FIXTURE_NAMES)
def test_preprocessor_idempotency(fixture_name: str) -> None:
    """Test idempotency: re-processing output produces identical result."""
    input_lines, expected_lines = load_fixture_pair(fixture_name)
    reprocessed_lines = process_lines(expected_lines)
    assert reprocessed_lines == expected_lines
```

## Failure Analysis

### Failed Fixture: 02-inline-backticks

**Behavior:**
- First processing: Input → Expected output (16 instances pass)
- Re-processing: Expected → Different output (test fails)

**Example difference (line with escaped backticks):**

Original expected:
```markdown
- Quote double backticks: `` ``` `` using `` double `` ``` ``
```

After re-processing:
```markdown
- Quote double backticks: `` ``` `` using `` double `` `` ``` `` ``
```

The trailing ``` gets wrapped with additional backticks: ``` → `` ``` ``

**Root cause:** Function `fix_backtick_spaces()` in `markdown_list_fixes.py` (lines 282-313)

The regex pattern `r"`([^`]*)`"` on line 311 matches single backtick pairs but has a logic flaw:

1. Line 298 skips processing if it contains `"`` "` or `" ``"` (escaped sequences with spaces)
2. However, lines with escaped triple backticks like ```` ``` ```` don't always match this pattern
3. Re-processing applies the regex again, treating backtick runs differently on second pass
4. This causes divergence in how spaces around backticks are quoted

## Impact

**FR-4 Status:** "Preprocessor-only idempotency" requirement **NOT MET**

The preprocessor is **not idempotent** for at least the `02-inline-backticks` fixture. This is a correctness issue that must be resolved before this feature can be complete.

## Stop Condition

**Triggered:** "Idempotency fails for any fixture (output changes on re-run)"

Per cycle spec, this is a STOP condition:
```
STOP IMMEDIATELY if:
- Idempotency fails for any fixture (output changes on re-run)
```

**Decision:** Stop execution and escalate to architecture review.

The test itself is correct and valuable - it successfully detects real bugs. However, fixing those bugs requires architectural analysis of the backtick handling pipeline.

## Next Steps

This stop condition should be escalated to the orchestrator with:

1. **Test artifact:** `test_preprocessor_idempotency` correctly identifies idempotency bugs
2. **Evidence:** 02-inline-backticks fixture demonstrates failure pattern
3. **Root cause:** `fix_backtick_spaces()` logic in preprocessing pipeline
4. **Scope:** Requires review of entire backtick escaping and spacing logic

The test is a **permanent addition** that will catch regressions once the idempotency bugs are fixed.

## Files Modified

- `tests/test_markdown_fixtures.py` - Added `test_preprocessor_idempotency` function (16 parametrized instances)

## Test Results

```
FAILED tests/test_markdown_fixtures.py::test_preprocessor_idempotency[02-inline-backticks]

AssertionError: Fixture 02-inline-backticks is not idempotent:
  Original output: [... 84 lines ...]
  After re-process: [... 84 lines with modifications ...]
  At index 25 diff: Expected ``` `` but got `` ``` ``
```

All other 444 tests pass. Only idempotency test failed (expected for RED phase).
