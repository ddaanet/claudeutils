# Cycle 3.4

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.4: StatuslineFormatter - vertical bar

**Objective**: Implement vertical_bar() for usage percentage display
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.vertical_bar() generates vertical bar character

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'vertical_bar'
```

**Why it fails:** vertical_bar() method doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_vertical_bar -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add vertical_bar() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add vertical_bar(percentage) returning colored vertical bar based on percentage
- File: tests/test_statusline_display.py
  Action: Test vertical_bar() with various percentages, verify colors

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_vertical_bar -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-4-notes.md

---
