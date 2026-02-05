# Phase 1: Display Formatting (7 cycles)

## Cycle 1.1: Extract Model Tier Helper

**Objective**: Implement helper function to extract model tier from display_name

**RED Phase:**

**Test**: `_extract_model_tier()` returns correct tier for known models

**Create test function** in tests/test_statusline_display.py:
```python
def test_extract_model_tier() -> None:
    """Extract model tier from display name."""
    formatter = StatuslineFormatter()

    # Test known models
    assert formatter._extract_model_tier("Claude Sonnet 4") == "sonnet"
    assert formatter._extract_model_tier("Claude Opus 3.7") == "opus"
    assert formatter._extract_model_tier("Claude 3 Haiku") == "haiku"

    # Test case insensitivity
    assert formatter._extract_model_tier("claude SONNET 4") == "sonnet"

    # Test unknown model
    assert formatter._extract_model_tier("Unknown Model") is None
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute '_extract_model_tier'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_extract_model_tier -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `_extract_model_tier()` helper to StatuslineFormatter

**Behavior**:
- Method accepts display_name string parameter
- Returns tier string ("opus", "sonnet", "haiku") for known models
- Returns None for unknown models
- Case-insensitive matching (use `str.lower()`)

**Approach**: Check if tier keywords appear in lowercased display name. Shell reference: lines 416-433 use substring matching.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `RESET` constant definition
  Location hint: After line 21

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_extract_model_tier -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 1.2: Format Model with Emoji and Color

**Objective**: Implement `format_model()` to display model with medal emoji and color

**RED Phase:**

**Test**: `format_model()` returns emoji, color, and abbreviated name

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_model() -> None:
    """Format model with emoji and color."""
    formatter = StatuslineFormatter()

    # Test Sonnet (🥈 yellow)
    result = formatter.format_model("Claude Sonnet 4", thinking_enabled=True)
    assert "🥈" in result
    assert "Sonnet" in result
    assert "\033[33m" in result  # Yellow color code

    # Test Opus (🥇 magenta)
    result = formatter.format_model("Claude Opus 3.7", thinking_enabled=True)
    assert "🥇" in result
    assert "Opus" in result
    assert "\033[35m" in result  # Magenta color code

    # Test Haiku (🥉 green)
    result = formatter.format_model("Claude 3 Haiku", thinking_enabled=True)
    assert "🥉" in result
    assert "Haiku" in result
    assert "\033[32m" in result  # Green color code

    # Test unknown model (no emoji)
    result = formatter.format_model("Unknown Model", thinking_enabled=True)
    assert "Unknown Model" in result
    assert "🥇" not in result and "🥈" not in result and "🥉" not in result
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_model'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_model -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add emoji mappings and `format_model()` method

**Behavior**:
- Add MODEL_EMOJI dict mapping tier names to medal emojis (🥇/🥈/🥉)
- Add MODEL_COLORS dict mapping tier names to color strings
- Method calls `_extract_model_tier()` to get tier from display_name
- For known tiers: return emoji + colored abbreviated name (capitalize tier)
- For unknown models: return display_name without emoji
- thinking_enabled parameter accepted but not used yet (Cycle 1.3)

**Approach**: Shell lines 416-428 show emoji/color mappings. Use existing `colored()` method for color formatting.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add MODEL_EMOJI and MODEL_COLORS class constants after COLORS dict
  Action: Add `format_model()` method after `_extract_model_tier()`
  Location hint: After Cycle 1.1 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_model -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 1.3: Add Thinking Disabled Indicator

**Objective**: Extend `format_model()` to show 😶 when thinking disabled

**RED Phase:**

**Test**: `format_model()` includes 😶 when thinking_enabled=False

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_model_thinking() -> None:
    """Format model with thinking disabled indicator."""
    formatter = StatuslineFormatter()

    # Test thinking disabled (shell line 437-438)
    result = formatter.format_model("Claude Sonnet 4", thinking_enabled=False)
    assert "😶" in result
    assert "🥈" in result
    assert "Sonnet" in result

    # Test thinking enabled (no 😶)
    result = formatter.format_model("Claude Sonnet 4", thinking_enabled=True)
    assert "😶" not in result
    assert "🥈" in result
```

**Expected failure:**
```
AssertionError: assert '😶' in '🥈 \033[33mSonnet\033[0m'
```

**Why it fails**: Method doesn't check thinking_enabled parameter yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_model_thinking -v`
- Must fail with AssertionError on 😶 presence
- If passes, STOP - feature may already exist

---

**GREEN Phase:**

**Implementation**: Extend `format_model()` to add 😶 when thinking disabled

**Behavior**:
- When thinking_enabled=False, include 😶 emoji after model emoji
- When thinking_enabled=True, no thinking indicator
- Format: `{model_emoji}{thinking_indicator} {colored_name}`

