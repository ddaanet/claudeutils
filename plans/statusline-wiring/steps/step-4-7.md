# Cycle 4.7

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-7-notes.md`

---

## Cycle 4.7: Format switchback time as MM/DD HH:MM [DEPENDS: 4.2]

**Objective**: get_switchback_time() calls read_switchback_plist() and formats datetime as "MM/DD HH:MM" (R3)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks read_switchback_plist() to return datetime(2026, 2, 3, 14, 30), asserts get_switchback_time() returns "02/03 14:30"

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline.api_usage' has no attribute 'get_switchback_time'
```

**Why it fails:** get_switchback_time() function doesn't exist yet

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_switchback_time -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add get_switchback_time() → str | None that calls read_switchback_plist(), formats with strftime("%m/%d %H:%M")

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Add get_switchback_time() function, call account.switchback.read_switchback_plist(), return None if None, else format as "MM/DD HH:MM"

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_switchback_time -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-7-notes.md

---

**Light Checkpoint** (end of Phase 4)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 4 implementations against design. Check for stubs.

---
