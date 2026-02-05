# Phase 1: Display Formatting (7 cycles)

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

## Cycle 1.3: Format Model Thinking Indicator

**Objective**: Extend `format_model()` to show 😶 when thinking disabled

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_model_thinking_disabled` in `tests/test_statusline_display.py`

**Assertions:**
- `format_model("Claude Sonnet 4", thinking_enabled=False)` returns string containing "😶" emoji
- Output format is `{medal}{thinking_indicator} {name}` (e.g., "🥈😶 Sonnet")
- `format_model("Claude Sonnet 4", thinking_enabled=True)` does NOT contain "😶" emoji
- Output format is `{medal} {name}` (e.g., "🥈 Sonnet")

**Expected failure:** Test expects "😶" but output doesn't contain it when `thinking_enabled=False`

**Why it fails:** `format_model()` doesn't handle thinking_enabled parameter yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_model_thinking_disabled -v`

---

### GREEN Phase

**Implementation:** Extend `format_model()` to accept and use thinking_enabled parameter

**Behavior:**
- Accept `thinking_enabled: bool` parameter
- If `thinking_enabled is False`: Insert "😶" emoji after medal emoji
- If `thinking_enabled is True`: No thinking indicator
- Format: `{medal}{thinking_indicator} {name}` where thinking_indicator is "" or "😶"

**Approach:** Conditional emoji insertion per D1. Shell reference lines 437-438 for thinking indicator.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add thinking_enabled parameter to format_model(), add conditional thinking indicator logic
  Location hint: Within format_model() method

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_model_thinking_disabled -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (no thinking indicator), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-3-notes.md

---

## Cycle 1.4: Format Directory with Emoji

**Objective**: Add `format_directory()` method with 📁 prefix and CYAN color

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_directory` in `tests/test_statusline_display.py`

**Assertions:**
- `format_directory("claudeutils")` returns string containing "📁" emoji
- Output contains directory name "claudeutils"
- Output contains ANSI cyan color code (`\033[36m`)
- Format is `{emoji} {colored_name}` (e.g., "📁 claudeutils")

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_directory'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_directory -v`

---

### GREEN Phase

**Implementation:** Add `format_directory()` method to StatuslineFormatter

**Behavior:**
- Accept directory name as string
- Prefix with "📁" emoji
- Apply CYAN color to directory name
- Return formatted string: `📁 {cyan_name}`

**Approach:** Simple emoji prefix + color application per D1. Shell reference line 448.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_directory(name: str) method
  Location hint: After format_model()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_directory -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-4-notes.md

---

## Cycle 1.5: Format Git Status with Emoji

**Objective**: Add `format_git_status()` method with ✅/🟡 emoji and branch color

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_git_status` in `tests/test_statusline_display.py`

**Assertions:**
- `format_git_status(GitStatus(branch="main", dirty=False))` returns string containing "✅" emoji
- Output contains "main" branch name
- Output contains ANSI green color code (`\033[32m`)
- `format_git_status(GitStatus(branch="feature", dirty=True))` returns string containing "🟡" emoji
- Output contains "feature" branch name
- Output contains ANSI yellow color code (`\033[33m`) and bold code (`\033[1m`)
- Format is `{emoji} {colored_branch}` (e.g., "✅ main" or "🟡 feature")

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_git_status'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_git_status -v`

---

### GREEN Phase

**Implementation:** Add `format_git_status()` method to StatuslineFormatter

**Behavior:**
- Accept GitStatus model (branch: str, dirty: bool)
- If dirty is False: Use "✅" emoji, apply GREEN color to branch
- If dirty is True: Use "🟡" emoji, apply YELLOW + BOLD to branch
- Return formatted string: `{emoji} {colored_branch}`

**Approach:** Conditional emoji and color per dirty state. Shell reference lines 459-461.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_git_status(status: GitStatus) method
  Location hint: After format_directory()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_git_status -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-5-notes.md

---

## Cycle 1.6: Format Cost with Emoji

**Objective**: Add `format_cost()` method with 💰 prefix

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_format_cost` in `tests/test_statusline_display.py`

**Assertions:**
- `format_cost(0.05)` returns string containing "💰" emoji
- Output contains "$0.05" formatted with 2 decimal places
- Format is `{emoji} ${amount:.2f}` (e.g., "💰 $0.05")
- `format_cost(1.234)` returns "💰 $1.23" (rounded to 2 decimals)

**Expected failure:** `AttributeError: 'StatuslineFormatter' object has no attribute 'format_cost'`

**Why it fails:** Method doesn't exist yet

**Verify RED:** `pytest tests/test_statusline_display.py::test_format_cost -v`

---

### GREEN Phase

**Implementation:** Add `format_cost()` method to StatuslineFormatter

**Behavior:**
- Accept cost as float
- Format as dollar amount with 2 decimal places
- Prefix with "💰" emoji
- Return formatted string: `💰 ${amount:.2f}`

**Approach:** Simple emoji prefix + dollar formatting per D1. Shell reference line 475.

**Changes:**
- File: `src/claudeutils/statusline/display.py`
  Action: Add format_cost(amount: float) method
  Location hint: After format_git_status()

**Verify GREEN:** `pytest tests/test_statusline_display.py::test_format_cost -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (AttributeError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-1-6-notes.md

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
