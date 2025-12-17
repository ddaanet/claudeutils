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

## TDD Test Sequence (8 Tests)

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
    """Empty string is trivial."""
    assert is_trivial("") is True
```
**Implementation hint:** `if not text.strip(): return True`

#### Test 2: `test_is_trivial_whitespace_only`
```python
def test_is_trivial_whitespace_only():
    """Whitespace-only strings are trivial."""
    for text in [" ", "   ", "\t", "\n", " \t\n "]:
        assert is_trivial(text) is True
```

---

### Group B: Single Characters (Test 3)

#### Test 3: `test_is_trivial_single_character`
```python
def test_is_trivial_single_character():
    """Any single character is trivial."""
    for text in ["a", "z", "1", "!", " x "]:
        assert is_trivial(text) is True
```
**Implementation hint:** `if len(text.strip()) == 1: return True`

---

### Group C: Keywords (Tests 4-6)

#### Test 4: `test_is_trivial_keywords_case_insensitive`
```python
def test_is_trivial_keywords_case_insensitive():
    """Trivial keywords are case-insensitive."""
    # Test all keywords in various cases
    for word in ["y", "n", "k", "g", "ok", "go", "yes", "no",
                 "continue", "proceed", "sure", "okay", "resume"]:
        assert is_trivial(word) is True
        assert is_trivial(word.upper()) is True
        assert is_trivial(word.title()) is True
```
**Implementation hint:** Create set of trivial keywords, check `text.strip().lower() in trivial_set`

#### Test 5: `test_is_trivial_keywords_with_whitespace`
```python
def test_is_trivial_keywords_with_whitespace():
    """Trivial keywords with leading/trailing whitespace."""
    for text in [" continue ", "\tok\t", "  yes  ", "\nresume\n"]:
        assert is_trivial(text) is True
```
**Implementation note:** The `.strip()` handles this automatically

#### Test 6: `test_is_trivial_slash_commands`
```python
def test_is_trivial_slash_commands():
    """Slash commands are trivial."""
    for text in ["/model", "/clear", "/help", "/commit", " /model "]:
        assert is_trivial(text) is True
```
**Implementation hint:** `if text.strip().startswith('/'): return True`

---

### Group D: Non-Trivial Text (Tests 7-8)

#### Test 7: `test_is_trivial_substantive_messages`
```python
def test_is_trivial_substantive_messages():
    """Substantive messages are NOT trivial."""
    for text in [
        "Design a python script",
        "Help me with this bug",
        "yesterday",  # Contains 'y' but not exact match
        "yes I think that works",  # Contains keyword with other text
    ]:
        assert is_trivial(text) is False
```
**Implementation note:** Exact match check prevents false positives

#### Test 8: `test_is_trivial_exact_match_only`
```python
def test_is_trivial_exact_match_only():
    """Case insensitivity applies only to exact keyword matches."""
    # Exact matches are trivial
    for text in ["YeS", "OK", "ContinUE"]:
        assert is_trivial(text) is True

    # Keywords + extra text are NOT trivial
    for text in ["Yes please", "OK done", "continue with this"]:
        assert is_trivial(text) is False
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

- All tests from this spec written and passing
- Red-Green-Refactor cycle followed for each test
- User validation requested after each test-implement iteration
- `just dev` passes (format, check, test)

## After Completion

**STOP HERE.** Do not proceed to Step 3.

Report: `just dev` output and confirmation Step 2 is complete.
