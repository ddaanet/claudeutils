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
# Phase 3: CLI Integration and Validation

**Objective:** Add Python environment detection, integrate formatter methods into CLI, and validate visual parity

**Files:**
- Source: `src/claudeutils/statusline/context.py`, `src/claudeutils/statusline/models.py`, `src/claudeutils/statusline/cli.py`
- Tests: `tests/test_statusline_context.py`, `tests/test_statusline_cli.py`

**Shell reference:** `scratch/home/claude/statusline-command.sh` lines 465-472 (Python env), full output lines 441-488

---

## Cycle 3.1: Python Environment Detection

**Objective:** Add get_python_env() function and PythonEnv model

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_get_python_env`
**Assertions:**
- `get_python_env()` with `VIRTUAL_ENV="/path/to/venv"` returns `PythonEnv(name="venv")`
- `get_python_env()` with `CONDA_DEFAULT_ENV="myenv"` returns `PythonEnv(name="myenv")`
- `get_python_env()` with no environment variables returns `PythonEnv(name=None)`
- VIRTUAL_ENV takes precedence if both are set

**Expected failure:** `ImportError: cannot import name 'get_python_env' from 'claudeutils.statusline.context'` or `ImportError: cannot import name 'PythonEnv' from 'claudeutils.statusline.models'`

**Why it fails:** Function and model not yet implemented

**Verify RED:** `pytest tests/test_statusline_context.py::test_get_python_env -v`

---

**GREEN Phase:**

**Implementation:** Add get_python_env() to context.py and PythonEnv model to models.py

**Behavior:**
- Check `os.environ.get("VIRTUAL_ENV")` → extract basename as name
- If not found, check `os.environ.get("CONDA_DEFAULT_ENV")` → use directly as name
- If neither found, return `PythonEnv(name=None)`
- PythonEnv model has optional `name` field

**Approach:** Environment variable lookups with os.path.basename (shell lines 465-472)

**Changes:**
- File: `src/claudeutils/statusline/context.py`
  Action: Implement get_python_env() function
  Location hint: After existing context functions
- File: `src/claudeutils/statusline/models.py`
  Action: Add PythonEnv Pydantic model with optional name field
  Location hint: After existing models

**Verify GREEN:** `pytest tests/test_statusline_context.py::test_get_python_env -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_context.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-3-1-notes.md

---

## Cycle 3.2: CLI Line 1 Composition

**Objective:** Replace string concatenation with formatter method calls for Line 1

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_cli_line1_format`
**Assertions:**
- Line 1 output contains `🥈` emoji (from format_model())
- Line 1 output contains `📁` emoji (from format_directory())
- Line 1 output contains `✅` or `🟡` emoji (from format_git_status())
- Line 1 output contains `💰` emoji (from format_cost())
- Line 1 output contains `🧠` emoji (from format_context())
- Output includes ANSI color codes (verify at least one color present)
- Test with mock data: display_name="Claude Sonnet 4", directory="claudeutils", git clean, cost=0.05, tokens=45000

**Expected failure:** Test assertion failure — output missing emojis and colors

**Why it fails:** CLI still uses plain string concatenation

**Verify RED:** `pytest tests/test_statusline_cli.py::test_cli_line1_format -v`

---

**GREEN Phase:**

**Implementation:** Update CLI Line 1 composition to use formatter methods

**Behavior:**
- Call `format_model(display_name, thinking_enabled)` for model display
- Call `format_directory(current_dir)` for directory display
- Call `format_git_status(git_status)` for git display
- Call `format_cost(total_cost_usd)` for cost display
- Call `format_context(context_tokens)` for context display
- Join with spaces to form Line 1

**Approach:** Replace existing string joins with formatter method calls

**Changes:**
- File: `src/claudeutils/statusline/cli.py`
  Action: Update Line 1 composition logic to call format_* methods from StatuslineFormatter
  Location hint: Find Line 1 construction (likely variable assignment), replace with formatter calls

**Verify GREEN:** `pytest tests/test_statusline_cli.py::test_cli_line1_format -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_cli.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-3-2-notes.md

---

## Cycle 3.3: CLI Line 2 Composition

**Objective:** Integrate format_mode() into Line 2 composition

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_cli_line2_format`
**Assertions:**
- Line 2 output contains `🎫` emoji (plan mode) or `💳` emoji (API mode)
- Output includes ANSI color codes (green for plan, yellow for API)
- Mode name capitalized: "Plan" or "API"
- Usage data formatting unchanged (existing behavior preserved)
- Test with mock data: mode="plan", usage data present

**Expected failure:** Test assertion failure — output missing mode emoji and color

**Why it fails:** CLI still uses plain "mode:" text prefix

**Verify RED:** `pytest tests/test_statusline_cli.py::test_cli_line2_format -v`

---

**GREEN Phase:**

**Implementation:** Update CLI Line 2 composition to use format_mode()

**Behavior:**
- Call `format_mode(account_state.mode)` for mode display
- Replace "mode:" prefix with formatted output
- Preserve existing usage data formatting

**Approach:** Replace mode prefix construction with format_mode() call

**Changes:**
- File: `src/claudeutils/statusline/cli.py`
  Action: Update Line 2 composition to call format_mode() instead of plain text
  Location hint: Find Line 2 construction, replace mode prefix with format_mode()

**Verify GREEN:** `pytest tests/test_statusline_cli.py::test_cli_line2_format -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_cli.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-3-3-notes.md

