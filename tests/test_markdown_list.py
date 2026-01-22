"""Tests for markdown module."""

from claudeutils.markdown import (
    fix_metadata_blocks,
    fix_metadata_list_indentation,
    fix_warning_lines,
)


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
