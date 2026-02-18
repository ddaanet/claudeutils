# Cycle 4.2

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Cycle 4.2: red-plausibility — clear violation (function created in prior GREEN, RED expects ImportError, exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_red_plausibility` from Cycle 4.1 — understand `created_names` tracking and name extraction.

**RED Phase:**

**Test:** `test_red_plausibility_violation`
**Assertions:**
- Running `red-plausibility` on `VIOLATION_RED_IMPLAUSIBLE` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section names: the function (`widget`), prior GREEN cycle that created it (1.1), current RED cycle (1.2)
- Report `Summary` shows `Failed: 1`, `Ambiguous: 0`

**Fixture:** `VIOLATION_RED_IMPLAUSIBLE` — Cycle 1.1 GREEN creates `src/widget.py` with `widget()` function; Cycle 1.2 RED expects `ImportError` — `widget` not importable. Since `widget.py` was created in prior GREEN, RED would already pass.

**Expected failure:** `AssertionError` — current 4.1 implementation passes all inputs as plausible; violation detection not yet added.

**Why it fails:** 4.1 GREEN spec defines happy-path-only behavior (exit 0 for all plausible inputs); violation detection branch does not exist yet.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_red_plausibility_violation -v`

---

**GREEN Phase:**

**Implementation:** Add clear-violation detection to `check_red_plausibility`.

**Behavior:**
- When RED expects `ImportError` or `ModuleNotFoundError` on a name that IS in `created_names`: clear violation (exit 1)
- Violation record: `function_name`, `created_in` (prior cycle ID), `red_cycle_id`
- Write FAIL report with violations, exit 1

**Approach:** Collect `created_names` from prior cycles' GREENs only (cycles 1..N-1, NOT the current cycle's own GREEN). Check current cycle's RED `**Expected failure:**`. If failure type is `ImportError`/`ModuleNotFoundError` AND the name appears in `created_names` → violation. `sys.exit(1)` with violations.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add clear-violation check in RED-phase processing block of `check_red_plausibility`; update handler to exit 1
  Location hint: Inside `check_red_plausibility`, RED phase processing block

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_red_plausibility_violation -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
