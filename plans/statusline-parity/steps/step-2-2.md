# Cycle 2.2

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/statusline-parity/reports/cycle-2-2-notes.md`

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
