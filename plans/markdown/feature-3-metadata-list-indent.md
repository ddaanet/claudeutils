# Feature 3: Metadata List Indentation

- **Feature:** Convert metadata labels to list items and indent following lists
- **File:** `src/claudeutils/markdown.py`
- **Tests:** `tests/test_markdown.py`
- **Model:** Haiku (task coder)

---

## Problem Statement

When Claude generates metadata labels followed by lists, the structure needs proper
formatting:

**Current output:**

```
**Plan Files:**
- `plans/phase-1.md`
- `plans/phase-2.md`
```

**Should be:**

```
- **Plan Files:**
  - `plans/phase-1.md`
  - `plans/phase-2.md`
```

The metadata label should become a list item, and the following list should be indented
by 2 spaces to create a proper nested list.

---

## Relation to Existing `fix_metadata_blocks`

**Existing function:**

```python
def fix_metadata_blocks(lines: list[str]) -> list[str]:
    """Convert consecutive **Label:** lines to list items."""
```

Handles:

```
- **File:** `role.md`
- **Model:** Sonnet

→

- **File:** `role.md`
- **Model:** Sonnet
```

**New function:**

```python
def fix_metadata_list_indentation(lines: list[str]) -> list[str]:
    """Convert metadata labels to list items and indent following lists."""
```

Handles:

```
**Plan Files:**
- item1
- item2

→

- **Plan Files:**
  - item1
  - item2
```

**Key differences:**

- Existing: Consecutive metadata labels with content on same line
- New: Single metadata label (ending with `:**` or `**:`) followed by a list

**Integration:** Both functions run, each handling different patterns.

---

## Requirements

### Pattern Detection

**Metadata label patterns:**

- `**Label:**` (colon inside bold) - no content after
- `**Label**:` (colon outside bold) - no content after

**Following list patterns:**

- Lines starting with `-`, `*`, or `1.`, etc.
- May have existing indentation

### Transformation

