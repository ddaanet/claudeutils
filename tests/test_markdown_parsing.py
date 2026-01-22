"""Tests for markdown module."""

from claudeutils.markdown import (
    fix_warning_lines,
    process_lines,
)


def test_segment_aware_processing_applies_fix_to_plain_text() -> None:
    """Test 9: Fix applies to plain text, skips protected blocks.

    When content is mixed (plain text + ```python block):
    - Plain text with metadata should be converted to lists
    - Content inside ```python block should be unchanged
    """
    input_lines = [
        "**File:** test.py\n",
        "**Model:** Sonnet\n",
        "\n",
        "```python\n",
        "config = {\n",
        '    "name": "test",\n',
        '    "version": "1.0"\n',
        "}\n",
        "```\n",
    ]
    expected = [
        "- **File:** test.py\n",
        "- **Model:** Sonnet\n",
        "\n",
        "```python\n",
        "config = {\n",
        '    "name": "test",\n',
        '    "version": "1.0"\n',
        "}\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_segment_aware_processing_skips_yaml_prolog() -> None:
    """Test 10: YAML prolog block content is completely unchanged.

    YAML prologs contain structured data that should not be processed.
    All fixes must skip content inside ---...--- prolog sections.
    """
    input_lines = [
        "---\n",
        "title: Document\n",
        "tasks: [ build, test ]\n",
        "---\n",
        "\n",
        "**File:** result.md\n",
        "**Model:** Sonnet\n",
    ]
    expected = [
        "---\n",
        "title: Document\n",
        "tasks: [ build, test ]\n",
        "---\n",
        "\n",
        "- **File:** result.md\n",
        "- **Model:** Sonnet\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_segment_aware_processing_skips_bare_fence_blocks() -> None:
    """Test 11: Bare ``` block content is completely unchanged.

    Bare code blocks (no language) should not have fixes applied.
    This prevents false positives from colon/bracket-prefixed content.
    """
    input_lines = [
        "```\n",
        "NOTE: Important\n",
        "TODO: Action item\n",
        "```\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_segment_aware_processing_skips_nested_markdown_in_python() -> None:
    """Test 12: Content in non-markdown blocks is fully protected.

    When content appears inside ```python block,
    all processing-sensitive patterns are protected.
    This prevents false positives from pipes, colons, and other patterns.
    """
    input_lines = [
        "```python\n",
        "config = {\n",
        "    # Table format example:\n",
        "    # | Column | Value |\n",
        "    # | ------ | ----- |\n",
        "    # | Build  | Done  |\n",
        "    # | Test   | Pass  |\n",
        "    'name': 'test'\n",
        "}\n",
        "```\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_inner_fence_in_python_block_passed_through() -> None:
    """Test 18: Inner fence in non-markdown block is upgraded to 4 backticks.

    Verify that `process_lines` fixes inner fences in non-markdown blocks
    by upgrading to 4 backticks (typical Claude output discussing code blocks).
    """
    input_lines = [
        "```python\n",
        "def foo():\n",
        '    """\n',
        "    Example:\n",
        "    ```\n",
        "    code\n",
        "    ```\n",
        '    """\n',
        "```\n",
    ]
    expected = [
        "````python\n",
        "def foo():\n",
        '    """\n',
        "    Example:\n",
        "    ```\n",
        "    code\n",
        "    ```\n",
        '    """\n',
        "````\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_inner_fence_detection_in_markdown_block() -> None:
    """Test 19: Inner fence detection in ```markdown block.

    Verify that markdown blocks with inner fences still nest correctly
    (converts outer fence from ``` to ````).
    """
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
    result = process_lines(input_lines)
    assert result == expected


def test_single_bold_label_not_converted_to_list() -> None:
    """Test: Single **Label:** line should NOT be converted to list item.

    User requirement: Single label line ≠ metadata list.
    Only 2+ consecutive labels are converted.
    """
    input_lines = [
        "**Commits:**\n",
        "- item 1\n",
        "\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_yaml_prolog_recognizes_keys_without_spaces() -> None:
    r"""Test: YAML prolog keys without trailing spaces are recognized.

    Phase 4: Fix YAML Prolog Detection
    Bug: Pattern r"^\w+:\s" requires space after colon
    Fix: Pattern r"^[a-zA-Z_][\w-]*:" allows keys without values

    Verify that nested YAML keys like "tier_structure:" and "critical:"
    (with no trailing space) are recognized as valid YAML prolog content.
    """
    input_lines = [
        "---\n",
        "tier_structure:\n",
        "  critical:\n",
        "    - item\n",
        "---\n",
        "Content here\n",
    ]
    # YAML prolog should not be processed by fix_warning_lines
    # So the keys should NOT be converted to list items
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_yaml_prolog_recognizes_keys_with_hyphens() -> None:
    """Test: YAML prolog keys with hyphens are recognized.

    Pattern should support keys like "author-model:", "semantic-type:"
    """
    input_lines = [
        "---\n",
        "author-model: claude-3-5-sonnet\n",
        "semantic-type: configuration\n",
        "---\n",
        "Content\n",
    ]
    expected = input_lines.copy()
    result = process_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_regular_prose() -> None:
    r"""Test: Regular prose should NOT be converted to list items.

    Phase 5: Rewrite extract_prefix()
    Bug: Pattern r"^(\S+(?:\s|:))" matches regular text like "Task agent"
    Fix: Only match emojis, brackets, and uppercase word+colon

    Lines starting with regular words should NOT be converted to lists,
    even if they appear in pairs.
    """
    input_lines = [
        "Task agent prompt is a replacement.\n",
        "Task agent are interactive-only.\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_block_quotes() -> None:
    """Test: Block quotes should NOT be converted to lists.

    Lines starting with > should be protected.
    """
    input_lines = [
        "> Your subagent's system prompt goes here.\n",
        "> This can be multiple paragraphs.\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_tree_diagrams() -> None:
    """Test: Tree diagram symbols should NOT be converted to lists.

    Lines with tree branch symbols (├, └, │) should be protected.
    """
    input_lines = [
        "  ├─ fix_dunder_references\n",
        "  ├─ fix_metadata_blocks\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_preserves_uppercase_colon_prefixes() -> None:
    """Test: Uppercase word + colon prefixes (NOTE:, WARNING:) are still detected.

    These legitimate prefixes should still convert to lists when 2+.
    """
    input_lines = [
        "NOTE: This is important\n",
        "NOTE: Another note\n",
    ]
    expected = [
        "- NOTE: This is important\n",
        "- NOTE: Another note\n",
    ]
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_prefix_detection_excludes_lowercase_colon_prefixes() -> None:
    """Test: Lowercase word + colon should NOT be converted.

    Only UPPERCASE word + colon are valid prefixes (NOTE:, WARNING:, etc.)
    Lowercase like "Implementation:" should not be treated as prefix.
    """
    input_lines = [
        "Implementation: Start here\n",
        "Implementation: Then that\n",
    ]
    expected = input_lines.copy()
    result = fix_warning_lines(input_lines)
    assert result == expected


def test_integration_python_fence_protection() -> None:
    """Integration: Content in ```python fences is protected."""
    input_lines = [
        "Here is ```python code:\n",
        "\n",
        "```python\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
        "```\n",
        "\n",
        "After the fence.\n",
    ]
    result = process_lines(input_lines)
    # Python fence content should NOT be converted to list items
    assert result[3] == "✅ Task 1\n"
    assert result[4] == "✅ Task 2\n"


def test_integration_yaml_fence_protection() -> None:
    """Integration: Content in ```yaml fences is protected."""
    input_lines = [
        "Configuration:\n",
        "\n",
        "```yaml\n",
        "✅ Check: true\n",
        "❌ Status: false\n",
        "```\n",
        "\n",
        "End of config.\n",
    ]
    result = process_lines(input_lines)
    # YAML fence content should NOT be converted to list items
    assert result[3] == "✅ Check: true\n"
    assert result[4] == "❌ Status: false\n"


def test_integration_markdown_fence_processing() -> None:
    """Integration: Content in ```markdown fences IS processed (intentional).

    Markdown blocks are processable=True to allow formatting doc examples.
    """
    input_lines = [
        "Example markdown:\n",
        "\n",
        "```markdown\n",
        "**File:** role.md\n",
        "**Model:** Sonnet\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    # Markdown fence content IS processed (intentional - for doc examples)
    assert result[3] == "- **File:** role.md\n"
    assert result[4] == "- **Model:** Sonnet\n"


def test_integration_bare_fence_protection() -> None:
    """Integration: Content in bare ``` fences is protected."""
    input_lines = [
        "Some code:\n",
        "\n",
        "```\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    # Bare fence content should NOT be converted to list items
    assert result[3] == "✅ Task 1\n"
    assert result[4] == "✅ Task 2\n"


def test_integration_yaml_prolog_protection() -> None:
    """Integration: YAML prologs are protected and not processed."""
    input_lines = [
        "---\n",
        "author_model: claude-sonnet\n",
        "semantic_type: guide\n",
        "---\n",
        "\n",
        "Content starts here.\n",
    ]
    result = process_lines(input_lines)
    # YAML prolog should remain unchanged
    assert result[0] == "---\n"
    assert result[1] == "author_model: claude-sonnet\n"
    assert result[2] == "semantic_type: guide\n"
    assert result[3] == "---\n"


def test_integration_plain_text_still_processes() -> None:
    """Integration: Plain text (not in fences) is still processed correctly."""
    input_lines = [
        "Some content\n",
        "\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
    ]
    result = process_lines(input_lines)
    # Plain text emoji lines SHOULD be converted to list items
    assert result[2] == "- ✅ Task 1\n"
    assert result[3] == "- ✅ Task 2\n"


def test_nested_python_block_in_markdown_no_blank_line() -> None:
    """Test: Nested ```python block inside ```markdown doesn't get blank line.

    When ```python block appears inside ```markdown block, fix_markdown_code_blocks
    should NOT insert a blank line after the ```python fence (Bug #2 regression test).
    Requires recursive parsing to work correctly.
    """
    input_lines = [
        "````markdown\n",
        "# Example\n",
        "\n",
        "```python\n",
        "code_here\n",
        "```\n",
        "\n",
        "````\n",
    ]

    # Process the lines
    result = process_lines(input_lines)

    # Find the ```python fence in the output
    python_fence_idx = None
    for i, line in enumerate(result):
        if line.strip() == "```python":
            python_fence_idx = i
            break

    assert python_fence_idx is not None, "```python fence not found"

    # Verify next line is NOT blank (Bug #2 would insert a blank line here)
    assert python_fence_idx + 1 < len(result), "No line after python fence"
    next_line = result[python_fence_idx + 1]
    assert next_line.strip() != "", (
        f"Unexpected blank line after ```python fence: {next_line!r}"
    )
    assert next_line == "code_here\n", f"Expected code line, got: {next_line!r}"


def test_integration_nested_fences_in_markdown_block() -> None:
    """Integration test: Bare ``` fence inside ````markdown block.

    Tests Bug #1 fix: Bare ``` fences inside ````markdown blocks should be
    protected from processing. Emoji lines inside the bare fence should NOT
    be converted to list items.
    """
    input_lines = [
        "````markdown\n",
        "## Markdown Cleanup Examples\n",
        "\n",
        "### Checklist Detection\n",
        "\n",
        "**Input:**\n",
        "\n",
        "```\n",
        "✅ Issue #1: XPASS tests visible\n",
        "✅ Issue #2: Setup failures captured\n",
        "❌ Issue #3: Not fixed yet\n",
        "```\n",
        "\n",
        "````\n",
    ]

    result = process_lines(input_lines)

    # Find the bare fence content
    bare_fence_start = None
    bare_fence_end = None
    for i, line in enumerate(result):
        stripped = line.strip()
        if stripped == "```":
            if bare_fence_start is None:
                bare_fence_start = i
            else:
                bare_fence_end = i
                break

    assert bare_fence_start is not None, "Opening bare fence not found"
    assert bare_fence_end is not None, "Closing bare fence not found"

    # Verify emoji lines inside bare fence were NOT converted to list items
    content_inside_fence = result[bare_fence_start + 1 : bare_fence_end]
    assert len(content_inside_fence) == 3, (
        f"Expected 3 lines, got {len(content_inside_fence)}"
    )

    # These lines should be unchanged (not prefixed with "- ")
    assert content_inside_fence[0] == "✅ Issue #1: XPASS tests visible\n"
    assert content_inside_fence[1] == "✅ Issue #2: Setup failures captured\n"
    assert content_inside_fence[2] == "❌ Issue #3: Not fixed yet\n"


# Integration tests for inline code span protection
