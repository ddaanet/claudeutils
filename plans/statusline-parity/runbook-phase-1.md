# Phase 1: Display Formatting

**Objective:** Implement emoji and color formatting methods in StatuslineFormatter

**Files:**
- Source: `src/claudeutils/statusline/display.py`
- Tests: `tests/test_statusline_display.py`

**Shell reference:** `scratch/home/claude/statusline-command.sh` lines 416-441 (model), 443-463 (directory/git), 474-480 (cost)

---

## Cycle 1.1: Model Tier Extraction

**Objective:** Extract model tier from display_name for emoji/color lookup

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_extract_model_tier`
**Assertions:**
- `_extract_model_tier("Claude Sonnet 4")` returns `"sonnet"`
- `_extract_model_tier("Claude Opus 4")` returns `"opus"`
- `_extract_model_tier("Claude Haiku 4")` returns `"haiku"`
- `_extract_model_tier("Unknown Model")` returns `None`

**Expected failure:** `AttributeError: module 'claudeutils.statusline.display' has no attribute '_extract_model_tier'`

**Why it fails:** Helper function not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_extract_model_tier -v`

---

**GREEN Phase:**

**Implementation:** Add `_extract_model_tier()` helper to StatuslineFormatter

**Behavior:**
- Substring matching against display_name.lower()
- Check "opus" → return "opus"
- Check "sonnet" → return "sonnet"
- Check "haiku" → return "haiku"
- No match → return None

**Approach:** Simple if-elif chain with substring checks (shell lines 416-433 use similar pattern)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add private static method `_extract_model_tier(display_name: str) -> str | None`
  Location hint: Near top of StatuslineFormatter class, before public methods

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_extract_model_tier -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-1-notes.md

---

## Cycle 1.2: Model Formatting with Emoji and Color