---

## Cycle 3.4: Integration Validation

**Objective:** Validate end-to-end visual parity against shell output

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_visual_parity_integration`
**Assertions:**
- End-to-end test with realistic mock data produces output matching shell format
- Line 1 pattern: `🥈 Sonnet  📁 claudeutils  ✅ tools-rewrite  💰 $0.05  🧠 45k [██]`
- Line 2 pattern: `🎫 Plan  5h 45% ▆ 2:30 / 7d 23% ▂`
- All emojis present
- All color codes present (verify ANSI codes in output)
- Token bar renders correctly
- Edge cases:
  - Missing data (no git status) → graceful fallback
  - Unknown model name → display full name with no emoji
  - Python environment present → 🐍 indicator in output
  - Terminal width constraints → bar width reasonable

**Expected failure:** Test assertion failure — edge cases not handled, or presentation gaps

**Why it fails:** Integration gaps not yet addressed

**Verify RED:** `pytest tests/test_statusline_cli.py::test_visual_parity_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix presentation gaps and edge case handling

**Behavior:**
- Handle missing data gracefully (empty strings, None values)
- Unknown model names display full name
- Python environment formatted as `🐍 <name>` when present
- Token bar width bounded (max 7 blocks for 175k context limit)
- ANSI codes properly closed (RESET after colors)

**Approach:** Add fallback logic and edge case handling based on test failures

**Changes:**
- File: `src/claudeutils/statusline/cli.py`
  Action: Add edge case handling and fallbacks as needed
  Location hint: Update formatter method calls with conditionals for missing data
- File: `src/claudeutils/statusline/display.py`
  Action: Fix any gaps found during integration testing
  Location hint: Update format_* methods with defensive checks

**Verify GREEN:** `pytest tests/test_statusline_cli.py::test_visual_parity_integration -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline_cli.py -v`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions, visual parity achieved
**Report Path:** plans/statusline-parity/reports/cycle-3-4-notes.md

---

**Full Checkpoint** (end of Phase 3)
1. Fix: Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when green.
2. Vet: Review all changes for quality, clarity, design alignment. Apply high/medium fixes. Commit.
3. Functional: Review all implementations against design. Check for stubs.
# Phase 4: TTL Update

**Objective:** Update UsageCache TTL to match design spec

**Files:**
- Source: `src/claudeutils/account/usage.py`
- Tests: `tests/test_account_usage.py` (if exists) or integration test in CLI tests

**Design reference:** D7 — TTL adjustment from 30s to 10s (non-critical)

---

## Cycle 4.1: TTL Constant Update

**Objective:** Update UsageCache TTL from 30 seconds to 10 seconds

**Script Evaluation:** Direct execution (TDD cycle)
**Execution Model:** Haiku

**Implementation:**

**RED Phase:**

**Test:** `test_usage_cache_ttl`
**Assertions:**
- UsageCache instance has TTL attribute equal to 10 (seconds)
- Or if TTL is class-level constant: `UsageCache.TTL == 10`
- Verify cache expires after 10 seconds (mock time.time() if needed)

**Expected failure:** Test assertion failure — TTL is 30, not 10

**Why it fails:** TTL constant still set to 30 seconds

**Verify RED:** `pytest tests/test_account_usage.py::test_usage_cache_ttl -v` (or appropriate test location)

---

**GREEN Phase:**

**Implementation:** Update TTL constant in UsageCache

**Behavior:**
- Change TTL from 30 to 10
- No other logic changes
- Cache expiration behavior unchanged (just shorter TTL)

**Approach:** Single constant assignment

**Changes:**
- File: `src/claudeutils/account/usage.py`
  Action: Update TTL constant from 30 to 10
  Location hint: Find TTL constant definition (likely near class definition or __init__)

**Verify GREEN:** `pytest tests/test_account_usage.py::test_usage_cache_ttl -v`
- Must pass

**Verify no regression:** `pytest tests/test_account_usage.py -v` or `just test`
- All existing tests pass

**Expected Outcome:** GREEN verification, no regressions
**Report Path:** plans/statusline-parity/reports/cycle-4-1-notes.md

---

**Light Checkpoint** (end of Phase 4)
1. Fix: Run `just dev`. Sonnet quiet-task diagnoses and fixes failures. Commit when passing.
2. Functional: Review Phase 4 implementation. Verify TTL change only.
