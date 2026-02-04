# Cycle 2.4

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-4-notes.md`

---

## Cycle 2.4: Parse thinking state from settings.json

**Objective**: get_thinking_state() reads ~/.claude/settings.json and returns ThinkingState(enabled=bool)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py mocks Path.open to return settings JSON with alwaysThinkingEnabled=true, asserts get_thinking_state() returns ThinkingState(enabled=True)

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline.context' has no attribute 'get_thinking_state'
```

**Why it fails:** get_thinking_state() function doesn't exist yet

**Verify RED:** pytest tests/test_statusline_context.py::test_get_thinking_state_enabled -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add get_thinking_state() function that reads ~/.claude/settings.json and parses alwaysThinkingEnabled field

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add get_thinking_state() → ThinkingState, read Path.home() / ".claude" / "settings.json", parse JSON, extract alwaysThinkingEnabled
- File: src/claudeutils/statusline/models.py
  Action: Add ThinkingState(BaseModel) with enabled: bool field

**Verify GREEN:** pytest tests/test_statusline_context.py::test_get_thinking_state_enabled -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-4-notes.md

---
