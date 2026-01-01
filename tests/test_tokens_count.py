"""Unit tests for count_tokens_for_file function."""

from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import APIError, AuthenticationError, RateLimitError

from claudeutils.exceptions import (
    ApiAuthenticationError,
    ApiError,
    ApiRateLimitError,
    FileReadError,
)
from claudeutils.tokens import (
    ModelId,
    TokenCount,
    calculate_total,
    count_tokens_for_file,
    count_tokens_for_files,
)


class TestCountTokensForFile:
    """Tests for count_tokens_for_file function."""

    def test_count_tokens_for_simple_text(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Count tokens for a simple text file.

        Given: File with content "Hello world", model="sonnet", mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Returns integer token count > 0
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock
        mock_client = mock_anthropic_client(token_count=5)

        # Call function
        result = count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify
        assert isinstance(result, int)
        assert result > 0
        assert result == 5

    def test_count_tokens_for_markdown_with_code_blocks(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Count tokens for markdown file with code blocks.

        Given: File with markdown including code block, model="opus", mock
        When: count_tokens_for_file(path, model, client) called
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

        # Setup mock
        mock_client = mock_anthropic_client(token_count=42)

        # Call function
        result = count_tokens_for_file(test_file, ModelId("opus"), mock_client)

        # Verify
        assert isinstance(result, int)
        assert result == 42

    def test_handle_empty_file(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle empty files without API call.

        Given: Empty file, model="haiku", mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Returns 0
        """
        # Create empty test file
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        # Setup mock (won't be called for empty file)
        mock_client = mock_anthropic_client()

        # Call function
        result = count_tokens_for_file(test_file, ModelId("haiku"), mock_client)

        assert result == 0

    def test_handle_api_authentication_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle API authentication error.

        Given: Invalid/missing API key, mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Raises ApiAuthenticationError with clear message
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock to raise AuthenticationError
        auth_error = AuthenticationError("Invalid API key", response=Mock(), body={})
        mock_client = mock_anthropic_client(side_effect=auth_error)

        # Call function, should raise ApiAuthenticationError
        with pytest.raises(
            ApiAuthenticationError, match=r"(?i)(?:anthropic_api_key|api key)"
        ):
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

    def test_handle_api_rate_limit_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle API rate limit error.

        Given: API returns rate limit error, mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Raises ApiRateLimitError with rate limit message
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock to raise RateLimitError
        rate_limit_error = RateLimitError(
            "Rate limit exceeded", response=Mock(), body={}
        )
        mock_client = mock_anthropic_client(side_effect=rate_limit_error)

        # Call function, should raise ApiRateLimitError
        with pytest.raises(ApiRateLimitError) as exc_info:
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify error message mentions rate limit
        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg

    def test_read_api_key_from_environment(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Read API key from environment.

        Given: ANTHROPIC_API_KEY environment variable set, mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Client uses environment variable value
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Set environment variable
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")

        # Setup mock
        mock_client = mock_anthropic_client(token_count=5)

        # Call function
        result = count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify result - the Anthropic SDK was used
        assert result == 5

    def test_error_message_guides_user_to_set_api_key(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Error message guides user to set API key.

        Given: No ANTHROPIC_API_KEY environment variable, mock client
        When: Token counting attempted with count_tokens_for_file
        Then: Error message includes "ANTHROPIC_API_KEY" and setup instructions
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Remove API key from environment
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        # Setup mock to raise AuthenticationError
        auth_error = AuthenticationError("Invalid API key", response=Mock(), body={})
        mock_client = mock_anthropic_client(side_effect=auth_error)

        # Call function, should raise ApiAuthenticationError
        with pytest.raises(ApiAuthenticationError) as exc_info:
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify error message includes ANTHROPIC_API_KEY and setup instructions
        error_msg = str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in error_msg
        assert "set" in error_msg.lower()  # "Please set" guidance

    def test_count_tokens_uses_resolved_model_id(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Verify API receives resolved model ID.

        Given: Test file containing "Hello world", mock Anthropic client
        When: count_tokens_for_file is called with file path,
        ModelId("claude-sonnet-4-5-20250929"), and mock client
        Then: Returns token count AND mock's messages.count_tokens was
        called with exact model ID "claude-sonnet-4-5-20250929"
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock
        mock_client = mock_anthropic_client(token_count=5)

        # Call function with mock client
        result = count_tokens_for_file(
            test_file, ModelId("claude-sonnet-4-5-20250929"), mock_client
        )

        # Verify
        assert result == 5
        mock_client.messages.count_tokens.assert_called_once_with(
            model="claude-sonnet-4-5-20250929",
            messages=[{"role": "user", "content": "Hello world"}],
        )

    def test_count_tokens_unreadable_file_shows_reason(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle unreadable file error.

        Given: Test file with permissions 000 (unreadable), mock client
        When: count_tokens_for_file is called
        Then: Raises FileReadError with message containing "Failed to read",
        the file path, and "Permission denied"
        """
        # Create unreadable test file
        test_file = tmp_path / "unreadable.md"
        test_file.write_text("Hello world")
        test_file.chmod(0o000)

        # Setup mock
        mock_client = mock_anthropic_client()

        # Call function, should raise FileReadError
        with pytest.raises(FileReadError) as exc_info:
            count_tokens_for_file(
                test_file, ModelId("claude-sonnet-4-5-20250929"), mock_client
            )

        # Verify error message
        error_msg = str(exc_info.value)
        assert "Failed to read" in error_msg
        assert str(test_file) in error_msg

    def test_count_tokens_binary_file_shows_decode_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle binary file decode error.

        Given: Binary file (PNG header bytes), mock Anthropic client
        When: count_tokens_for_file is called
        Then: Raises FileReadError with message containing "Failed to read"
        and file path
        """
        # Create binary test file (PNG header)
        test_file = tmp_path / "binary.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n")

        # Setup mock
        mock_client = mock_anthropic_client()

        # Call function, should raise FileReadError
        with pytest.raises(FileReadError) as exc_info:
            count_tokens_for_file(
                test_file, ModelId("claude-sonnet-4-5-20250929"), mock_client
            )

        # Verify error message
        error_msg = str(exc_info.value)
        assert "Failed to read" in error_msg
        assert str(test_file) in error_msg


class TestCountTokensForFiles:
    """Tests for count_tokens_for_files function."""

    def test_count_tokens_for_files_reuses_single_client(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Verify client is reused across multiple files.

        Given: Three test files ("Hello", "World", "Test"), mock client
        When: count_tokens_for_files is called with paths and resolved ID
        Then: Returns three TokenCount objects, client's
        messages.count_tokens called exactly 3 times
        """
        # Create test files
        file1 = tmp_path / "file1.md"
        file1.write_text("Hello")
        file2 = tmp_path / "file2.md"
        file2.write_text("World")
        file3 = tmp_path / "file3.md"
        file3.write_text("Test")

        # Setup mock with side_effect for multiple responses
        mock_responses = [
            Mock(input_tokens=2),
            Mock(input_tokens=1),
            Mock(input_tokens=3),
        ]
        mock_client = mock_anthropic_client(side_effect=mock_responses)

        # Call function
        results = count_tokens_for_files(
            [file1, file2, file3],
            ModelId("claude-sonnet-4-5-20250929"),
        )

        # Verify
        assert len(results) == 3
        assert mock_client.messages.count_tokens.call_count == 3

    def test_count_tokens_for_multiple_files(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Count tokens for multiple files.

        Given: Two files: "Hello" (file1), "World" (file2), model="sonnet"
        When: count_tokens_for_files(paths, model) called
        Then: Returns list of TokenCount objects with per-file counts
        """
        # Create test files
        file1 = tmp_path / "file1.md"
        file1.write_text("Hello")
        file2 = tmp_path / "file2.md"
        file2.write_text("World")

        # Setup mock with side_effect for multiple responses
        mock_responses = [
            Mock(input_tokens=2),
            Mock(input_tokens=1),
        ]
        mock_anthropic_client(side_effect=mock_responses)

        # Call function
        results = count_tokens_for_files([file1, file2], ModelId("sonnet"))

        # Verify
        assert len(results) == 2
        assert results[0].path == str(file1)
        assert results[0].count == 2
        assert results[1].path == str(file2)
        assert results[1].count == 1

    def test_calculate_total_across_files(self) -> None:
        """Calculate total tokens across files.

        Given: TokenCount results for 3 files: [5, 10, 8]
        When: calculate_total(results) called
        Then: Returns 23
        """
        results = [
            TokenCount(path="file1.md", count=5),
            TokenCount(path="file2.md", count=10),
            TokenCount(path="file3.md", count=8),
        ]

        total = calculate_total(results)

        assert total == 23

    def test_preserve_file_order_in_results(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Preserve file order in results.

        Given: Files [b.md, a.md, c.md] in that order, model="haiku"
        When: count_tokens_for_files(paths, model) called
        Then: Results maintain input order [b.md, a.md, c.md]
        """
        # Create test files in specific order
        file_b = tmp_path / "b.md"
        file_b.write_text("B")
        file_a = tmp_path / "a.md"
        file_a.write_text("A")
        file_c = tmp_path / "c.md"
        file_c.write_text("C")

        # Setup mock with side_effect for multiple responses
        mock_responses = [
            Mock(input_tokens=10),
            Mock(input_tokens=20),
            Mock(input_tokens=30),
        ]
        mock_anthropic_client(side_effect=mock_responses)

        # Call function with files in order [b, a, c]
        results = count_tokens_for_files([file_b, file_a, file_c], ModelId("haiku"))

        # Verify order is preserved
        assert len(results) == 3
        assert results[0].path == str(file_b)
        assert results[1].path == str(file_a)
        assert results[2].path == str(file_c)

    def test_count_tokens_handles_network_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle generic API errors.

        Given: Test file with content, mock to raise APIError
        When: count_tokens_for_file is called
        Then: Raises ApiError with message containing "API error"
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock to raise APIError
        api_error = APIError("Connection timeout", request=Mock(), body={})
        mock_client = mock_anthropic_client(side_effect=api_error)

        # Call function, should raise ApiError
        with pytest.raises(ApiError) as exc_info:
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify error message contains "API error"
        error_msg = str(exc_info.value).lower()
        assert "api error" in error_msg