**Approach**: Shell lines 437-438 show thinking indicator placement. Use conditional expression for thinking_indicator variable.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Modify `format_model()` method to use thinking_enabled parameter
  Location hint: Add thinking_indicator variable, include in f-string

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_model_thinking -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 1.4: Format Directory with Emoji

**Objective**: Implement `format_directory()` with 📁 prefix and CYAN color

**RED Phase:**

**Test**: `format_directory()` returns 📁 emoji with cyan colored directory name

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_directory() -> None:
    """Format directory with emoji and color."""
    formatter = StatuslineFormatter()

    result = formatter.format_directory("claudeutils")
    assert "📁" in result
    assert "claudeutils" in result
    assert "\033[36m" in result  # CYAN color code
    assert "\033[0m" in result   # Reset code
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_directory'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_directory -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `format_directory()` method

**Behavior**:
- Accept directory basename as string parameter
- Return formatted string with 📁 emoji prefix
- Use CYAN color for directory name

**Approach**: Shell line 448 shows format. Use existing `colored()` method with 'cyan' color.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `format_model()`
  Location hint: After Cycle 1.3 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_directory -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 1.5: Format Git Status with Emoji

**Objective**: Implement `format_git_status()` with ✅/🟡 emoji and branch color

**RED Phase:**

**Test**: `format_git_status()` returns emoji and colored branch based on dirty state

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_git_status() -> None:
    """Format git status with emoji and color."""
    formatter = StatuslineFormatter()

    # Test clean working tree (shell line 459)
    result = formatter.format_git_status("main", dirty=False)
    assert "✅" in result
    assert "main" in result
    assert "\033[32m" in result  # GREEN color code

    # Test dirty working tree (shell line 461)
    result = formatter.format_git_status("feature-branch", dirty=True)
    assert "🟡" in result
    assert "feature-branch" in result
    assert "\033[33m" in result  # YELLOW color code
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_git_status'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_git_status -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `format_git_status()` method

**Behavior**:
- Accept branch name and dirty boolean
- Clean working tree: ✅ emoji with GREEN branch color
- Dirty working tree: 🟡 emoji with YELLOW branch color
- Return formatted status with emoji and colored branch name

**Approach**: Shell lines 459-461 show conditional emoji/color selection. Use if/else for dirty check.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `format_directory()`
  Location hint: After Cycle 1.4 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_git_status -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 1.6: Format Cost with Emoji

**Objective**: Implement `format_cost()` with 💰 prefix

**RED Phase:**

**Test**: `format_cost()` returns 💰 emoji with dollar amount

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_cost() -> None:
    """Format cost with emoji and dollar sign."""
    formatter = StatuslineFormatter()

    result = formatter.format_cost(0.05)
    assert "💰" in result
    assert "$0.05" in result

    # Test zero cost
    result = formatter.format_cost(0.00)
    assert "💰" in result
    assert "$0.00" in result

    # Test larger amount
    result = formatter.format_cost(12.50)
    assert "💰" in result
    assert "$12.50" in result
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_cost'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_cost -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `format_cost()` method

**Behavior**:
- Accept cost as float (USD)
- Return formatted string with 💰 emoji prefix
- Format cost with dollar sign and 2 decimal places

**Approach**: Shell line 475 shows format. Use f-string with `.2f` precision.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `format_git_status()`
  Location hint: After Cycle 1.5 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_cost -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 1.7: Format Mode with Emoji

**Objective**: Implement `format_mode()` with 🎫/💳 emoji and color

**RED Phase:**

**Test**: `format_mode()` returns emoji and colored mode name based on account mode

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_mode() -> None:
    """Format mode with emoji and color."""
    formatter = StatuslineFormatter()

    # Test plan mode (shell line 632)
    result = formatter.format_mode("plan")
    assert "🎫" in result
    assert "Plan" in result
    assert "\033[32m" in result  # GREEN color code

    # Test API mode (shell line 637)
    result = formatter.format_mode("api")
    assert "💳" in result
    assert "API" in result
    assert "\033[33m" in result  # YELLOW color code
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_mode'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_mode -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `format_mode()` method

**Behavior**:
- Accept mode string ("plan" or "api")
- Plan mode: 🎫 emoji with GREEN "Plan" label
- API mode: 💳 emoji with YELLOW "API" label
- Return formatted mode with emoji and colored label

**Approach**: Shell lines 632-637 show conditional emoji/color/label selection. Use if/else for mode check.

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `format_cost()`
  Location hint: After Cycle 1.6 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_mode -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

**Expected Outcome**: Phase 1 complete with 7 formatter methods implemented and tested
**Error Conditions**: Any AttributeError on expected methods → STOP; Any regression failure → STOP
**Validation**: All RED phases verified ✓, all GREEN phases verified ✓, No regressions ✓
**Success Criteria**: 7 format methods exist, all tests pass, emoji/color mappings correct
