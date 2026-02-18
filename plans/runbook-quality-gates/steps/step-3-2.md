# Cycle 3.2

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.2: test-counts — count mismatch (checkpoint claims more tests than exist, exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_test_counts` from Cycle 3.1 — understand checkpoint claim extraction and comparison logic.

**RED Phase:**

**Test:** `test_test_counts_mismatch`
**Assertions:**
- Running `test-counts` on `VIOLATION_TEST_COUNTS` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section shows: checkpoint location, claimed count (5), actual count (3)
- Report lists the 3 actual test function names
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_TEST_COUNTS` — three `**Test:**` fields (`test_alpha`, `test_beta`, `test_gamma`) and checkpoint "All 5 tests pass".

**Expected failure:** `AssertionError` — current `check_test_counts` from 3.1 returns PASS for all inputs; violation comparison is not yet implemented.

**Why it fails:** 3.1 GREEN only implements the happy path (no violations). The mismatch detection branch (claimed != actual) is not added until this cycle's GREEN phase.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_test_counts_mismatch -v`

---

**GREEN Phase:**

**Implementation:** Add count-mismatch detection and FAIL path to `check_test_counts`.

**Behavior:**
- After collecting unique function count and checkpoint claims: if `claimed_count != actual_count` → violation
- Violation record: `checkpoint_location` (approximate line context), `claimed_count`, `actual_count`, `test_function_list`
- Write FAIL report with violations, exit 1

**Approach:** `int(match.group(1))` for claimed count; `len(unique_names)` for actual. If mismatch: append violation. Multiple checkpoint claims in same runbook are checked independently — each may match or mismatch.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add comparison logic in `check_test_counts`; update handler to exit 1 on violations
  Location hint: Inside `check_test_counts`, after collecting test names and checkpoint claims

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_test_counts_mismatch -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
