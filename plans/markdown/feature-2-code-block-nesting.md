# Feature 2: Markdown Code Block Nesting

- **Feature:** Detect and properly nest `markdown blocks containing inner` fences
- **File:** `src/claudeutils/markdown.py`
- **Tests:** `tests/test_markdown.py`
- **Model:** Haiku (task coder)

---

## Problem Statement

Claude-generated markdown sometimes includes `markdown blocks that contain inner`
fences. Without proper nesting, these blocks are malformed and dprint cannot format them
correctly.

**Example of problem:**

````
```markdown
# Example
```python
code
```
```
````

The inner ``` fence closes the outer block prematurely, breaking the structure.

**Solution:** Use ```` (4 backticks) for outer fence when inner ``` fences detected:

`````
````markdown
# Example
```python
code
```
````
`````

---

## Requirements

### Success Cases

1. **Nest `` ```markdown `` blocks with inner fences:**
   - Input: `` ```markdown `` block containing `` ``` ``
   - Output: ````markdown block (4 backticks)

### Error Cases

2. **Error on inner fences in non-markdown blocks:**
   - Input: `` ```python `` block containing inner `` ``` ``
   - Output: Raise error with clear message
   - Rationale: Prevents dprint failures downstream

### No-op Cases

3. **Leave `` ```markdown `` blocks without inner fences unchanged:**
   - Input: `` ```markdown `` block with no inner fences
   - Output: Same as input (3 backticks)

---

## TDD Cycles

**Agent Reuse Pattern:**

- Each cycle = one haiku agent call (writes test + minimal code)
- Resume same agent for subsequent cycles while context < 75k
- Launch new agent if context approaches 75k

**Workflow:**

```
Sonnet: Launch/resume haiku agent with Cycle N requirements
Haiku: Writes test (red) + minimal code (green) → returns
Sonnet: Resume haiku agent with Cycle N+1 requirements
... continue through all 4 cycles
```

---

### Cycle 1: Detect ```markdown block with inner fence

**Test:**

