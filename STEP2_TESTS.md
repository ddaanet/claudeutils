# Coding Agent Task: Step 2 - Trivial Feedback Filter (TDD)

## Mission

Implement Step 2 of the Claude Code feedback extraction tool using **strict Test-Driven Development**:
- Write ONE test
- Run it and see it FAIL (Red)
- Implement minimal code to make it PASS (Green)
- Refactor if needed
- Repeat for next test

**STOP after completing all Step 2 tests.** Do not proceed to Step 3.

---

## Project Context

**Location:** `/Users/david/code/claudeutils`

**Reference documents (READ THESE FIRST):**
- `PLAN.md` - Full 5-step implementation plan with all requirements
- `STATUS.md` - Current project status (Step 1 complete)
- `agents/STEP1_COMPLETION.md` - What was completed in Step 1
- `agents/NEXT_AGENT_NOTES.md` - User preferences and workflow

**Current state:**
- Step 1 functions implemented: `encode_project_path()`, `get_project_history_dir()`, `list_top_level_sessions()`
- SessionInfo model defined
- All Step 1 tests passing (16 tests)

**Existing files:**
- `src/claudeutils/main.py` - Add Step 2 function here
- `tests/test_main.py` - Add Step 2 tests here
- `justfile` - Task runner (use `just test`, `just check`, `just format`)

---

## Step 2 Function to Implement

### `is_trivial(text: str) -> bool`
Determines whether user feedback should be filtered out as trivial.

**Trivial patterns:** Empty strings, whitespace-only, single characters, short affirmations, and slash commands.

**Specific patterns to detect:**
- Empty string or whitespace only
- Single characters (any single char)
- Short keywords (case-insensitive): `y`, `n`, `k`, `g`, `ok`, `go`, `yes`, `no`, `continue`, `proceed`, `sure`, `okay`, `resume`
- Slash commands: any text starting with `/` (e.g., `/model`, `/clear`)

**Return value:**
- `True` if text is trivial (should be filtered out)
- `False` if text is substantive (should be kept)

---

## TDD Test Sequence (12 Tests)

Follow this EXACT sequence. For each test:
1. Write the test in `tests/test_main.py`
2. Run `pytest tests/test_main.py::test_is_trivial_{name} -v`
3. See it FAIL
4. Implement minimal code in `src/claudeutils/main.py` to make it pass
5. Run test again - should PASS
6. **Request user validation before continuing to next test**
7. Move to next test

### Group A: Empty and Whitespace (Tests 1-2)

#### Test 1: `test_is_trivial_empty_string`
```python
def test_is_trivial_empty_string():
    """Empty string is trivial"""
    assert is_trivial("") is True
```
**Implementation hint:** `if not text.strip(): return True`

#### Test 2: `test_is_trivial_whitespace_only`
```python
def test_is_trivial_whitespace_only():
    """Whitespace-only strings are trivial"""
    assert is_trivial(" ") is True
    assert is_trivial("   ") is True
    assert is_trivial("\t") is True
    assert is_trivial("\n") is True
    assert is_trivial(" \t\n ") is True
```

---

### Group B: Single Characters (Test 3)

#### Test 3: `test_is_trivial_single_character`
```python
def test_is_trivial_single_character():
    """Any single character is trivial"""
    assert is_trivial("a") is True
    assert is_trivial("z") is True
    assert is_trivial("1") is True
    assert is_trivial("!") is True
    assert is_trivial(" x ") is True  # Single char with whitespace
```
**Implementation hint:** `if len(text.strip()) == 1: return True`

---

### Group C: Short Affirmations (Tests 4-7)

#### Test 4: `test_is_trivial_yes_no_variants`
```python
def test_is_trivial_yes_no_variants():
    """Yes/no variations are trivial (case-insensitive)"""
    assert is_trivial("y") is True
    assert is_trivial("Y") is True
    assert is_trivial("n") is True
    assert is_trivial("N") is True
    assert is_trivial("yes") is True
    assert is_trivial("YES") is True
    assert is_trivial("no") is True
    assert is_trivial("No") is True
```
**Implementation hint:** Create set of trivial keywords, check `text.strip().lower() in trivial_set`

#### Test 5: `test_is_trivial_short_keywords`
```python
def test_is_trivial_short_keywords():
    """Short affirmative keywords are trivial"""
    assert is_trivial("ok") is True
    assert is_trivial("OK") is True
    assert is_trivial("k") is True
    assert is_trivial("K") is True
    assert is_trivial("go") is True
    assert is_trivial("Go") is True
    assert is_trivial("g") is True
    assert is_trivial("G") is True
```

#### Test 6: `test_is_trivial_continuation_keywords`
```python
def test_is_trivial_continuation_keywords():
    """Continuation/approval keywords are trivial"""
    assert is_trivial("continue") is True
    assert is_trivial("Continue") is True
    assert is_trivial("proceed") is True
    assert is_trivial("PROCEED") is True
    assert is_trivial("sure") is True
    assert is_trivial("Sure") is True
    assert is_trivial("okay") is True
    assert is_trivial("Okay") is True
    assert is_trivial("resume") is True
    assert is_trivial("RESUME") is True
```

