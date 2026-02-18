# Cycle 2.1

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.1: lifecycle — happy path (correct create→modify ordering, exit 0)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand current structure from Phase 1: importlib block, `write_report`, subcommand stubs.

**RED Phase:**

**Test:** `test_lifecycle_happy_path`
**Assertions:**
- Running `lifecycle` on `VALID_TDD` fixture exits with code 0
- Report file exists at `plans/valid-tdd/reports/validation-lifecycle.md` (or path derived from fixture job name)
- Report contains `**Result:** PASS`
- Report `Summary` shows `Failed: 0`

**Fixture:** `VALID_TDD` — file `src/module.py` is created in fixture-internal Cycle 1.1 and modified in fixture-internal Cycle 1.2 (correct ordering; these are cycle IDs within the fixture content, not Phase 1 of this runbook).

**Expected failure:** `AssertionError` — `lifecycle` handler is still a stub; no report written.

**Why it fails:** `lifecycle` handler not yet implemented; stub exits 0 without writing report.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_lifecycle_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_lifecycle(content, path)` and wire to `lifecycle` handler.

**Behavior:**
- Reads runbook content (directory → `assemble_phase_files`; file → read directly)
- Extracts all `File:` + `Action:` pairs from each cycle/step in order
- Action classification: "create" actions = `Create`, `Write new`; "modify" actions = `Modify`, `Add`, `Update`, `Edit`, `Extend`
- Builds ordered list of `(cycle_id, file_path, action_type)` tuples
- Records first-occurrence action per file path
- No violations if all first occurrences are "create" (or files are never modified before created)
- Write PASS report, exit 0

**Approach:** Iterate cycles in document order. For each cycle, extract `File:` lines in its `**Changes:**` section and the `Action:` field on the next line. Maintain `dict[file_path, first_seen_cycle_id]` and `dict[file_path, first_action_type]`. No violations for VALID_TDD.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `check_lifecycle(content, path)` function with file action extraction and ordering logic; wire to `lifecycle` handler
  Location hint: After `check_model_tags`, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_lifecycle_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
