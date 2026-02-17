# Cycle 2.2

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.2: lifecycle — modify-before-create violation (exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_lifecycle` implementation from Cycle 2.1 — understand action tracking data structures.

**RED Phase:**

**Test:** `test_lifecycle_modify_before_create`
**Assertions:**
- Running `lifecycle` on `VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section contains `src/widget.py`
- Report `Violations` section contains `Cycle 1.1` (the modify location) and `no prior creation found`
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE` — Cycle 1.1 has `File: src/widget.py, Action: Modify`; no earlier cycle creates `src/widget.py`.

**Expected failure:** `AssertionError` — current `check_lifecycle` from 2.1 passes all inputs (only tracks creation, doesn't flag modify-before-create).

**Why it fails:** 2.1 GREEN only needs to handle happy path; modify-before-create detection not yet added.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_lifecycle_modify_before_create -v`

---

**GREEN Phase:**

**Implementation:** Add modify-before-create detection to `check_lifecycle`.

**Behavior:**
- When first occurrence of a file path is a "modify" action → violation: file modified before creation
- Violation record: `file_path`, `modify_location` (cycle ID), `"no prior creation found"`
- Write FAIL report with violations, exit 1

**Approach:** When processing a modify action: if `file_path` not in `created_files` set → append violation. Maintain `created_files` set (files where first action was "create"). Process in document order.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add modify-before-create check inside `check_lifecycle`; extend `write_report` to handle lifecycle violation format if needed
  Location hint: Inside `check_lifecycle`, within the action-processing loop

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_lifecycle_modify_before_create -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
