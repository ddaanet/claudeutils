"""Tests for markdown module."""

from pathlib import Path

import pytest

from claudeutils.exceptions import MarkdownInnerFenceError
from claudeutils.markdown import (
    escape_inline_backticks,
    fix_backtick_spaces,
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
    """Test: 2+ consecutive metadata labels trigger list conversion and indentation.

    When 2+ consecutive **Label:** lines appear (with space after colon),
    they form a metadata list and following numbered list is indented.
    """
    input_lines = [
        "**Label:** content\n",
        "**Execution phase:**\n",
        "4. Batch reads\n",
    ]
    expected = [
        "- **Label:** content\n",
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


def test_escape_inline_backticks_preserves_four_backticks() -> None:
    """Test: Four backticks in text are wrapped correctly."""
    input_lines = [
        "Output: ```` markdown block\n",
    ]
    expected = [
        "Output: `` ```` `` markdown block\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_preserves_five_backticks() -> None:
    """Test: Five backticks in text are wrapped correctly."""
    input_lines = [
        "Use ````` for special cases\n",
    ]
    expected = [
        "Use `` ````` `` for special cases\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_handles_mixed_backtick_counts() -> None:
    """Test: Text with both triple and quad backticks handled correctly."""
    input_lines = [
        "Use ``` for code and ```` for edge cases\n",
    ]
    expected = [
        "Use `` ``` `` for code and `` ```` `` for edge cases\n",
    ]
    assert escape_inline_backticks(input_lines) == expected


def test_escape_inline_backticks_four_backticks_idempotent() -> None:
    """Test: Escape backticks is idempotent with mixed 4-backtick and 3-backtick inline.

    Regression test for bug where having both ````markdown and ``` on the same
    line would cause non-idempotent behavior on second pass.
    """
    input_lines = [
        "Use a ````markdown block to include ``` blocks.\n",
    ]

    # First run - should wrap both sequences
    result1 = escape_inline_backticks(input_lines)
    expected_first = [
        "Use a `` ````markdown `` block to include `` ``` `` blocks.\n",
    ]
    assert result1 == expected_first, (
        f"First pass incorrect:\nGot: {result1}\nExpected: {expected_first}"
    )

    # Second run should produce identical result (must be idempotent)
    result2 = escape_inline_backticks(result1)
    assert result1 == result2, f"Not idempotent:\nPass 1: {result1}\nPass 2: {result2}"


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
    """Test: 2+ labels converted and following list indented, single label not converted."""
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
        "**Plan Files:**\n",
        "- `plans/phase-1.md`\n",
        "- `plans/phase-2.md`\n",
    ]
    lines = fix_metadata_blocks(input_lines)
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


def test_fix_backtick_spaces_quotes_trailing_space() -> None:
    """Test 13: Quote backticks with trailing space.

    When inline code has trailing whitespace, it's ambiguous in documentation.
    Quote the content to make the space explicit.
    """
    input_line = "`blah ` text\n"
    expected = '`"blah "` text\n'
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_quotes_leading_space() -> None:
    """Test 14: Quote backticks with leading space.

    When inline code has leading whitespace, quote it to make it explicit.
    """
    input_line = "` blah` text\n"
    expected = '`" blah"` text\n'
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_quotes_both_spaces() -> None:
    """Test 15: Quote backticks with both leading and trailing space.

    When inline code has both leading and trailing whitespace, quote both.
    """
    input_line = "` | ` text\n"
    expected = '`" | "` text\n'
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_skips_code_without_spaces() -> None:
    """Test 16: Skip backticks without leading/trailing spaces.

    Backticks without whitespace should remain unchanged.
    """
    input_line = "`code` text\n"
    expected = "`code` text\n"
    result = fix_backtick_spaces([input_line])
    assert result == [expected]


def test_fix_backtick_spaces_via_segment_processing() -> None:
    """Test 17: Apply via segment-aware processing.

    When content is mixed (plain text + ```python block):
    - Plain text backticks with spaces should be quoted
    - Content inside ```python block should be unchanged
    """
    input_lines = [
        "This code ` has spaces ` in it.\n",
        "\n",
        "```python\n",
        "# This ` has spaces ` but should not be quoted\n",
        "text = '` also ` spaces'\n",
        "```\n",
    ]
    expected = [
        'This code `" has spaces "` in it.\n',
        "\n",
        "```python\n",
        "# This ` has spaces ` but should not be quoted\n",
        "text = '` also ` spaces'\n",
        "```\n",
    ]
    result = process_lines(input_lines)
    assert result == expected


def test_inner_fence_detection_in_python_block() -> None:
    """Test 18: Inner fence detection still works after segment changes.

    Verify that `fix_markdown_code_blocks` still detects and errors on
    inner fences in non-markdown blocks (unchanged behavior).
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

    with pytest.raises(
        MarkdownInnerFenceError, match="Inner fence detected in non-markdown block"
    ):
        process_lines(input_lines)


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


def test_fix_warning_lines_skips_table_rows() -> None:
    """Test: Tables should not be converted to lists by fix_warning_lines."""
    input_lines = [
        "| Header 1 | Header 2 |\n",
        "| -------- | -------- |\n",
        "| Value 1  | Value 2  |\n",
        "\n",
    ]
    result = fix_warning_lines(input_lines)
    assert result == input_lines


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


def test_escape_inline_backticks_preserves_single_backtick_spans() -> None:
    """Test: Single backtick spans not corrupted by escaping."""
    input_lines = ["Single `backtick` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Single `backtick` text\n"]


def test_escape_inline_backticks_preserves_double_backtick_spans() -> None:
    """Test: Double backtick spans not corrupted by escaping."""
    input_lines = ["Double ``backtick`` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Double ``backtick`` text\n"]


def test_escape_inline_backticks_preserves_double_containing_single() -> None:
    """Test: Double backtick spans containing single backtick preserved."""
    input_lines = ["Double ``Backtick ` char`` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Double ``Backtick ` char`` text\n"]


def test_escape_inline_backticks_preserves_multiple_spans() -> None:
    """Test: Multiple inline code spans on same line preserved."""
    input_lines = ["First `span1` and second `span2` here\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["First `span1` and second `span2` here\n"]


def test_escape_inline_backticks_preserves_mixed_delimiters() -> None:
    """Test: Mixed single and double backtick spans preserved."""
    input_lines = ["Single `a` and double ``b`` text\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Single `a` and double ``b`` text\n"]


def test_escape_inline_backticks_escapes_bare_triple_outside_spans() -> None:
    """Test: Bare triple backticks outside spans are escaped."""
    input_lines = ["Text with ```python outside\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Text with `` ```python `` outside\n"]


def test_escape_inline_backticks_mixed_bare_and_inline() -> None:
    """Test: Escapes bare fences but preserves inline code spans."""
    input_lines = ["Use `code` but escape ```python here\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Use `code` but escape `` ```python `` here\n"]


def test_escape_inline_backticks_preserves_quoted_doc_example() -> None:
    """Test: Documentation example with inline code preserved."""
    input_lines = ['Given: `"````markdown\\n"` (4 backticks with language)\n']
    result = escape_inline_backticks(input_lines)
    # Single-backtick span containing 4 backticks and text - preserved
    assert result == ['Given: `"````markdown\\n"` (4 backticks with language)\n']


def test_escape_inline_backticks_adjacent_spans() -> None:
    """Test: Adjacent inline code spans handled correctly."""
    input_lines = ["`first``second`text\n"]
    result = escape_inline_backticks(input_lines)
    # `first` is valid span, ``second` has mismatched delimiters (2 opening, 1 closing)
    # Should preserve the valid `first` span
    assert "`first`" in result[0]


def test_escape_inline_backticks_empty_span() -> None:
    """Test: Empty inline code spans preserved."""
    input_lines = ["Empty `` span\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["Empty `` span\n"]


def test_escape_inline_backticks_span_at_boundaries() -> None:
    """Test: Spans at start/end of line preserved."""
    input_lines = ["`start` middle `end`\n"]
    result = escape_inline_backticks(input_lines)
    assert result == ["`start` middle `end`\n"]


def test_escape_inline_backticks_unclosed_not_corrupted() -> None:
    """Test: Unclosed backticks handled gracefully."""
    input_lines = ["Unclosed `backtick and ```python\n"]
    result = escape_inline_backticks(input_lines)
    # Unclosed ` is not a span, so ```python should be escaped
    assert "`` ```python ``" in result[0]


def test_escape_inline_backticks_preserves_one_four_one_with_spaces() -> None:
    """Test: Explicit single-backtick span with four backticks inside."""
    input_lines = ["Use ` ```` ` for blocks\n"]
    result = escape_inline_backticks(input_lines)
    # Single-backtick span with spaces - should be preserved
    assert result == ["Use ` ```` ` for blocks\n"]
