# Cycle 3.3

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.3: test-counts — parametrized test accounting (test_foo[param1]/[param2] count as 1, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_test_counts` — understand the base-name deduplication logic from Cycle 3.1.

**RED Phase:**

**Test:** `test_test_counts_parametrized`
**Assertions:**
- Running `test-counts` on `VIOLATION_TEST_COUNTS_PARAMETRIZED` fixture exits with code 0
- Report contains `**Result:** PASS`
- Unique function count is 1 (not 2) for `test_foo[param1]` and `test_foo[param2]`

**Fixture:** `VIOLATION_TEST_COUNTS_PARAMETRIZED` — two `**Test:**` fields: `` `test_foo[param1]` `` and `` `test_foo[param2]` ``; checkpoint "All 1 tests pass".

**Expected failure:** `AssertionError` — current implementation stores raw names (no stripping), yielding count 2 for `test_foo[param1]` and `test_foo[param2]` → mismatch with checkpoint claim of 1 → exits 1 instead of 0.

**Why it fails:** 3.1 GREEN collects raw names into the set. Parametrize-bracket stripping is not introduced until this cycle's GREEN phase.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_test_counts_parametrized -v`

---

**GREEN Phase:**

**Implementation:** Ensure parametrized test names are normalized to base function name before deduplication.

**Behavior:**
- Before adding each name to the unique-names set, strip any `[...]` parametrize suffix from the end
- `test_foo[param1]` and `test_foo[param2]` both normalize to `test_foo` → set size 1
- Checkpoint "All 1 tests pass" matches → PASS, exit 0

**Hint:** Use a regex or string operation to strip the bracket suffix from each extracted name before insertion. Apply normalization in the name-collection step. Affects all test counts — verify existing tests still pass with normalization applied.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add parametrize-suffix stripping when collecting unique function names in `check_test_counts`
  Location hint: Inside the test-name collection loop in `check_test_counts`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_test_counts_parametrized -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.

# Phase 4: `red-plausibility` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phase 1 (script scaffold, importlib infrastructure, `write_report` function)

**Parsing targets:** RED `**Expected failure:**` text (function/module names) + GREEN `**Changes:**` sections (what was created in prior cycles).

**Exit codes:** 0 = plausible (no violations), 1 = clear violation (function created in prior GREEN, RED expects ImportError), 2 = ambiguous (function exists but RED tests different behavior).

---
