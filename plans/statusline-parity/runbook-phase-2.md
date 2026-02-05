# Phase 2: Token Bar and Context (3 cycles)

## Cycle 2.1: Horizontal Token Bar Multi-Block Rendering

**Objective**: Create `horizontal_token_bar()` method with 8-level Unicode blocks for multi-block rendering

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_horizontal_token_bar` in `tests/test_statusline_display.py`

**Assertions:**
- `horizontal_token_bar(0)` returns empty string (no tokens)
- `horizontal_token_bar(25000)` returns single full block "█"
- `horizontal_token_bar(12500)` returns single half-block "▌" (8-level partials)
- `horizontal_token_bar(50000)` returns "██" (two full blocks)
- `horizontal_token_bar(37500)` returns "█▌" (one full + one half)
- `horizontal_token_bar(100000)` returns "████" (4 full blocks at 25k per block)
- `horizontal_token_bar(130625)` returns "█████▊" (5 full + 8-level partial at level 5/8)
- All blocks rendered with same color (no color progression yet - tested in 2.2)
- Format: `[{blocks}]` with square brackets

**Unicode levels reference (8-level):**
- Level 0: space " " (0/8)
- Level 1: ▏ (1/8)
- Level 2: ▎ (2/8)
- Level 3: ▍ (3/8)
- Level 4: ▌ (4/8)
- Level 5: ▋ (5/8)
- Level 6: ▊ (6/8)
- Level 7: ▉ (7/8)
- Level 8: █ (8/8 - full block)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'horizontal_token_bar'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`

---

### GREEN Phase

**Implementation:** Add `horizontal_token_bar()` method to StatuslineFormatter

**Behavior:**
- Accept token_count as integer parameter
- Divide tokens into 25k chunks to determine full blocks
- Calculate remainder tokens and map to 8-level Unicode scale (0/8 through 8/8)
- Compose bar string from full block characters (█) plus one partial block if remainder exists
- Wrap result in square brackets
- Return formatted bar string

**Approach:** Direct implementation of shell algorithm (lines 169-215). Uses mathematical division/modulo to calculate blocks, maps remainder fraction to 8-level Unicode scale per D2.

**Hint:** 8-level Unicode blocks defined in RED phase Unicode reference. Map remainder as fraction of 25k, scale 0-8.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add `horizontal_token_bar(token_count: int) -> str` method
  Location hint: After existing formatter methods

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-2-1-notes.md

---

## Cycle 2.2: Horizontal Token Bar Color Progression

**Objective**: Extend `horizontal_token_bar()` to apply progressive color per block based on thresholds

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_horizontal_token_bar_color` in `tests/test_statusline_display.py`

**Assertions:**
- `horizontal_token_bar(12500)` returns colored block matching BRGREEN color (< 25k tokens)
- `horizontal_token_bar(37500)` returns two blocks with BRGREEN for first, GREEN for second (25k-50k range)
- `horizontal_token_bar(62500)` returns three blocks with BRGREEN, GREEN, BLUE colors (50k-75k)
- `horizontal_token_bar(87500)` returns four blocks with color progression: BRGREEN, GREEN, BLUE, YELLOW (75k-100k)
- `horizontal_token_bar(112500)` returns five blocks with BRGREEN, GREEN, BLUE, YELLOW, RED (100k-125k)
- `horizontal_token_bar(137500)` returns color progression ending with BRRED + BLINK for final block (>= 125k)
- Partial blocks use same color as their full block range
- Each block individually colored, not entire bar
- Format: `[{color1}█{color2}█...{reset}]` with color codes inserted per block

**Color thresholds (shell lines 101-121):**
- Block 1 (0-25k): BRGREEN (`\033[92m`)
- Block 2 (25k-50k): GREEN (`\033[32m`)
- Block 3 (50k-75k): BLUE (`\033[34m`)
- Block 4 (75k-100k): YELLOW (`\033[33m`)
- Block 5 (100k-125k): RED (`\033[31m`)
- Block 6+ (>= 125k): BRRED + BLINK (`\033[91m` + `\033[5m`)

**Expected failure:** Output contains block characters but lacks color codes or uses wrong colors

**Why it fails:** `horizontal_token_bar()` doesn't apply color per block yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar_color -v`

---

### GREEN Phase

**Implementation:** Extend `horizontal_token_bar()` to apply threshold-based color per block

**Behavior:**
- For each block position (0, 1, 2...), apply color based on position-to-threshold mapping
- Block 0: BRGREEN
- Block 1: GREEN
- Block 2: BLUE
- Block 3: YELLOW
- Block 4: RED
- Block 5+: BRRED + BLINK
- Partial blocks use same color as their position would have
- Wrap colored blocks in brackets with reset code
- Return colored bar string

**Approach:** Map block position to threshold-based color per D5. Shell reference lines 101-121 for color scheme. Each block gets individual color code wrapper.

**Hint:** Use existing `_color()` helper or inline ANSI codes. Add BRGREEN and BRRED constants if not present.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add BRGREEN and BRRED constants, modify `horizontal_token_bar()` to apply per-block coloring
  Location hint: Within `horizontal_token_bar()` method, after block calculation

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar_color -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (no colors or wrong colors), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-2-2-notes.md

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
