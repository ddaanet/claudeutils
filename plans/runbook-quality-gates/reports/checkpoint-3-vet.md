# Vet Review: Phase 3 Checkpoint — test-counts subcommand

**Scope**: Phase 3 implementation (Cycles 3.1–3.3): `check_test_counts`, `cmd_test_counts`, fixture extraction to `tests/fixtures/validate_runbook_fixtures.py`
**Date**: 2026-02-17T23:26:34Z
**Mode**: review + fix

## Summary

Phase 3 delivers the `test-counts` subcommand with three TDD cycles: happy path (Cycle 3.1), count mismatch detection with test name listing (Cycle 3.2), and parametrized test name normalization (Cycle 3.3). The stop condition from Cycle 3.2 (432-line test file) was resolved by extracting fixtures to `tests/fixtures/validate_runbook_fixtures.py`. All 9 tests pass. `just dev` is clean.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`check_test_counts` checks all checkpoints against the global test count, not count accumulated to that point**
   - Location: `agent-core/bin/validate-runbook.py:174–188`
   - Note: The implementation collects all `**Test:**` names into one global set, then checks every checkpoint claim against that global count. For multi-phase runbooks with intermediate checkpoints (e.g., "All 2 tests pass" mid-document, "All 5 tests pass" at end), the early checkpoint would be measured against the final total and produce a false violation. Phase 3 spec line 46 says "accumulated to that point" but line 49 says "After all cycles, find all checkpoint claims" — ambiguous for multi-checkpoint cases. All current tests use single-checkpoint fixtures, so no test exercises the bug.
   - **Status**: DEFERRED — No multi-checkpoint test fixture exists in this scope, and the spec is internally contradictory for the multi-checkpoint case. The single-checkpoint design (one checkpoint per phase, at the end) is how real runbooks are structured. Fixing multi-checkpoint accumulation is Phase 4 scope or a future enhancement when real-world runbooks with multiple mid-document checkpoints are encountered.

2. **`VALID_TDD` Common Context checkpoint spec says "All 1 tests pass" but fixture has "All 2 tests pass"**
   - Location: `plans/runbook-quality-gates/runbook-phase-1.md:47`, `tests/fixtures/validate_runbook_fixtures.py:83`
   - Note: The Common Context specification says the VALID_TDD fixture "contains a RED phase with `test_foo` and a checkpoint 'All 1 tests pass'". The fixture has two tests (`test_foo`, `test_bar`) requiring "All 2 tests pass". The execution report documents this correction was deliberate (Cycle 3.1 decision). The Common Context is now stale relative to the fixture.
   - **Status**: FIXED — Updated Common Context to match the implemented fixture.

## Fixes Applied

- `plans/runbook-quality-gates/runbook-phase-1.md:47` — Updated checkpoint claim from "All 1 tests pass" to "All 2 tests pass" to match the VALID_TDD fixture, which has two test functions (`test_foo`, `test_bar`).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-4: Test count reconciliation — checkpoint claims match actual test function count | Satisfied | `check_test_counts` in `validate-runbook.py:167–189`; `test_test_counts_happy_path`, `test_test_counts_mismatch` |
| Parametrized tests: test_foo[param1] and test_foo[param2] count as 1 unique function | Satisfied | `re.sub(r'\[.*?\]$', '', ...)` at line 176; `test_test_counts_parametrized` |
| Exit codes: 0 = pass, 1 = violations found | Satisfied | `cmd_test_counts` at lines 192–202; all three test cases verified |

---

## Positive Observations

- Fixture extraction to `tests/fixtures/validate_runbook_fixtures.py` cleanly resolves the stop condition from Cycle 3.2 — test file dropped from 432 to 275 lines, fixtures module at 230 lines.
- `_args` underscore prefix on the stub handler correctly signals intentionally unused parameter.
- The three fixture constants (`VIOLATION_TEST_COUNTS`, `VIOLATION_TEST_COUNTS_PARAMETRIZED`) accurately represent the boundary cases — mismatch with name listing and parametrized deduplication.
- Execution report is detailed and accurate, including the over-implementation note from Cycle 3.2 and the VALID_TDD checkpoint correction rationale.
