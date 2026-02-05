# Cycle 1.2

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-2-notes.md`

---

## Cycle 1.2: Format Model with Emoji and Color

**Objective**: Add `format_model()` method with medal emoji and color coding

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_model` in `tests/test_statusline_display.py`

**Assertions:**
- `format_model("Claude Sonnet 4", thinking_enabled=True)` returns string containing "🥈" emoji
- Output contains "Sonnet" (abbreviated name)
- Output contains ANSI yellow color code (`\033[33m`)
- `format_model("Claude Opus 4", thinking_enabled=True)` returns string containing "🥇" emoji
- Output contains ANSI magenta color code (`\033[35m`)
- `format_model("Claude Haiku 4", thinking_enabled=True)` returns string containing "🥉" emoji
- Output contains ANSI green color code (`\033[32m`)
- `format_model("Unknown Model", thinking_enabled=True)` returns full display_name with no emoji

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_model'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_model -v`

---

### GREEN Phase

**Implementation:** Add `format_model()` method to StatuslineFormatter

**Behavior:**
- Extract tier using `_extract_model_tier()`
- If tier exists: Look up emoji from MODEL_EMOJI dict, look up color from MODEL_COLORS dict, abbreviate name
- If tier is None: Return full display_name with no emoji or color
- Apply color using existing `_color()` helper
- Return formatted string: `{emoji} {colored_name}`

**Approach:** Map tier to emoji/color per D1. Shell reference lines 416-428 for emoji mapping.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add class constants MODEL_EMOJI and MODEL_COLORS dicts, add format_model() method
  Location hint: After _extract_model_tier()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_model -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-2-notes.md

---
