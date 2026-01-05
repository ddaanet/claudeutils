"""Tests for markdown module."""

from pathlib import Path

import pytest

from claudeutils.exceptions import MarkdownInnerFenceError
from claudeutils.markdown import (
    escape_inline_backticks,
    fix_markdown_code_blocks,
    fix_metadata_blocks,
    fix_metadata_list_indentation,
    fix_warning_lines,
    process_file,
    process_lines,
)


def test_import_process_lines() -> None:
    """Test: Import process_lines function."""
    assert callable(process_lines)


def test_process_lines_fixes_dunder_references() -> None:
    """Test: process_lines fixes dunder references."""
    input_lines = ["## About __init__.py\n"]
    expected = ["## About `__init__.py`\n"]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_metadata_blocks() -> None:
    """Test: process_lines fixes metadata blocks."""
    input_lines = [
        "**File:** `role.md`\n",
        "**Model:** Sonnet\n",
        "\n",
    ]
    expected = [
        "- **File:** `role.md`\n",
        "- **Model:** Sonnet\n",
        "\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_warning_lines() -> None:
    """Test: process_lines fixes warning lines."""
    input_lines = [
        "⚠️ Warning one\n",
        "⚠️ Warning two\n",
    ]
    expected = [
        "- ⚠️ Warning one\n",
        "- ⚠️ Warning two\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_nested_lists() -> None:
    """Test: process_lines fixes nested lists."""
    input_lines = [
        "2. Parent:\n",
        "   a. Child 1\n",
        "   b. Child 2\n",
    ]
    expected = [
        "2. Parent:\n",
        "   1. Child 1\n",
        "   2. Child 2\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_lines_fixes_numbered_list_spacing() -> None:
    """Test: process_lines fixes numbered list spacing."""
    input_lines = [
        "**Execution phase:**\n",
        "4. Batch reads\n",
    ]
    expected = [
        "- **Execution phase:**\n",
        "  4. Batch reads\n",
    ]
    assert process_lines(input_lines) == expected


def test_process_file_returns_true_when_modified(tmp_path: Path) -> None:
    """Test: process_file returns True when modified."""
    content = "## About __init__.py\n"
    filepath = tmp_path / "test.md"
    filepath.write_text(content)

    result = process_file(filepath)
    assert result is True
    assert filepath.read_text() == "## About `__init__.py`\n"


def test_process_file_returns_false_when_unchanged(tmp_path: Path) -> None:
    """Test: process_file returns False when unchanged."""
    content = "## About `__init__.py`\n"
    filepath = tmp_path / "test.md"
    filepath.write_text(content)

    result = process_file(filepath)
    assert result is False
    assert filepath.read_text() == content


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


def test_fix_warning_lines_skips_existing_lists() -> None:
    """Test: fix_warning_lines skips lines already formatted as lists."""
    input_lines = [
        "- ✅ Issue #1: Already a list\n",
        "- ✅ Issue #2: Already a list\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_skips_single_line() -> None:
    """Test: fix_warning_lines skips single line with emoji prefix."""
    input_lines = [
        "✅ Only one line\n",
        "\n",
        "Some other content\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected


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


def test_fix_markdown_code_blocks_errors_on_inner_fence_in_python() -> None:
    """Test: Error when ```python block contains inner fence."""
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

    with pytest.raises(
        MarkdownInnerFenceError, match="Inner fence detected in non-markdown block"
    ):
        fix_markdown_code_blocks(input_lines)


def test_escape_inline_backticks_wraps_language_references() -> None:
    """Test: Escape ```language when it appears inline in text."""
    input_lines = [
        "Text about ```markdown blocks\n",
        "\n",
        "More text with ```python and ```javascript references\n",
    ]
    expected = [
        "Text about `` ```markdown `` blocks\n",
        "\n",
        "More text with `` ```python `` and `` ```javascript `` references\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_wraps_standalone_triple_backticks() -> None:
    """Test: Escape ``` without language when it appears inline."""
    input_lines = [
        "Text mentioning ``` fences\n",
        "\n",
        "Use ``` to create code blocks\n",
    ]
    expected = [
        "Text mentioning `` ``` `` fences\n",
        "\n",
        "Use `` ``` `` to create code blocks\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_preserves_real_fences() -> None:
    """Test: Don't escape ``` when it's a real fence at line start."""
    input_lines = [
        "```bash\n",
        "echo hello\n",
        "```\n",
    ]
    # Should not modify - these are real fences
    assert escape_inline_backticks(input_lines) == input_lines


def test_escape_inline_backticks_is_idempotent() -> None:
    """Test: Running escape multiple times produces the same result."""
    input_lines = [
        "Text about ```markdown blocks\n",
        "\n",
        "Use ``` to create code blocks\n",
        "More text with ```python and ```javascript references\n",
    ]

    # First run
    result1 = escape_inline_backticks(input_lines)

    # Second run should produce identical result
    result2 = escape_inline_backticks(result1)

    assert result1 == result2


def test_escape_inline_backticks_skips_content_inside_blocks() -> None:
    """Test: Don't escape ``` inside code blocks."""
    input_lines = [
        "Text with ```python reference\n",
        "\n",
        "```markdown\n",
        "Example showing ```bash usage\n",
        "```\n",
        "\n",
        "More ```javascript outside\n",
    ]
    expected = [
        "Text with `` ```python `` reference\n",
        "\n",
        "```markdown\n",
        "Example showing ```bash usage\n",
        "```\n",
        "\n",
        "More `` ```javascript `` outside\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_fix_markdown_code_blocks_ignores_inline_backticks() -> None:
    """Test: Don't detect ``` as fence when it appears inline in text."""
    input_lines = [
        "Text about `` ```markdown `` blocks\n",
        "\n",
        "```bash\n",
        "echo hello\n",
        "```\n",
        "\n",
        "More text with `` ```python `` and `` ```javascript `` references\n",
    ]
    # Should not raise an error or modify the content
    assert fix_markdown_code_blocks(input_lines) == input_lines


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


def test_fix_metadata_list_indentation_skips_label_with_content() -> None:
    """Test: Skip metadata label with content on same line."""
    input_lines = [
        "**File:** `role.md`\n",
        "- item1\n",
        "- item2\n",
    ]
    expected = input_lines.copy()
    assert fix_metadata_list_indentation(input_lines) == expected


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


def test_process_lines_is_idempotent() -> None:
    """Test: Running process_lines multiple times produces the same result."""
    input_lines = [
        "## About __init__.py\n",
        "\n",
        "Text mentioning ```python and ```bash code.\n",
        "\n",
        "**File:** test.py\n",
        "**Model:** Sonnet\n",
        "\n",
        "```bash\n",
        "echo hello\n",
        "```\n",
    ]

    # First run
    result1 = process_lines(input_lines)

    # Second run
    result2 = process_lines(result1)

    # Should be identical (idempotent)
    assert result1 == result2


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
    lines = fix_metadata_blocks(input_lines)
    lines = fix_metadata_list_indentation(lines)
    assert lines == expected


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