1. Convert metadata label to list item: `- **Label:**`
2. Indent following list items by 2 spaces
3. Stop at blank line or non-list content

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
... continue through all 6 cycles
```

---

### Cycle 1: Basic metadata label with following list

**Test:**

```python
def test_fix_metadata_list_indentation_basic_case() -> None:
    """Test: Convert metadata label to list item and indent following list."""
    input_lines = [
        "**Plan Files:**\n",
        "- `plans/phase-1.md`\n",
        "- `plans/phase-2.md`\n",
        "\n",
    ]
    expected = [
        "- **Plan Files:**\n",
        "  - `plans/phase-1.md`\n",
        "  - `plans/phase-2.md`\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

```python
def fix_metadata_list_indentation(lines: list[str]) -> list[str]:
    """Convert metadata labels to list items and indent following lists.

    When a **Label:** or **Label**: line (without content) is followed by
    a list, convert the label to a list item and indent the following list
    by 2 spaces.
    """
    result = []
    i = 0

    # Patterns
    label_pattern = r"^\*\*[^*]+:\*\*\s*$|^\*\*[^*]+\*\*:\s*$"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if this is a metadata label without content
        if re.match(label_pattern, stripped):
            # Check if next line is a list item
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()

                if re.match(r"^[-*]|^\d+\.", next_stripped):
                    # Convert label to list item
                    result.append(f"- {stripped}\n")

                    # Collect and indent following list items
                    j = i + 1
                    while j < len(lines):
                        list_line = lines[j]
                        list_stripped = list_line.strip()

                        # Stop at blank line
                        if list_stripped == "":
                            result.append(list_line)
                            j += 1
                            break

                        # Stop at non-list content
                        if not re.match(r"^[-*]|^\d+\.", list_stripped):
                            break

                        # Indent list item by 2 spaces
                        result.append(f"  {list_stripped}\n")
                        j += 1

                    i = j
                    continue

        result.append(line)
        i += 1

    return result
```

**Verification:** Run test, ensure it passes

---

### Cycle 2: Handle **Label**: pattern (colon outside)

**Test:**

```python
def test_fix_metadata_list_indentation_colon_outside() -> None:
    """Test: Handle **Label**: pattern (colon outside bold)."""
    input_lines = [
        "**Implementation Date**:\n",
        "- 2026-01-04\n",
        "\n",
    ]
    expected = [
        "- **Implementation Date**:\n",
        "  - 2026-01-04\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

- Already handled by pattern: `r"^\*\*[^*]+\*\*:\s*$"`
- Verify regex matches both cases

**Verification:** Run test, ensure it passes

---

### Cycle 3: Don't convert label with content on same line

**Test:**

```python
def test_fix_metadata_list_indentation_skips_label_with_content() -> None:
    """Test: Skip metadata label with content on same line."""
    input_lines = [
        "**File:** `role.md`\n",
        "- item1\n",
        "- item2\n",
    ]
    expected = input_lines.copy()
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

- Pattern already requires line ending with `:**` or `**:` plus optional whitespace
- Verify logic correctly skips lines with content

**Verification:** Run test, ensure it passes

---

### Cycle 4: Handle numbered lists

**Test:**

```python
def test_fix_metadata_list_indentation_handles_numbered_lists() -> None:
    """Test: Indent numbered lists following metadata label."""
    input_lines = [
        "**Steps:**\n",
        "1. First step\n",
        "2. Second step\n",
        "\n",
    ]
    expected = [
        "- **Steps:**\n",
        "  1. First step\n",
        "  2. Second step\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

- Already handled by pattern: `r"^[-*]|^\d+\."`
- Verify numbered lists work correctly

**Verification:** Run test, ensure it passes

---

### Cycle 5: Handle list items with existing indentation

**Test:**

```python
def test_fix_metadata_list_indentation_adds_to_existing_indent() -> None:
    """Test: Add 2 spaces to list items that already have indentation."""
    input_lines = [
        "  **Nested Label:**\n",
        "  - item1\n",
        "    - nested item\n",
        "\n",
    ]
    expected = [
        "  - **Nested Label:**\n",
        "    - item1\n",
        "      - nested item\n",
        "\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

```python
# Updated implementation to handle existing indentation

def fix_metadata_list_indentation(lines: list[str]) -> list[str]:
    """Convert metadata labels to list items and indent following lists."""
    result = []
    i = 0

    label_pattern = r"^\*\*[^*]+:\*\*\s*$|^\*\*[^*]+\*\*:\s*$"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Extract existing indentation
        indent = line[: len(line) - len(line.lstrip())]

        if re.match(label_pattern, stripped):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_stripped = next_line.strip()

                if re.match(r"^[-*]|^\d+\.", next_stripped):
                    # Convert label to list item, preserve indentation
                    result.append(f"{indent}- {stripped}\n")

                    # Collect and indent following list items
                    j = i + 1
                    while j < len(lines):
                        list_line = lines[j]
                        list_stripped = list_line.strip()

                        if list_stripped == "":
                            result.append(list_line)
                            j += 1
                            break

                        if not re.match(r"^[-*]|^\d+\.|^  ", list_stripped):
                            # Not a list item or continuation
                            break

                        # Add 2 spaces to existing indentation
                        list_indent = list_line[: len(list_line) - len(list_line.lstrip())]
                        result.append(f"{list_indent}  {list_stripped}\n")
                        j += 1

                    i = j
                    continue

        result.append(line)
        i += 1

    return result
```

**Verification:** Run test, ensure it passes

---

### Cycle 6: Stop at non-list content

**Test:**

```python
def test_fix_metadata_list_indentation_stops_at_non_list() -> None:
    """Test: Stop indenting at non-list content."""
    input_lines = [
        "**Items:**\n",
        "- item1\n",
        "- item2\n",
        "Regular paragraph\n",
    ]
    expected = [
        "- **Items:**\n",
        "  - item1\n",
        "  - item2\n",
        "Regular paragraph\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

- Already handled by `if not re.match(...)` check
- Verify logic stops at non-list content

**Verification:** Run test, ensure it passes

---

## Integration with Existing `fix_metadata_blocks`

**Scenario: Both patterns in same file**

```python
def test_metadata_list_indentation_works_with_metadata_blocks() -> None:
    """Test: Both fixes work together without conflict."""
    input_lines = [
        "**File:** `role.md`\n",
        "**Model:** Sonnet\n",
        "\n",
        "**Plan Files:**\n",
        "- `plans/phase-1.md`\n",
        "- `plans/phase-2.md`\n",
    ]
    expected = [
        "- **File:** `role.md`\n",
        "- **Model:** Sonnet\n",
        "\n",
        "- **Plan Files:**\n",
        "  - `plans/phase-1.md`\n",
        "  - `plans/phase-2.md`\n",
    ]
    # Process through both fixes
    lines = fix_metadata_blocks(input_lines)
    lines = fix_metadata_list_indentation(lines)
    assert lines == expected
```

**Verification:**

- `fix_metadata_blocks` converts first two lines to list
- `fix_metadata_list_indentation` handles the label + list pattern
- No conflicts

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
    lines = fix_metadata_list_indentation(lines)  # NEW: Before numbered_list_spacing
    lines = fix_numbered_list_spacing(lines)
    lines = fix_markdown_code_blocks(lines)
    return lines
```

**Order rationale:**

- After `fix_nested_lists` (converts a/b/c to numbers)
- Before `fix_numbered_list_spacing` (handles spacing around numbered lists)
- Before `fix_markdown_code_blocks` (line-based before block-based)

---

## Validation

**Run all tests:**

```bash
just test tests/test_markdown.py::test_fix_metadata_list_indentation*
```

**Verify integration:**

```bash
just test tests/test_markdown.py::test_metadata_list_indentation_works_with_metadata_blocks
```

**Verify no regressions:**

```bash
just test tests/test_markdown.py
```

---

## Edge Cases

### Label followed by blank line then list

**Test:**

```python
def test_fix_metadata_list_indentation_skips_if_blank_line_between() -> None:
    """Test: Don't convert if blank line between label and list."""
    input_lines = [
        "**Items:**\n",
        "\n",
        "- item1\n",
    ]
    expected = input_lines.copy()
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

- Check `i + 1` is a list item (not blank)
- Already handled by checking `next_line` directly

---

### Multiple metadata labels with lists

**Test:**

```python
def test_fix_metadata_list_indentation_handles_multiple_labels() -> None:
    """Test: Handle multiple metadata labels with lists."""
    input_lines = [
        "**Files:**\n",
        "- file1\n",
        "- file2\n",
        "\n",
        "**Steps:**\n",
        "1. step1\n",
        "2. step2\n",
    ]
    expected = [
        "- **Files:**\n",
        "  - file1\n",
        "  - file2\n",
        "\n",
        "- **Steps:**\n",
        "  1. step1\n",
        "  2. step2\n",
    ]
    assert fix_metadata_list_indentation(input_lines) == expected
```

**Implementation:**

- Already handled by while loop
- Verify multiple occurrences work

---

## Notes

- Complement existing `fix_metadata_blocks` - handle different patterns
- Add 2 spaces indentation (standard markdown nested list)
- Preserve existing indentation + add 2 spaces
- Stop at blank lines or non-list content
- Handle both `:**` and `**:` patterns
