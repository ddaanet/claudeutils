# Cycle 1.1

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-1-notes.md`

---

## Cycle 1.1: Extract Model Tier Helper

**Objective**: Create helper function to extract model tier from display_name

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_extract_model_tier` in `tests/test_statusline_display.py`

**Assertions:**
- `_extract_model_tier("Claude Opus 4")` returns `"opus"`
- `_extract_model_tier("Claude Sonnet 4")` returns `"sonnet"`
- `_extract_model_tier("Claude Haiku 4")` returns `"haiku"`
- `_extract_model_tier("claude opus 3.5")` returns `"opus"` (case-insensitive)
- `_extract_model_tier("Unknown Model")` returns `None`

**Expected failure:** `AttributeError: module 'claudeutils.statusline.display' has no attribute '_extract_model_tier'`

**Why it fails:** Function doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_extract_model_tier -v`

---

### GREEN Phase

**Implementation:** Add `_extract_model_tier()` helper to StatuslineFormatter class

**Behavior:**
- Check if "opus" in display_name.lower() → return "opus"
- Check if "sonnet" in display_name.lower() → return "sonnet"
- Check if "haiku" in display_name.lower() → return "haiku"
- Otherwise → return None

**Approach:** Substring matching per D4 (shell lines 416-433 pattern)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add `_extract_model_tier(display_name: str) -> str | None` method to StatuslineFormatter
  Location hint: Before existing format methods

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_extract_model_tier -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-1-notes.md

---
