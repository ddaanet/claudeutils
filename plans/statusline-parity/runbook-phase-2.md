# Phase 2: Token Bar and Context (3 cycles)

## Cycle 2.1: Horizontal Token Bar Multi-Block Rendering

**Objective**: Implement `horizontal_token_bar()` with multi-block rendering

**RED Phase:**

**Test**: `horizontal_token_bar()` returns multi-block bar based on token count

**Create test function** in tests/test_statusline_display.py:
```python
def test_horizontal_token_bar() -> None:
    """Horizontal token bar with multi-block rendering."""
    formatter = StatuslineFormatter()

    # Test 25k tokens (1 full block)
    result = formatter.horizontal_token_bar(25000)
    assert "█" in result
    assert result.count("█") == 1

    # Test 50k tokens (2 full blocks)
    result = formatter.horizontal_token_bar(50000)
    assert "█" in result
    assert result.count("█") == 2

    # Test 37500 tokens (1.5 blocks - 1 full + 1 half)
    result = formatter.horizontal_token_bar(37500)
    assert "█" in result
    # Should have partial block character (one of ▏▎▍▌▋▊▉)
    assert any(char in result for char in "▏▎▍▌▋▊▉")

    # Test small count (< 25k, partial block only)
    result = formatter.horizontal_token_bar(12500)
    assert any(char in result for char in "▏▎▍▌▋▊▉")
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'horizontal_token_bar'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `horizontal_token_bar()` method

**Behavior**:
- Each 25,000 tokens = one full block (█)
- Partial blocks use 8-level Unicode: ▏▎▍▌▋▊▉█
- Return bar as string of multiple blocks (e.g., "██▌" for ~62k tokens)
- Shell algorithm: lines 169-215

**Approach**:
- Calculate full blocks: `tokens // 25000`
- Calculate remaining tokens for partial block
- Map remainder to 8-level characters (each level = 3125 tokens)
- Concatenate full blocks + partial block

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `format_mode()`
  Location hint: After Phase 1 methods

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_horizontal_token_bar -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 2.2: Token Bar Progressive Color

**Objective**: Extend `horizontal_token_bar()` with threshold-based color per block

**RED Phase:**

**Test**: `horizontal_token_bar()` applies color based on token thresholds

**Create test function** in tests/test_statusline_display.py:
```python
def test_horizontal_token_bar_color() -> None:
    """Token bar with progressive color per block."""
    formatter = StatuslineFormatter()

    # Test low tokens (< 25k, should be green/brgreen)
    result = formatter.horizontal_token_bar(15000)
    # Should contain green color code (exact code depends on implementation)
    assert "\033[" in result  # ANSI color code present

    # Test high tokens (> 100k, should be red/brred)
    result = formatter.horizontal_token_bar(125000)
    assert "\033[" in result  # ANSI color code present
```

**Expected failure:**
```
AssertionError: assert '\033[' in '█████'
```

**Why it fails**: Method returns plain blocks without color codes

**Verify RED**: `pytest tests/test_statusline_display.py::test_horizontal_token_bar_color -v`
- Must fail with AssertionError on ANSI code presence
- If passes, STOP - color may already be implemented

---

**GREEN Phase:**

**Implementation**: Add color to `horizontal_token_bar()` based on thresholds

**Behavior**:
- Add BRGREEN and BRRED color constants to COLORS dict
- Color blocks based on cumulative token count:
  - < 25k: BRGREEN
  - < 50k: GREEN
  - < 75k: BLUE
  - < 100k: YELLOW
  - < 125k: RED
  - >= 150k: BRRED (with BLINK)
- Each block gets color based on its threshold range
- Shell reference: lines 101-121 for thresholds

**Approach**:
- Extend COLORS dict with bright variants
- Add BLINK constant for critical threshold
- Loop through blocks, apply color based on position × 25k
- Use `colored()` method for each block character

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add BRGREEN, BRRED to COLORS dict (lines ~12-20)
  Action: Add BLINK constant after RESET
  Action: Modify `horizontal_token_bar()` to color each block
  Location hint: Update Cycle 2.1 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_horizontal_token_bar_color -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

## Cycle 2.3: Format Context with Token Bar

**Objective**: Implement `format_context()` integrating horizontal token bar

**RED Phase:**

**Test**: `format_context()` returns 🧠 emoji, colored tokens, and horizontal bar

**Create test function** in tests/test_statusline_display.py:
```python
def test_format_context() -> None:
    """Format context with emoji, tokens, and horizontal bar."""
    formatter = StatuslineFormatter()

    # Test with moderate token count
    result = formatter.format_context(45000)
    assert "🧠" in result
    assert "45k" in result  # Humanized token count
    assert "[" in result and "]" in result  # Bar brackets
    # Should contain block characters
    assert any(char in result for char in "▏▎▍▌▋▊▉█")

    # Test with small token count
    result = formatter.format_context(1500)
    assert "🧠" in result
    assert "1.5k" in result or "1k" in result
```

**Expected failure:**
```
AttributeError: 'StatuslineFormatter' object has no attribute 'format_context'
```

**Why it fails**: Method doesn't exist yet

**Verify RED**: `pytest tests/test_statusline_display.py::test_format_context -v`
- Must fail with AttributeError
- If passes, STOP - method may already exist

---

**GREEN Phase:**

**Implementation**: Add `format_context()` method

**Behavior**:
- Accept context_tokens as integer
- Format tokens using existing `format_tokens()` method
- Generate horizontal bar using `horizontal_token_bar()`
- Color token count based on threshold (same as bar colors)
- Return format: `🧠 {colored_tokens} [{bar}]`
- Shell reference: lines 482-488

**Approach**:
- Call `format_tokens()` for humanized count
- Call `horizontal_token_bar()` for bar
- Determine token count color from same thresholds as bar
- Use `colored()` for token count
- Wrap bar in brackets

**Changes:**
- File: src/claudeutils/statusline/display.py
  Action: Add method after `horizontal_token_bar()`
  Location hint: After Cycle 2.2 method

**Verify GREEN**: `pytest tests/test_statusline_display.py::test_format_context -v`
- Must pass all assertions

**Verify no regression**: `pytest tests/test_statusline_display.py -v`
- All existing tests must still pass

---

**Expected Outcome**: Phase 2 complete with token bar and context formatting
**Error Conditions**: Any AttributeError on expected methods → STOP; Any regression failure → STOP
**Validation**: All RED phases verified ✓, all GREEN phases verified ✓, No regressions ✓
**Success Criteria**: Horizontal bar renders multi-block with color, context integrates bar correctly
