# Cycle 4.1

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Cycle 4.1: red-plausibility — happy path (RED function not in prior GREENs, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand current structure from Phase 1.

**RED Phase:**

**Test:** `test_red_plausibility_happy_path`
**Assertions:**
- Running `red-plausibility` on `VALID_TDD` fixture exits with code 0
- Report file written to expected path
- Report contains `**Result:** PASS`
- Report `Summary` shows `Failed: 0`, `Ambiguous: 0`

**Fixture:** `VALID_TDD` — Cycle 1.1 RED expects `ImportError` on `src.module`; no prior GREEN creates `src/module.py` (Cycle 1.1 RED comes before its own GREEN).

**Expected failure:** `AssertionError` — `red-plausibility` handler is still a stub; no report written.

**Why it fails:** `red-plausibility` handler not yet implemented.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_red_plausibility_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_red_plausibility(content, path)` and wire to `red-plausibility` handler.

**Behavior:**
- Process cycles in document order, maintaining `created_names` set (function/module names created in prior cycles' GREEN `**Changes:**` sections only)
- For each cycle N: check its RED `**Expected failure:**` line for function/module names referenced against `created_names` (built from cycles 1..N-1)
- After checking cycle N's RED: add cycle N's own GREEN `Action: Create` entries to `created_names` (making them available for cycles N+1 and beyond)
- If `ImportError` or `ModuleNotFoundError` expected on a name NOT in `created_names` → plausible (no violation)
- Write PASS report, exit 0

**Approach:** Parse `**Expected failure:**` with regex to extract module/function name (e.g., `ImportError` on `src.module` → extract `src.module` or `module`). Parse GREEN `**Changes:**` `Action: Create` entries for file stem names. Only prior cycles' GREENs (cycles 1..N-1) contribute to `created_names` when evaluating cycle N's RED — the current cycle's own GREEN must NOT be included (that GREEN hasn't executed yet when RED is written, so it cannot make the RED already-passing).

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `check_red_plausibility(content, path)` with sequential RED-check then GREEN-accumulate per cycle; wire to handler
  Location hint: After `check_test_counts`, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_red_plausibility_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
