"""Tests for markdown module."""

from pathlib import Path

from claudeutils.markdown import process_file, process_lines


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
        "**Execution phase:**\n",
        "\n",
        "4. Batch reads\n",
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
    from claudeutils.markdown import fix_warning_lines
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
    from claudeutils.markdown import fix_warning_lines
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
    from claudeutils.markdown import fix_warning_lines
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
    from claudeutils.markdown import fix_warning_lines
    input_lines = [
        "- ✅ Issue #1: Already a list\n",
        "- ✅ Issue #2: Already a list\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_skips_single_line() -> None:
    """Test: fix_warning_lines skips single line with emoji prefix."""
    from claudeutils.markdown import fix_warning_lines
    input_lines = [
        "✅ Only one line\n",
        "\n",
        "Some other content\n",
    ]
    expected = input_lines.copy()
    assert fix_warning_lines(input_lines) == expected


def test_fix_warning_lines_handles_bracket_and_colon_prefix() -> None:
    """Test: fix_warning_lines handles [TODO] and NOTE: patterns."""
    from claudeutils.markdown import fix_warning_lines
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
    from claudeutils.markdown import fix_markdown_code_blocks
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
    from claudeutils.markdown import fix_markdown_code_blocks
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
    import pytest
    from claudeutils.markdown import fix_markdown_code_blocks
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


def test_fix_markdown_code_blocks_handles_multiple_blocks() -> None:
    """Test: Handle multiple ```markdown blocks correctly."""
    from claudeutils.markdown import fix_markdown_code_blocks
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
