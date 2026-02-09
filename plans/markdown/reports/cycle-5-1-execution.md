# Cycle 5.1: Add parametrized idempotency test

**Timestamp:** 2026-02-09 23:45:00 UTC

## Execution Summary

- **Status:** STOP_CONDITION
- **Test command:** `pytest tests/test_markdown_fixtures.py::test_preprocessor_idempotency -v`
- **RED result:** FAIL as expected (test discovers real idempotency bugs)
- **GREEN result:** N/A (stopped at stop condition)
- **Regression check:** 444/445 tests pass (new test fails as expected for RED)
- **Refactoring:** none (WIP commit created as checkpoint)
- **Files modified:**
  - `tests/test_markdown_fixtures.py` - Added `test_preprocessor_idempotency` function (lines 158-173)
  - `plans/markdown/reports/cycle-5-1-idempotency-findings.md` - Detailed findings report
- **Stop condition:** Idempotency failures detected in 02-inline-backticks fixture
- **Decision made:** Escalate architectural fix to orchestrator; test is permanent and valuable

## Cycle Details

### RED Phase

**Test created:** `test_preprocessor_idempotency`
- **Location:** `tests/test_markdown_fixtures.py` lines 158-173
- **Pattern:** Parametrized over all 16 markdown fixtures (same discovery as existing fixture test)
- **Behavior:** For each fixture, loads expected output, re-processes it, asserts unchanged
- **Code:**
  ```python
  @pytest.mark.parametrize("fixture_name", _FIXTURE_NAMES)
  def test_preprocessor_idempotency(fixture_name: str) -> None:
      input_lines, expected_lines = load_fixture_pair(fixture_name)
      reprocessed_lines = process_lines(expected_lines)
      assert reprocessed_lines == expected_lines
  ```

**Failure verification:**
- Test fails on `test_preprocessor_idempotency[02-inline-backticks]`
- Root cause: `fix_backtick_spaces()` function has idempotency bug
- Pattern: Escaped triple backticks get re-quoted on second pass
  - Original: `` ``` `` using `` double `` ``` ``
  - After re-process: `` ``` `` using `` double `` `` ``` `` `` (extra spaces)

**Stop condition triggered:** "Idempotency fails for any fixture (output changes on re-run)"

### GREEN Phase - BLOCKED

Cannot proceed to GREEN phase because idempotency failures in the preprocessor pipeline are a correctness issue, not a test implementation issue. Making the test pass would require fixing the underlying preprocessor bugs, which is beyond scope of the test addition itself.

### REFACTOR Phase - SKIPPED

WIP commit created:
```
acb9b6d WIP: Cycle 5.1 - Add parametrized idempotency test
```

No lint/precommit validation performed per REFACTOR protocol (GREEN phase not reached).

## Impact Assessment

**Test Value:** CRITICAL
- Successfully detects real idempotency bugs in the preprocessor
- Validates FR-4 requirement: "Preprocessor-only idempotency"
- Parametrized approach ensures all fixtures are checked
- Will catch regressions once bugs are fixed

**Findings:** One fixture (02-inline-backticks) exhibits non-idempotent behavior

The test is **correct and permanent**. It revealed actual bugs that must be fixed separately.

## Escalation

This cycle hit a stop condition that requires architectural review:

1. **Stop condition:** Idempotency failures in 02-inline-backticks
2. **Root cause:** `fix_backtick_spaces()` function in `markdown_list_fixes.py`
3. **Issue:** Regex pattern and skip logic cause divergent behavior on re-processing
4. **Scope:** Affects backtick escaping pipeline (multiple functions involved)

**Action needed:** Orchestrator should route to architecture review for fixing the idempotency bugs.

**Test artifact status:** Ready for deployment; will validate fixes once architecture review completes.

## Phase 5 Status

- **Cycle 5.1 complete:** Test added ✓, idempotency bugs identified ✓, escalated ✓
- **Cycle 5.2 pending:** Dependency on architecture fix for idempotency
- **Cycle 5.3 pending:** Integration tests (also blocked by idempotency fix)
- **Next:** Wait for architecture review completion before proceeding to 5.2
