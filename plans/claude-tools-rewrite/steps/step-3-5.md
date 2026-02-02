# Cycle 3.5

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.5: StatuslineFormatter - limit display

**Objective**: Implement limit_display() formatting name, percentage, reset time
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.limit_display() formats limit info with colors

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'limit_display'
```

**Why it fails:** limit_display() method doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_limit_display -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add limit_display() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add limit_display(name, pct, reset) formatting string with vertical bar and colored reset time
- File: tests/test_statusline_display.py
  Action: Test limit_display() with various inputs, verify format

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_limit_display -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-5-notes.md

---
