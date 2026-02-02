# Cycle 3.2

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.2: StatuslineFormatter - colored text

**Objective**: Implement colored() method returning ANSI-wrapped text
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.colored() wraps text in ANSI color codes

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline' has no attribute 'StatuslineFormatter'
```

**Why it fails:** StatuslineFormatter class doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_colored_text -xvs`
- Must fail with AttributeError
- If passes, STOP - class may already exist

---

**GREEN Phase:**

**Implementation:** Create StatuslineFormatter with colored() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Create StatuslineFormatter class with colored(text, color) returning ANSI-wrapped text
- File: src/claudeutils/statusline/__init__.py
  Action: Add `from .display import StatuslineFormatter`
- File: tests/test_statusline_display.py
  Action: Test colored() with various colors, verify ANSI codes

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_colored_text -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-2-notes.md

---
