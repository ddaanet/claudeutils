# Cycle 1.2: next_action derivation for post-ready states

**Timestamp:** 2026-02-21T14:35:00Z

## Status
GREEN_VERIFIED

## Test Command
`pytest tests/test_planstate_inference.py::test_next_action_post_ready_states -v`

## Phase Results

### RED Phase
**Result:** FAIL as expected

Test: `test_next_action_post_ready_states` — parametrized test with 4 cases
- review-pending: Expected `/deliverable-review plans/test-plan`, got `""` (FAIL)
- rework: Expected `""`, got `""` (PASS)
- reviewed: Expected `""`, got `""` (PASS)
- delivered: Expected `""`, got `""` (PASS)

Failure message matched design D-5 specification. The `_derive_next_action()` function had no case for post-ready states, so all returned default `""`.

### GREEN Phase
**Result:** PASS

Implementation added 4 post-ready state cases to `_derive_next_action()`:
- `review-pending` → `/deliverable-review plans/{name}`
- `rework` → `""` (manual fix required)
- `reviewed` → `""` (agent derives merge)
- `delivered` → `""` (terminal)

All 4 parametrized test cases now pass.

### Regression Check
**Result:** 26/26 passed

Full test suite for `test_planstate_inference.py` passes with no regressions.

## Refactoring
Data-driven approach: Extracted template strings into `_NEXT_ACTION_TEMPLATES` dict to reduce cyclomatic complexity from match statement (9 return statements → 7 return statements → 2 return statements with data-driven approach). Reduced PLR0911 complexity warning.

## Files Modified
- `src/claudeutils/planstate/inference.py` — Added `_NEXT_ACTION_TEMPLATES` dict and refactored `_derive_next_action()` to use template.format()
- `tests/test_planstate_inference.py` — Added `test_next_action_post_ready_states` parametrized test

## Stop Condition
None — cycle completed successfully.

## Decision Made
**D-5 Implementation:** Match design specification exactly. Post-ready states: review-pending has defined action (skill delegation), others return empty string (require manual intervention or context-based derivation).

**Refactoring:** Extracted to data structure to reduce complexity. No architectural changes to state machine.
