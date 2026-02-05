# Cycle 2.3

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/statusline-parity/reports/cycle-2-3-notes.md`

---

## Cycle 2.3: Format Context with Token Bar Integration

**Objective**: Add `format_context()` method with 🧠 prefix, colored token count, and horizontal token bar

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_context` in `tests/test_statusline_display.py`

**Assertions:**
- `format_context(1500)` returns string containing "🧠" emoji
- Output contains formatted token count "1.5k" (kilos with 1 decimal)
- Output contains horizontal bar from `horizontal_token_bar()` (e.g., "▏" for low tokens)
- Format is `{emoji} {colored_count} {bar}` (e.g., "🧠 1.5k [▏]")
- `format_context(45000)` returns "45k" (no decimal for round thousands)
- Output contains bar with multiple blocks based on 45k tokens
- `format_context(1200000)` returns "1.2M" (millions abbreviated)
- Token count itself has threshold-based color separate from bar colors
- Token count is BRGREEN for < 25k, GREEN for < 50k, BLUE for < 75k, YELLOW for < 100k, RED for < 125k, BRRED+BLINK for >= 150k
- Bar position in output is after token count

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_context'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_context -v`

---

### GREEN Phase

**Implementation:** Add `format_context()` method to StatuslineFormatter

**Behavior:**
- Accept token_count as integer parameter
- Apply threshold-based color to token count based on value ranges (see thresholds below)
- Convert token count to human-readable format (1.5k, 45k, 1.2M)
  - Values < 1M: divide by 1000 for kilos, include decimal for non-round values
  - Values >= 1M: divide by 1,000,000 for millions, round to 1 decimal
- Call `horizontal_token_bar(token_count)` to get colored bar visualization
- Compose final string with brain emoji prefix, colored count, and bar
- Return formatted context string

**Token count color thresholds:**
- < 25k: BRGREEN
- < 50k: GREEN
- < 75k: BLUE
- < 100k: YELLOW
- < 125k: RED
- >= 150k: BRRED + BLINK

**Approach:** Compose from existing helpers. Use threshold-based coloring per D1 and D5. Call `horizontal_token_bar()` from 2.1-2.2. Shell reference lines 101-121 (color thresholds) and 486-488 (context format).

**Hint:** Create helper for number formatting (kilos/millions) or inline the logic. Brain emoji is 🧠 (U+1F9E0).

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add `format_context(token_count: int) -> str` method
  Location hint: After `horizontal_token_bar()` method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_context -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-2-3-notes.md

---

**Light Checkpoint** (end of Phase 2)

1. **Fix:** Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when passing.
2. **Functional:** Review Phase 2 implementations against design. Verify `horizontal_token_bar()` correctly renders multi-block bars with per-block coloring. Verify `format_context()` applies threshold-based color to token count AND calls token bar. Check for stubs (hard-coded returns, incomplete algorithms). If stubs found, STOP and report. If all functional, proceed to Phase 3.

# Phase 3: CLI Integration and Validation - Cycle 3.1 Only
