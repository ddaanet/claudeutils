# Feature 1: Checklist Detection (Any Consistent Prefix)

- **Feature:** Extend `fix_warning_lines` to detect any consistent non-markup prefix
- **File:** `src/claudeutils/markdown.py`
- **Tests:** `tests/test_markdown.py`
- **Model:** Haiku (task coder)

---

## Current Implementation

The existing `fix_warning_lines` function handles:

- Lines starting with `"⚠️ "`
- Lines matching `"Option [A-Z]: "` pattern

```python
def fix_warning_lines(lines: list[str]) -> list[str]:
    """Convert consecutive ⚠️ or Option X: lines to list items."""
    result = []
    i = 0
    option_pattern = r"^Option [A-Z]: "

    def is_listable_line(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("⚠️ ") or bool(re.match(option_pattern, stripped))

    while i < len(lines):
        line = lines[i]
        if is_listable_line(line):
            warning_lines = [line]
            j = i + 1
            while j < len(lines) and is_listable_line(lines[j]):
                warning_lines.append(lines[j])
                j += 1
            if len(warning_lines) >= 2:
                for warn_line in warning_lines:
                    stripped = warn_line.strip()
                    result.append(f"- {stripped}\n")
                i = j
                continue
        result.append(line)
        i += 1
    return result
```

---

## Required Changes

**Goal:** Detect ANY consistent non-markup prefix pattern, not just `⚠️` and `Option X:`

**Strategy:**

1. Extract prefix from line (non-whitespace characters before first space or word
   boundary)
2. Check if prefix is NOT a markdown list marker (`-`, `*`, `1.`, etc.)
3. Group consecutive lines with similar prefix patterns
4. Convert groups of 2+ lines to list items

**Examples of prefixes to detect:**

- `"✅ "` - checkmark emoji
- `"❌ "` - cross emoji
- `"⚠️ "` - warning emoji (already handled)
- `"[TODO]"` - bracketed text
- `"NOTE:"` - text with colon
- Any other consistent pattern

---

## TDD Cycles

**Agent Reuse Pattern:**

- Each cycle = one haiku agent call (writes test + minimal code)
- Resume same agent for subsequent cycles while context < 75k
- Launch new agent if context approaches 75k

**Workflow:**

```
Sonnet: Launch haiku agent with Cycle 1 requirements
Haiku: Writes test (red) + minimal code (green) → returns
Sonnet: Resume haiku agent with Cycle 2 requirements
Haiku: Writes test (red) + minimal code (green) → returns
... continue reusing agent through all 6 cycles (if context permits)
```

---

### Cycle 1: Detect checkmark emoji prefix

**Test:**

```python
def test_fix_warning_lines_handles_checkmark_emoji() -> None:
    """Test: fix_warning_lines converts consecutive ✅ lines to list."""
    input_lines = [
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
    ]
    expected = [
        "- ✅ Issue #1: XPASS tests visible\n",
        "- ✅ Issue #2: Setup failures captured\n",
    ]
    assert fix_warning_lines(input_lines) == expected
```

**Implementation:**

- Add `"✅ "` to `is_listable_line` check
- Minimal change: `stripped.startswith("✅ ")` or similar

**Verification:** Run test, ensure it passes

---

### Cycle 2: Detect cross emoji prefix

**Test:**

```python
def test_fix_warning_lines_handles_cross_emoji() -> None:
    """Test: fix_warning_lines converts consecutive ❌ lines to list."""
    input_lines = [
        "❌ Failed test 1\n",
        "❌ Failed test 2\n",
    ]
    expected = [
        "- ❌ Failed test 1\n",
        "- ❌ Failed test 2\n",
    ]
    assert fix_warning_lines(input_lines) == expected
```

**Implementation:**

- Add `"❌ "` to `is_listable_line` check

**Verification:** Run test, ensure it passes

---

### Cycle 3: Detect mixed emoji prefixes with similar pattern

**Test:**

```python
def test_fix_warning_lines_handles_mixed_emoji_prefix() -> None:
    """Test: fix_warning_lines converts mixed ✅/❌ lines to list."""
    input_lines = [
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
        "❌ Issue #3: Not fixed yet\n",
    ]
    expected = [
        "- ✅ Issue #1: XPASS tests visible\n",
        "- ✅ Issue #2: Setup failures captured\n",
        "- ❌ Issue #3: Not fixed yet\n",
    ]
    assert fix_warning_lines(input_lines) == expected
```

**Implementation:**

- Refactor to detect "similar pattern" not just exact match
- Extract prefix pattern (emoji before space, or text before colon, etc.)
- Group lines with similar prefix structure

**Verification:** Run test, ensure it passes

---

### Cycle 4: Don't trigger on existing list items

**Test:**

