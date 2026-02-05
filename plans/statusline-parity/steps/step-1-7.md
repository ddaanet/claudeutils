# Cycle 1.7

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/statusline-parity/reports/cycle-1-7-notes.md`

---

## Cycle 1.7: Format Mode with Emoji

**Objective**: Add `format_mode()` method with 🎫/💳 emoji and color

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_mode` in `tests/test_statusline_display.py`

**Assertions:**
- `format_mode("plan")` returns string containing "🎫" emoji
- Output contains "Plan" (capitalized)
- Output contains ANSI green color code (`\033[32m`)
- `format_mode("api")` returns string containing "💳" emoji
- Output contains "API" (capitalized)
- Output contains ANSI yellow color code (`\033[33m`)
- Format is `{emoji} {colored_mode}` (e.g., "🎫 Plan" or "💳 API")

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_mode'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_mode -v`

---

### GREEN Phase

**Implementation:** Add `format_mode()` method to StatuslineFormatter

**Behavior:**
- Accept mode as string ("plan" or "api")
- If mode is "plan": Use "🎫" emoji, capitalize to "Plan", apply GREEN color
- If mode is "api": Use "💳" emoji, capitalize to "API", apply YELLOW color
- Return formatted string: `{emoji} {colored_mode}`

**Approach:** Conditional emoji and color per mode type. Shell reference lines 632-637.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_mode(mode: str) method
  Location hint: After format_cost()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_mode -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-7-notes.md

---

**Light Checkpoint** (end of Phase 1)

1. **Fix:** Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when passing.
2. **Functional:** Review Phase 1 implementations against design. Check for stubs (constant returns, no computation). If stubs found, STOP and report. If all functional, proceed to Phase 2.

# Phase 2: Token Bar and Context (3 cycles)
