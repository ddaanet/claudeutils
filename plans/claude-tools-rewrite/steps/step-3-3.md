# Cycle 3.3

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.3: StatuslineFormatter - token bar

**Objective**: Implement token_bar() returning Unicode block progress bar
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** StatuslineFormatter.token_bar() generates progress bar with Unicode blocks

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'token_bar'
```

**Why it fails:** token_bar() method doesn't exist

**Verify RED:** `pytest tests/test_statusline_display.py::test_token_bar -xvs`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation:** Add token_bar() method

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add token_bar(tokens, max_tokens) calculating percentage and rendering Unicode blocks
- File: tests/test_statusline_display.py
  Action: Test token_bar() with various values, verify block characters and colors

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_token_bar -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-3-notes.md

---
