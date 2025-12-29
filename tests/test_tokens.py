"""Unit tests for token counting functionality."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from claudeutils.tokens import count_tokens_for_file


class TestCountTokensForFile:
    """Tests for count_tokens_for_file function."""

    def test_count_tokens_for_simple_text(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Count tokens for a simple text file.

        Given: File with content "Hello world", model="sonnet"
        When: count_tokens_for_file(path, model) called
        Then: Returns integer token count > 0
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.input_tokens = 5
        mock_client.messages.count_tokens.return_value = mock_response

        # Patch the Anthropic client initialization
        monkeypatch.setattr(
            "claudeutils.tokens.Anthropic",
            Mock(return_value=mock_client),
        )

        # Call function
        result = count_tokens_for_file(test_file, "sonnet")

        # Verify
        assert isinstance(result, int)
        assert result > 0
        assert result == 5

    def test_count_tokens_for_markdown_with_code_blocks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Count tokens for markdown file with code blocks.

        Given: File with markdown content including code block, model="opus"
        When: count_tokens_for_file(path, model) called
        Then: Returns token count reflecting full content
        """
        # Create test file with markdown and code block
        test_file = tmp_path / "test.md"
        content = """# Title

Some text here.

```python
def hello():
    print("world")
```

More text."""
        test_file.write_text(content)

        # Mock Anthropic client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.input_tokens = 42
        mock_client.messages.count_tokens.return_value = mock_response

        # Patch the Anthropic client initialization
        monkeypatch.setattr(
            "claudeutils.tokens.Anthropic",
            Mock(return_value=mock_client),
        )

        # Call function
        result = count_tokens_for_file(test_file, "opus")

        # Verify
        assert isinstance(result, int)
        assert result == 42

    def test_handle_empty_file(self, tmp_path: Path) -> None:
        """Handle empty files without API call.

        Given: Empty file, model="haiku"
        When: count_tokens_for_file(path, model) called
        Then: Returns 0
        """
        # Create empty test file
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        # Call function
        result = count_tokens_for_file(test_file, "haiku")

        assert result == 0
