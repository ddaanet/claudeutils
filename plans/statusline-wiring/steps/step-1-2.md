# Cycle 1.2

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-1-2-notes.md`

---

## Cycle 1.2: Handle current_usage as optional (null case)

**Objective**: StatuslineInput.context_window.current_usage can be None (session resume case per R2)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_models.py parses JSON with context_window.current_usage=null without validation error

**Expected failure:**
```
ValidationError: current_usage field required
```

**Why it fails:** ContextUsage not marked as Optional

**Verify RED:** pytest tests/test_statusline_models.py::test_parse_null_current_usage -xvs
- Must fail with ValidationError
- If passes, STOP - field may already be optional

---

**GREEN Phase:**

**Implementation:** Update ContextUsage field in ContextWindowInfo to Optional[ContextUsage]

**Changes:**
- File: src/claudeutils/statusline/models.py
  Action: Change current_usage: ContextUsage to current_usage: ContextUsage | None = None

**Verify GREEN:** pytest tests/test_statusline_models.py::test_parse_null_current_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-1-2-notes.md

---
