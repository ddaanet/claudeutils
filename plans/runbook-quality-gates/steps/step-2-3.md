# Cycle 2.3

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.3: lifecycle — duplicate creation violation (exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `check_lifecycle` — understand `created_files` tracking from Cycle 2.2.

**RED Phase:**

**Test:** `test_lifecycle_duplicate_creation`
**Assertions:**
- Running `lifecycle` on `VIOLATION_LIFECYCLE_DUPLICATE_CREATE` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section contains `src/module.py`
- Report `Violations` section contains `Cycle 1.1` (first creation) and `Cycle 2.1` (duplicate creation)
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_LIFECYCLE_DUPLICATE_CREATE` — Cycle 1.1 creates `src/module.py`; Cycle 2.1 also creates `src/module.py`.

**Expected failure:** `AssertionError` — current `check_lifecycle` doesn't detect duplicate creation (only tracks first occurrence, not repeated create actions).

**Why it fails:** 2.2 implementation records first creation but doesn't check if a "create" action occurs when file already in `created_files`.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_lifecycle_duplicate_creation -v`

---

**GREEN Phase:**

**Implementation:** Add duplicate creation detection to `check_lifecycle`.

**Behavior:**
- When a "create" action is found for a file already in `created_files`: violation with both cycle IDs
- Violation record: `file_path`, `first_creation_location`, `duplicate_creation_location`
- Write FAIL report with violations, exit 1

**Approach:** When processing a create action: if `file_path` already in `created_files` dict → append duplicate violation with `created_files[file_path]` (first location) and current cycle ID. Both violations (modify-before-create and duplicate creation) can appear in same report.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add duplicate creation check in `check_lifecycle` create-action branch
  Location hint: Inside `check_lifecycle`, create-action handling

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_lifecycle_duplicate_creation -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.

# Phase 3: `test-counts` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phase 1 (script scaffold, importlib infrastructure, `write_report` function)

**Parsing targets:** `**Test:**` fields in RED phases (test function names) + "All N tests pass" checkpoint claims.

---
