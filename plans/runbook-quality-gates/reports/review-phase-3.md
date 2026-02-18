# Runbook Review: Phase 3 — test-counts subcommand

**Artifact**: `plans/runbook-quality-gates/runbook-phase-3.md`
**Date**: 2026-02-17T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (3 cycles)

## Summary

Phase 3 implements the `test-counts` subcommand across 3 cycles: happy path, count mismatch, and parametrized test accounting. The structure and RED assertions are sound. Four issues were found and fixed: a critical RED-plausibility contradiction between 3.1 GREEN and 3.3 RED (stripping described in 3.1 made 3.3 RED implausible), a major fixture consistency gap (`VALID_TDD` described differently across phases), prescriptive code in 3.3 GREEN, and uncertain expected-failure language in 3.2 and 3.3 RED.

**Overall Assessment**: Ready

## Findings

### Critical Issues

1. **RED plausibility contradiction: 3.1 GREEN strips brackets but 3.3 RED assumes they are not stripped**
   - Location: Cycle 3.1 GREEN Behavior/Approach; Cycle 3.3 RED Expected failure
   - Problem: 3.1 GREEN stated "Collect unique test function names (strip `[...]` parametrize suffixes to get base name)" and the Approach said "Collect test names in a set (base name only — strip `[param]` suffix)". Cycle 3.3 RED expected failure stated "current implementation counts raw names without stripping `[...]` suffix". If 3.1 implements stripping as described, 3.3 RED would pass immediately — the cycle would have no failing RED phase.
   - Fix: Removed stripping from 3.1 GREEN Behavior and Approach. 3.1 now collects raw names. Stripping is introduced only in 3.3 GREEN, making 3.3 RED plausibly fail.
   - **Status**: FIXED

### Major Issues

1. **`VALID_TDD` fixture description inconsistent across phases**
   - Location: Cycle 3.1 RED, Fixture line
   - Problem: Phase 1 defines `VALID_TDD` with "sonnet model tag and non-architectural file references". Phase 2 defines it with `src/module.py` created/modified actions. Phase 3 assumed it has a RED phase with `**Test:** \`test_foo\`` and checkpoint "All 1 tests pass" — fields not mentioned in prior-phase definitions. An executor following Phase 1/2 definitions would build a fixture that causes Phase 3 tests to fail unexpectedly.
   - Fix: Updated fixture description to acknowledge the dependency on prior-phase fixture, explicitly state the required test-counts fields, and offer the option to augment or create a separate `VALID_TDD_WITH_TEST_COUNTS` fixture.
   - **Status**: FIXED

### Minor Issues

1. **Prescriptive exact `re.sub` call in 3.3 GREEN Changes and Behavior**
   - Location: Cycle 3.3 GREEN Behavior line and Changes Action field
   - Problem: `re.sub(r'\[.*\]$', '', name)` prescribes the exact Python call, crossing from hint-level guidance into full implementation prescription.
   - Fix: Replaced with behavioral description ("strip any `[...]` parametrize suffix from the end") and a hint note ("Use a regex or string operation to strip the bracket suffix"). Removed specific call from Changes Action field.
   - **Status**: FIXED

2. **Uncertain "may" language in RED expected-failure descriptions**
   - Location: Cycle 3.2 RED Expected failure/Why it fails; Cycle 3.3 RED Expected failure/Why it fails
   - Problem: 3.2 said "may not compare claimed vs actual" and 3.3 said "may use naive set membership". The "may" language is ambiguous — executors need definitive statements about what the implementation does at that point.
   - Fix: 3.2 updated to "returns PASS for all inputs; violation comparison is not yet implemented" and "3.1 GREEN only implements the happy path — mismatch detection is not added until this cycle's GREEN". 3.3 updated to "stores raw names (no stripping)" and "3.1 GREEN collects raw names into the set".
   - **Status**: FIXED

## Fixes Applied

- Cycle 3.1 GREEN Behavior: Removed bracket stripping ("strip `[...]` parametrize suffixes to get base name" → "raw names, no suffix stripping yet")
- Cycle 3.1 GREEN Approach: Removed "base name only — strip `[param]` suffix" → "raw names"
- Cycle 3.1 RED Fixture: Clarified `VALID_TDD` must include test-counts fields; offered augment/separate-fixture option
- Cycle 3.2 RED Expected failure: Replaced "may return PASS" → "returns PASS for all inputs; violation comparison is not yet implemented"
- Cycle 3.2 RED Why it fails: Replaced "may not compare" → definitive statement about 3.1 happy-path scope
- Cycle 3.3 RED Expected failure: Replaced "may use naive set membership" → "stores raw names (no stripping)"
- Cycle 3.3 RED Why it fails: Replaced "may use" → "3.1 GREEN collects raw names into the set"
- Cycle 3.3 GREEN Behavior: Replaced exact `re.sub(r'\[.*\]$', '', name)` with behavioral description
- Cycle 3.3 GREEN (new Hint line): Added hint-level guidance replacing the prescription
- Cycle 3.3 GREEN Changes Action: Removed `re.sub(...)` call from action description

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