**Objective:** Format model display with medal emoji, color, and abbreviated name

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_model`
**Assertions:**
- `format_model("Claude Sonnet 4", thinking_enabled=True)` returns string containing `🥈` emoji
- Output contains substring "Sonnet" (abbreviated, not "Claude Sonnet 4")
- Output includes ANSI yellow color code (`\033[33m`)
- `format_model("Claude Opus 4", thinking_enabled=True)` returns string containing `🥇` emoji
- `format_model("Claude Haiku 4", thinking_enabled=True)` returns string containing `🥉` emoji
- `format_model("Unknown Model", thinking_enabled=True)` returns "Unknown Model" with no emoji

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_model'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_model -v`

---

**GREEN Phase:**

**Implementation:** Add `format_model()` method to StatuslineFormatter

**Behavior:**
- Extract tier using `_extract_model_tier()`
- Look up emoji from MODEL_EMOJI dict (`{"opus": "🥇", "sonnet": "🥈", "haiku": "🥉"}`)
- Look up color from MODEL_COLORS dict (`{"opus": "magenta", "sonnet": "yellow", "haiku": "green"}`)
- Abbreviate name to tier (e.g., "Sonnet" not "Claude Sonnet 4")
- Return colored emoji + abbreviated name

**Approach:** Dict lookups with fallback to display_name if tier unknown (shell lines 416-433)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add class constants MODEL_EMOJI and MODEL_COLORS dicts, implement format_model() method
  Location hint: After existing COLORS dict, method after _extract_model_tier()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_model -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-2-notes.md

---

## Cycle 1.3: Model Thinking Indicator

**Objective:** Add 😶 indicator when thinking disabled

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_model_thinking_disabled`
**Assertions:**
- `format_model("Claude Sonnet 4", thinking_enabled=False)` returns string containing `😶` emoji
- Output contains both `🥈` and `😶` emojis
- `format_model("Claude Sonnet 4", thinking_enabled=True)` does NOT contain `😶` emoji

**Expected failure:** Test assertion failure — output missing `😶` when `thinking_enabled=False`

**Why it fails:** format_model() does not check thinking_enabled parameter

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_model_thinking_disabled -v`

---

**GREEN Phase:**

**Implementation:** Extend format_model() to include thinking indicator

**Behavior:**
- When `thinking_enabled=False`, append `😶` after medal emoji
- When `thinking_enabled=True`, omit indicator
- Format: `🥈😶 Sonnet` or `🥈 Sonnet`

**Approach:** Conditional string concatenation (shell lines 437-438)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Update format_model() signature to accept thinking_enabled parameter, add conditional logic
  Location hint: Modify existing format_model() method body

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_model_thinking_disabled -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-3-notes.md

---

## Cycle 1.4: Directory Formatting

**Objective:** Format directory display with 📁 emoji and CYAN color

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_directory`
**Assertions:**
- `format_directory("claudeutils")` returns string containing `📁` emoji
- Output contains substring "claudeutils"
- Output includes ANSI cyan color code (`\033[36m`)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_directory'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_directory -v`

---

**GREEN Phase:**

**Implementation:** Add format_directory() method to StatuslineFormatter

**Behavior:**
- Prepend 📁 emoji
- Apply CYAN color to directory name
- Return formatted string

**Approach:** Similar pattern to format_model() — emoji + colored text (shell lines 443-448)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Implement format_directory() method
  Location hint: After format_model() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_directory -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-4-notes.md

---

## Cycle 1.5: Git Status Formatting

**Objective:** Format git status with ✅/🟡 emoji and colored branch name

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_git_status`
**Assertions:**
- `format_git_status(GitStatus(branch="main", dirty=False))` returns string containing `✅` emoji
- Output includes ANSI green color code for clean status
- `format_git_status(GitStatus(branch="main", dirty=True))` returns string containing `🟡` emoji
- Output includes ANSI yellow color code and bold for dirty status
- Both outputs contain substring "main"

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_git_status'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_git_status -v`

---

**GREEN Phase:**

**Implementation:** Add format_git_status() method to StatuslineFormatter

**Behavior:**
- Clean status: ✅ emoji + GREEN branch name
- Dirty status: 🟡 emoji + YELLOW BOLD branch name
- Return formatted string

**Approach:** Conditional emoji/color based on dirty flag (shell lines 450-463)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Implement format_git_status() method accepting GitStatus model
  Location hint: After format_directory() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_git_status -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-5-notes.md

---

## Cycle 1.6: Cost Formatting

**Objective:** Format cost display with 💰 emoji prefix

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_cost`
**Assertions:**
- `format_cost(0.05)` returns string containing `💰` emoji
- Output contains "$0.05" (2 decimal places)
- `format_cost(1.234)` returns string containing "$1.23" (rounded)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_cost'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_cost -v`

---

**GREEN Phase:**

**Implementation:** Add format_cost() method to StatuslineFormatter

**Behavior:**
- Prepend 💰 emoji
- Format amount as `$X.XX` with 2 decimal places
- Return formatted string

**Approach:** String formatting with f-string (shell lines 474-480)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Implement format_cost() method
  Location hint: After format_git_status() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_cost -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-6-notes.md

---

## Cycle 1.7: Mode Formatting

**Objective:** Format mode line with 🎫/💳 emoji and colored mode name

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_format_mode`
**Assertions:**
- `format_mode("plan")` returns string containing `🎫` emoji
- Output includes ANSI green color code
- Output contains substring "Plan" (capitalized)
- `format_mode("api")` returns string containing `💳` emoji
- Output includes ANSI yellow color code
- Output contains substring "API" (uppercase)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_mode'`

**Why it fails:** Method not yet implemented

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_mode -v`

---

**GREEN Phase:**

**Implementation:** Add format_mode() method to StatuslineFormatter

**Behavior:**
- Plan mode: 🎫 emoji + GREEN "Plan"
- API mode: 💳 emoji + YELLOW "API"
- Return formatted string

**Approach:** Conditional emoji/color based on mode string (shell lines 627-642)

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Implement format_mode() method
  Location hint: After format_cost() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_mode -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_display.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-1-7-notes.md

---

**Light Checkpoint** (end of Phase 1)
1. Fix: Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when passing.
2. Functional: Review Phase 1 implementations against design. Check for stubs.