#### Test 7: `test_is_trivial_with_whitespace`
```python
def test_is_trivial_with_whitespace():
    """Trivial keywords with leading/trailing whitespace"""
    assert is_trivial(" continue ") is True
    assert is_trivial("\tok\t") is True
    assert is_trivial("  yes  ") is True
    assert is_trivial("\nresume\n") is True
```
**Implementation note:** The `.strip()` in earlier implementation handles this automatically

---

### Group D: Slash Commands (Test 8)

#### Test 8: `test_is_trivial_slash_commands`
```python
def test_is_trivial_slash_commands():
    """Slash commands are trivial"""
    assert is_trivial("/model") is True
    assert is_trivial("/clear") is True
    assert is_trivial("/help") is True
    assert is_trivial("/commit") is True
    assert is_trivial(" /model ") is True  # With whitespace
```
**Implementation hint:** `if text.strip().startswith('/'): return True`

---

### Group E: Substantive Text (Tests 9-12)

#### Test 9: `test_is_trivial_substantive_text`
```python
def test_is_trivial_substantive_text():
    """Substantive messages are NOT trivial"""
    assert is_trivial("Design a python script") is False
    assert is_trivial("Help me with this bug") is False
    assert is_trivial("Can you explain this?") is False
    assert is_trivial("Update the function to handle edge cases") is False
```

#### Test 10: `test_is_trivial_longer_than_keywords`
```python
def test_is_trivial_longer_than_keywords():
    """Words containing trivial keywords but longer are NOT trivial"""
    assert is_trivial("yesterday") is False
    assert is_trivial("continuous") is False
    assert is_trivial("okapi") is False
    assert is_trivial("going") is False
    assert is_trivial("surely") is False
```
**Implementation note:** Exact match check prevents these false positives

#### Test 11: `test_is_trivial_sentences_with_keywords`
```python
def test_is_trivial_sentences_with_keywords():
    """Sentences containing trivial keywords are NOT trivial"""
    assert is_trivial("yes I think that works") is False
    assert is_trivial("ok let me explain") is False
    assert is_trivial("continue with the implementation") is False
```

#### Test 12: `test_is_trivial_mixed_case_substantive`
```python
def test_is_trivial_mixed_case_substantive():
    """Case insensitivity applies only to exact keyword matches"""
    assert is_trivial("YeS") is True  # Exact match
    assert is_trivial("Yes please") is False  # More than just keyword
    assert is_trivial("OK") is True  # Exact match
    assert is_trivial("OK done") is False  # More than just keyword
```

---

## Implementation Structure

### Add to `src/claudeutils/main.py`:

```python
def is_trivial(text: str) -> bool:
    """Determine whether user feedback should be filtered as trivial.

    Filters out:
    - Empty strings or whitespace only
    - Single characters
    - Short affirmations: y, n, k, g, ok, go, yes, no, continue, proceed, sure, okay, resume
    - Slash commands (starting with /)

    Args:
        text: User feedback text to evaluate

    Returns:
        True if text is trivial (should be filtered), False if substantive
    """
    # TODO: Implement
    pass
```

### Import in `tests/test_main.py`:

Update import statement to include:
```python
from claudeutils.main import (
    encode_project_path,
    get_project_history_dir,
    SessionInfo,
    list_top_level_sessions,
    is_trivial,  # Add this
)
```

---

## Implementation Strategy

Based on the test cases, the implementation should:

1. **Strip whitespace first:** `text = text.strip()`
2. **Check if empty:** `if not text: return True`
3. **Check if single character:** `if len(text) == 1: return True`
4. **Check if slash command:** `if text.startswith('/'): return True`
5. **Check against keyword set:** Define set of trivial keywords and check `text.lower() in trivial_keywords`

**Trivial keywords set:**
```python
TRIVIAL_KEYWORDS = {
    "y", "n", "k", "g",
    "ok", "go",
    "yes", "no",
    "continue", "proceed", "sure", "okay", "resume"
}
```

---

## Success Criteria

✅ All 12 tests written and passing
✅ Each test followed Red-Green-Refactor cycle
✅ User validation requested after each test-implement iteration
✅ Run `just test` shows all tests passing (Step 1 + Step 2 = 28 tests total)
✅ Run `just check` shows no linting or type errors

---

## User Validation Pattern

After implementing each test, request validation:

```
I've implemented the code to make test_{name} pass.

Test result: PASSING ✓
Ruff: No warnings
MyPy: Type checks passing

Ready to proceed to the next test?
```

---

## After Completion

**STOP HERE.** Do not proceed to Step 3. Report completion:
- Number of new tests passing (should be 12)
- Total tests passing (should be 28: 16 from Step 1 + 12 from Step 2)
- Confirmation that `just dev` passes (format, check, test)
- Confirmation that Step 2 is complete

Next session will handle Step 3 (message parsing and feedback extraction).
