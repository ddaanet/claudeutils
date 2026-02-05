# Phase 2: Token Bar and Context

**Objective:** Implement horizontal multi-block token bar and context formatting

**Files:**
- Source: `src/claudeutils/statusline/display.py`
- Tests: `tests/test_statusline_display.py`

**Shell reference:** `scratch/home/claude/statusline-command.sh` lines 169-215 (token bar algorithm), 482-488 (context display)

---

## Cycle 2.1: Horizontal Token Bar Rendering

**Objective:** Implement multi-block token bar with 8-level Unicode characters

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_horizontal_token_bar`
**Assertions:**
- `horizontal_token_bar(25000)` returns string containing exactly 1 full block `█`
- `horizontal_token_bar(50000)` returns string containing exactly 2 full blocks `██`
- `horizontal_token_bar(12500)` returns string containing 1 half block `▌` (partial representation)
- `horizontal_token_bar(30000)` returns string starting with `█` and containing a partial block character
- Each 25,000 tokens = one full block
- Partial blocks use 8-level Unicode: ▏▎▍▌▋▊▉█

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'horizontal_token_bar'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`

---

**GREEN Phase:**

**Implementation:** Add horizontal_token_bar() method to StatuslineFormatter

**Behavior:**
- Calculate full blocks: `tokens // 25000`
- Calculate partial block: remainder mapped to 8-level Unicode
- Each full block renders as `█`
- Partial block uses characters: ▏(1/8) ▎(2/8) ▍(3/8) ▌(4/8) ▋(5/8) ▊(6/8) ▉(7/8) █(8/8)
- Concatenate full blocks + partial block

**Approach:** Integer division and modulo arithmetic (shell lines 169-215 use similar algorithm)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Implement horizontal_token_bar() method, add BLOCK_CHARS constant for Unicode characters
  Location hint: After format_mode() method, add BLOCK_CHARS near other constants

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-2-1-notes.md

---

## Cycle 2.2: Token Bar Color Gradient

**Objective:** Add threshold-based color to token bar blocks

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_horizontal_token_bar_colors`
**Assertions:**
- `horizontal_token_bar(20000)` (< 25k) includes ANSI bright green color code (`\033[92m`)
- `horizontal_token_bar(40000)` (25k-50k range) includes ANSI green color code (`\033[32m`)
- `horizontal_token_bar(70000)` (50k-75k range) includes ANSI blue color code (`\033[34m`)
- `horizontal_token_bar(90000)` (75k-100k range) includes ANSI yellow color code (`\033[33m`)
- `horizontal_token_bar(120000)` (100k-125k range) includes ANSI red color code (`\033[31m`)
- `horizontal_token_bar(160000)` (≥150k) includes ANSI bright red (`\033[91m`) and BLINK (`\033[5m`) codes
- Color applies progressively per block, not to entire bar

**Expected failure:** Test assertion failure — output missing color codes

**Why it fails:** horizontal_token_bar() returns plain string without color

**Verify RED:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar_colors -v`

---

**GREEN Phase:**

**Implementation:** Extend horizontal_token_bar() with threshold-based coloring

**Behavior:**
- Define thresholds: <25k (brgreen), 25k-50k (green), 50k-75k (blue), 75k-100k (yellow), 100k-125k (red), ≥150k (brred+blink)
- For each full block: determine threshold range, apply color
- For partial block: apply color based on total token count
- Wrap each block with color code + block char + RESET

**Approach:** Threshold mapping similar to shell lines 101-121, per-block coloring

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Update horizontal_token_bar() to apply colors, add BRGREEN/BRRED/BLINK constants
  Location hint: Extend existing horizontal_token_bar() method, add color constants near COLORS dict

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_horizontal_token_bar_colors -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-2-2-notes.md

---

## Cycle 2.3: Context Formatting with Token Bar

**Objective:** Format context display with 🧠 emoji, colored token count, and horizontal bar

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_context`
**Assertions:**
- `format_context(1500)` returns string containing `🧠` emoji
- Output contains "1.5k" (kilo-formatted token count)
- Output includes horizontal token bar from horizontal_token_bar()
- Output enclosed in square brackets `[]`
- `format_context(45000)` contains "45k" and multi-block bar
- Token count colored based on threshold (same thresholds as token bar)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_context'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_context -v`

---

**GREEN Phase:**

**Implementation:** Add format_context() method to StatuslineFormatter

**Behavior:**
- Format token count in kilos: 1.5k, 25k, 1.2M (M for millions)
- Apply color to token count based on threshold
- Call horizontal_token_bar() to get colored bar
- Format as: `🧠 <colored_count> [<bar>]`

**Approach:** Kilo formatting + threshold color lookup + horizontal_token_bar() integration (shell lines 482-488)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Implement format_context() method integrating horizontal_token_bar()
  Location hint: After horizontal_token_bar() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_context -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-2-3-notes.md

---

**Light Checkpoint** (end of Phase 2)
1. Fix: Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when passing.
2. Functional: Review Phase 2 implementations against design. Check for stubs.