`````python
def test_fix_markdown_code_blocks_nests_when_inner_fence_detected() -> None:
    """Test: Nest ```markdown block containing inner ``` fence."""
    input_lines = [
        "```markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        "```\n",
        "```\n",
    ]
    expected = [
        "````markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        "```\n",
        "````\n",
    ]
    assert fix_markdown_code_blocks(input_lines) == expected
`````

**Implementation:**

`````python
def fix_markdown_code_blocks(lines: list[str]) -> list[str]:
    """Nest ```markdown blocks that contain inner ``` fences."""
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect ```markdown block start
        if stripped == "```markdown":
            # Find block end and check for inner fences
            block_lines = [line]
            j = i + 1
            has_inner_fence = False

            while j < len(lines):
                block_line = lines[j]
                block_lines.append(block_line)

                # Check for block end
                if block_line.strip() == "```":
                    # Found end, process block
                    if has_inner_fence:
                        # Use 4 backticks
                        result.append("````markdown\n")
                        result.extend(block_lines[1:-1])  # Content without fences
                        result.append("````\n")
                    else:
                        # No nesting needed
                        result.extend(block_lines)
                    i = j + 1
                    break

                # Check for inner fence (not at end)
                if block_line.strip().startswith("```"):
                    has_inner_fence = True

                j += 1
            else:
                # No closing fence found, append as-is
                result.extend(block_lines)
                i = j
            continue

        result.append(line)
        i += 1

    return result
`````

**Verification:** Run test, ensure it passes

---

### Cycle 2: Leave ```markdown without inner fence unchanged

**Test:**

````python
def test_fix_markdown_code_blocks_no_change_without_inner_fence() -> None:
    """Test: Leave ```markdown block without inner fence unchanged."""
    input_lines = [
        "```markdown\n",
        "# Simple Example\n",
        "No inner fences here\n",
        "```\n",
    ]
    expected = input_lines.copy()
    assert fix_markdown_code_blocks(input_lines) == expected
````

**Implementation:**

- Already handled by `if has_inner_fence` check
- Verify logic works correctly

**Verification:** Run test, ensure it passes

---

### Cycle 3: Error on inner fence in non-markdown block

**Test:**

````python
def test_fix_markdown_code_blocks_errors_on_inner_fence_in_python() -> None:
    """Test: Error when ```python block contains inner fence."""
    input_lines = [
        "```python\n",
        'def foo():\n',
        '    """\n',
        '    Example:\n',
        '    ```\n',
        '    code\n',
        '    ```\n',
        '    """\n',
        "```\n",
    ]

    with pytest.raises(ValueError, match="Inner fence detected in non-markdown block"):
        fix_markdown_code_blocks(input_lines)
````

**Implementation:**

`````python
def fix_markdown_code_blocks(lines: list[str]) -> list[str]:
    """Nest ```markdown blocks that contain inner ``` fences.

    Raises:
        ValueError: If inner fence detected in non-markdown code block
                    (prevents dprint formatting failures)
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect code block start (any language)
        if stripped.startswith("```") and len(stripped) > 3:
            language = stripped[3:]
            is_markdown = language == "markdown"

            # Find block end and check for inner fences
            block_lines = [line]
            j = i + 1
            has_inner_fence = False

            while j < len(lines):
                block_line = lines[j]
                block_lines.append(block_line)

                # Check for block end
                if block_line.strip() == "```":
                    # Found end, process block
                    if has_inner_fence:
                        if is_markdown:
                            # Nest with 4 backticks
                            result.append("````markdown\n")
                            result.extend(block_lines[1:-1])
                            result.append("````\n")
                        else:
                            # Error for non-markdown blocks
                            raise ValueError(
                                f"Inner fence detected in non-markdown block "
                                f"(language: {language}, line: {i + 1}). "
                                f"This will cause dprint formatting to fail."
                            )
                    else:
                        # No nesting needed
                        result.extend(block_lines)
                    i = j + 1
                    break

                # Check for inner fence (not at end)
                if block_line.strip().startswith("```"):
                    has_inner_fence = True

                j += 1
            else:
                # No closing fence found, append as-is
                result.extend(block_lines)
                i = j
            continue

        result.append(line)
        i += 1

    return result
`````

**Verification:** Run test, ensure it raises ValueError

---

### Cycle 4: Handle multiple ```markdown blocks in same file

**Test:**

`````python
def test_fix_markdown_code_blocks_handles_multiple_blocks() -> None:
    """Test: Handle multiple ```markdown blocks correctly."""
    input_lines = [
        "# Doc\n",
        "\n",
        "```markdown\n",
        "```python\n",
        "code\n",
        "```\n",
        "```\n",
        "\n",
        "Some text\n",
        "\n",
        "```markdown\n",
        "No inner fence\n",
        "```\n",
    ]
    expected = [
        "# Doc\n",
        "\n",
        "````markdown\n",
        "```python\n",
        "code\n",
        "```\n",
        "````\n",
        "\n",
        "Some text\n",
        "\n",
        "```markdown\n",
        "No inner fence\n",
        "```\n",
    ]
    assert fix_markdown_code_blocks(input_lines) == expected
`````

**Implementation:**

- Already handled by while loop structure
- Verify logic processes multiple blocks correctly

**Verification:** Run test, ensure it passes

---

## Edge Cases

### Unclosed code blocks

**Test:**

````python
def test_fix_markdown_code_blocks_handles_unclosed_block() -> None:
    """Test: Handle unclosed ```markdown block gracefully."""
    input_lines = [
        "```markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        # No closing fences
    ]
    expected = input_lines.copy()  # Leave as-is
    assert fix_markdown_code_blocks(input_lines) == expected
````

**Implementation:**

- Already handled by `while/else` clause
- Verify unclosed blocks don't break processing

---

### Empty code blocks

**Test:**

````python
def test_fix_markdown_code_blocks_handles_empty_block() -> None:
    """Test: Handle empty ```markdown block."""
    input_lines = [
        "```markdown\n",
        "```\n",
    ]
    expected = input_lines.copy()
    assert fix_markdown_code_blocks(input_lines) == expected
````

**Implementation:**

- Already handled (no inner fences = no change)
- Verify empty blocks work correctly

---

## Integration

**Add to `process_lines`:**

```python
def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    lines = [fix_dunder_references(line) for line in lines]
    lines = fix_metadata_blocks(lines)
    lines = fix_warning_lines(lines)
    lines = fix_nested_lists(lines)
    lines = fix_numbered_list_spacing(lines)
    lines = fix_markdown_code_blocks(lines)  # NEW: Add at end
    return lines
```

**Why at end?**

- Operates on full structure, not line-by-line
- Avoids interfering with other line-based fixes

---

## Validation

**Run all tests:**

```bash
just test tests/test_markdown.py::test_fix_markdown_code_blocks*
```

**Verify no regressions:**

```bash
just test tests/test_markdown.py
```

**Test error case manually:** Create a file with `` ```python `` block containing inner
fence, verify error message is clear and helpful.

---

## Error Message Format

**Clear, actionable error message:**

````
ValueError: Inner fence detected in non-markdown block (language: python, line: 42).
This will cause dprint formatting to fail.

Fix: Remove inner ``` fences from the python block, or escape them properly.
````

---

## Notes

- This fix runs LAST in the pipeline to avoid interfering with line-based fixes
- Error cases are important - prevent silent dprint failures
- Only ```markdown blocks should use nesting; other blocks should error
- Keep implementation simple - detect, validate, nest or error