```python
def test_fix_warning_lines_skips_existing_lists() -> None:
    """Test: fix_warning_lines skips lines already formatted as lists."""
    input_lines = [
        "- ✅ Issue #1: Already a list\n",
        "- ✅ Issue #2: Already a list\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected
```

**Implementation:**

- Check if line starts with `-`, `*`, or number pattern
- Skip lines that are already list items

**Verification:** Run test, ensure it passes

---

### Cycle 5: Don't convert single lines

**Test:**

```python
def test_fix_warning_lines_skips_single_line() -> None:
    """Test: fix_warning_lines skips single line with emoji prefix."""
    input_lines = [
        "✅ Only one line\n",
        "\n",
        "Some other content\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected
```

**Implementation:**

- Already handled by `if len(warning_lines) >= 2` check
- Verify existing logic works

**Verification:** Run test, ensure it passes

---

### Cycle 6: Handle bracket and colon patterns

**Test:**

```python
def test_fix_warning_lines_handles_bracket_and_colon_prefix() -> None:
    """Test: fix_warning_lines handles [TODO] and NOTE: patterns."""
    input_lines = [
        "[TODO] Implement feature X\n",
        "[TODO] Write tests\n",
        "\n",
        "NOTE: This is important\n",
        "NOTE: Remember this\n",
    ]
    expected = [
        "- [TODO] Implement feature X\n",
        "- [TODO] Write tests\n",
        "\n",
        "- NOTE: This is important\n",
        "- NOTE: Remember this\n",
    ]
    assert fix_warning_lines(input_lines) == expected
```

**Implementation:**

- Generalize prefix detection to handle brackets and colons
- Extract prefix pattern: characters before first space or end of "word"

**Verification:** Run test, ensure it passes

---

## Implementation Strategy

### Refactor `is_listable_line` to `extract_prefix`

- **Current approach:** Hard-coded patterns
- **New approach:** Generic prefix extraction

```python
def extract_prefix(line: str) -> str | None:
    """Extract non-markup prefix from line.

    Returns None if line:
    - Is already a list item (starts with -, *, or number)
    - Has no clear prefix pattern

    Returns prefix string if line has consistent non-markup prefix.
    """
    stripped = line.strip()

    # Skip existing list items
    if re.match(r'^[-*]|^\d+\.', stripped):
        return None

    # Extract prefix (logic to be developed in TDD cycles)
    # Examples:
    # "✅ Text" -> "✅"
    # "[TODO] Text" -> "[TODO]"
    # "NOTE: Text" -> "NOTE:"

    # Placeholder: implement in TDD cycles
    pass
```

### Refactor main loop to use prefix grouping

```python
def fix_warning_lines(lines: list[str]) -> list[str]:
    """Convert consecutive lines with consistent non-markup prefix to list items."""
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        prefix = extract_prefix(line)

        if prefix:
            # Find all consecutive lines with similar prefix
            prefixed_lines = [line]
            j = i + 1
            while j < len(lines):
                next_prefix = extract_prefix(lines[j])
                if next_prefix and is_similar_prefix(prefix, next_prefix):
                    prefixed_lines.append(lines[j])
                    j += 1
                else:
                    break

            # Convert if 2+ lines
            if len(prefixed_lines) >= 2:
                for pline in prefixed_lines:
                    result.append(f"- {pline.strip()}\n")
                i = j
                continue

        result.append(line)
        i += 1

    return result

def is_similar_prefix(prefix1: str, prefix2: str) -> bool:
    """Check if two prefixes are similar enough to group together."""
    # Placeholder: implement in TDD cycles
    # Examples:
    # "✅" and "✅" -> True (exact match)
    # "✅" and "❌" -> True (both emoji)
    # "[TODO]" and "[DONE]" -> True (both bracketed)
    # "✅" and "[TODO]" -> False (different patterns)
    pass
```

---

## Integration

**Update `process_lines`:**

```python
def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    lines = [fix_dunder_references(line) for line in lines]
    lines = fix_metadata_blocks(lines)
    lines = fix_warning_lines(lines)  # Extended in this feature
    lines = fix_nested_lists(lines)
    return fix_numbered_list_spacing(lines)
```

No changes needed - `fix_warning_lines` already in pipeline.

---

## Validation

**Run all tests:**

```bash
just test tests/test_markdown.py::test_fix_warning_lines*
```

**Verify no regressions:**

```bash
just test tests/test_markdown.py
```

**Check existing patterns still work:**

- `"⚠️ "` lines still convert
- `Option X:` lines still convert
- Integration with other fixes still works

---

## Notes

- Keep backward compatibility with existing `⚠️` and `Option X:` patterns
- Refactor incrementally - each TDD cycle adds one test and minimal code
- Don't over-engineer - implement only what tests require
- Similar prefix matching should be simple (e.g., same prefix type: emoji, bracket,
  colon)
