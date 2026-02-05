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
