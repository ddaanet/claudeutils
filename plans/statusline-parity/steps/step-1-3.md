# Cycle 1.3

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-3-notes.md`

---

## Cycle 1.3: Format Model Thinking Indicator

**Objective**: Extend `format_model()` to show 😶 when thinking disabled

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_model_thinking_disabled` in `tests/test_statusline_display.py`

**Assertions:**
- `format_model("Claude Sonnet 4", thinking_enabled=False)` returns string containing "😶" emoji
- Output format is `{medal}{thinking_indicator} {name}` (e.g., "🥈😶 Sonnet")
- `format_model("Claude Sonnet 4", thinking_enabled=True)` does NOT contain "😶" emoji
- Output format is `{medal} {name}` (e.g., "🥈 Sonnet")

**Expected failure:** Test expects "😶" but output doesn't contain it when `thinking_enabled=False`

**Why it fails:** `format_model()` doesn't handle thinking_enabled parameter yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_model_thinking_disabled -v`

---

### GREEN Phase

**Implementation:** Extend `format_model()` to accept and use thinking_enabled parameter

**Behavior:**
- Accept `thinking_enabled: bool` parameter
- If `thinking_enabled is False`: Insert "😶" emoji after medal emoji
- If `thinking_enabled is True`: No thinking indicator
- Format: `{medal}{thinking_indicator} {name}` where thinking_indicator is "" or "😶"

**Approach:** Conditional emoji insertion per D1. Shell reference lines 437-438 for thinking indicator.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add thinking_enabled parameter to format_model(), add conditional thinking indicator logic
  Location hint: Within format_model() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_model_thinking_disabled -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (no thinking indicator), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-3-notes.md

---
