"""Tests for segment parsing functionality."""

from claudeutils.markdown import parse_segments


def test_parse_segments_empty_input() -> None:
    """Test: parse_segments returns empty list for empty input."""
    assert parse_segments([]) == []


def test_parse_segments_plain_text_no_fences() -> None:
    """Test: parse_segments returns single processable segment for plain text."""
    lines = ["Line 1\n", "Line 2\n"]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True
    assert result[0].lines == lines


def test_parse_segments_python_block() -> None:
    """Test: parse_segments detects ```python block as protected."""
    lines = [
        "```python\n",
        "x = 1\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is False
    assert result[0].language == "python"


def test_parse_segments_markdown_block() -> None:
    """Test: parse_segments detects ```markdown block as processable."""
    lines = [
        "```markdown\n",
        "# Title\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True
    assert result[0].language == "markdown"


def test_parse_segments_bare_fence_block() -> None:
    """Test: parse_segments detects bare ``` block as protected."""
    lines = [
        "```\n",
        "raw text\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is False
    assert result[0].language is None


def test_parse_segments_text_before_and_after_fence() -> None:
    """Test: parse_segments returns 3 segments for text-fence-text."""
    lines = [
        "Text before\n",
        "```python\n",
        "code\n",
        "```\n",
        "Text after\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 3
    assert result[0].processable is True
    assert result[0].lines == ["Text before\n"]
    assert result[1].processable is False
    assert result[1].language == "python"
    assert result[2].processable is True
    assert result[2].lines == ["Text after\n"]


def test_parse_segments_consecutive_fenced_blocks() -> None:
    """Test: parse_segments handles consecutive fenced blocks."""
    lines = [
        "```bash\n",
        "echo hello\n",
        "```\n",
        "```python\n",
        "x = 1\n",
        "```\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 2
    assert result[0].processable is False
    assert result[0].language == "bash"
    assert result[1].processable is False
    assert result[1].language == "python"


def test_parse_segments_nested_markdown_inside_python() -> None:
    """Test: Nested ```markdown inside ```python is NOT processable."""
    lines = [
        "```python\n",
        "# docstring with example:\n",
        "```markdown\n",
        "# Title\n",
        "```\n",
        "```\n",  # closes python block
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is False
    assert result[0].language == "python"


def test_parse_segments_yaml_prolog() -> None:
    """Test: YAML prolog section is detected as protected."""
    lines = [
        "---\n",
        "title: Test Document\n",
        "author: Claude\n",
        "---\n",
        "\n",
        "Content here\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 2
    assert result[0].processable is False
    assert result[0].language == "yaml-prolog"
    assert result[0].lines == lines[:4]
    assert result[1].processable is True
    assert result[1].lines == ["\n", "Content here\n"]


def test_parse_segments_yaml_prolog_not_ruler() -> None:
    """Test: --- with blank lines INSIDE is NOT a prolog (it's a ruler)."""
    lines = [
        "Content above\n",
        "\n",
        "---\n",
        "\n",
        "Content below\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True
    assert result[0].lines == lines


def test_parse_segments_yaml_prolog_must_have_key_value() -> None:
    """Test: --- section without key: value is NOT a prolog."""
    lines = [
        "---\n",
        "just some text\n",
        "no colons here\n",
        "---\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 1
    assert result[0].processable is True


def test_parse_segments_yaml_prolog_mid_document() -> None:
    """Test: YAML prolog can appear mid-document after markdown content."""
    lines = [
        "# Previous content\n",
        "\n",
        "Some text here\n",
        "---\n",
        "stage: production\n",
        "version: 2.0\n",
        "---\n",
        "Content after\n",
    ]
    result = parse_segments(lines)
    assert len(result) == 3
    assert result[0].processable is True
    assert result[0].lines == lines[:3]
    assert result[1].processable is False
    assert result[1].language == "yaml-prolog"
    assert result[1].lines == lines[3:7]
    assert result[2].processable is True
    assert result[2].lines == ["Content after\n"]
