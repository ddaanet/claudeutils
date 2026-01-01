"""Integration tests for tokens CLI subcommand."""

import io
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from anthropic import AuthenticationError

from claudeutils.exceptions import (
    ApiRateLimitError,
    FileReadError,
)
from claudeutils.tokens_cli import handle_tokens


def test_cli_requires_model_argument(tmp_path: Path) -> None:
    """Test that CLI requires model argument."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    result = subprocess.run(
        ["uv", "run", "claudeutils", "tokens", str(test_file)],
        check=False,
        capture_output=True,
        text=True,
    )

    # argparse returns exit code 2 for missing required arguments
    assert result.returncode == 2
    assert "required" in result.stderr.lower()


def test_cli_accepts_single_file(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test that CLI accepts single file with model."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks
    mock_token_counting(model_id="claude-sonnet-4-5-20250929", counts=42)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("sonnet", [str(test_file)])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert "test.md" in output
    assert "42" in output


def test_cli_reports_missing_file(tmp_path: Path) -> None:
    """Test that CLI reports missing file."""
    missing_file = tmp_path / "missing.md"
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("haiku", [str(missing_file)])
        assert exc_info.value.code == 1
        error_output = sys.stderr.getvalue()
        assert "missing.md" in error_output
    finally:
        sys.stderr = old_stderr


def test_cli_handles_multiple_files(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test that CLI handles multiple files."""
    file1 = tmp_path / "a.md"
    file2 = tmp_path / "b.md"
    file1.write_text("Hello")
    file2.write_text("World")

    # Setup mocks
    mock_token_counting(model_id="claude-opus-4-5-20251101", counts=[10, 20])
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("opus", [str(file1), str(file2)])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert "a.md" in output
    assert "b.md" in output
    assert "10" in output
    assert "20" in output


def test_cli_text_format_with_model_id(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test default text format shows model ID and file counts."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks
    mock_token_counting(model_id="claude-sonnet-4-5-20250929", counts=42)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("sonnet", [str(test_file)])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    lines = output.strip().split("\n")
    assert "Using model: claude-sonnet-4-5-20250929" in lines[0]
    assert "test.md: 42 tokens" in output


def test_cli_json_format_with_model_id(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test JSON format outputs structured data with model ID."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks
    mock_token_counting(model_id="claude-haiku-4-5-20251001", counts=42)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("haiku", [str(test_file)], json_output=True)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    result = json.loads(output)
    assert result["model"] == "claude-haiku-4-5-20251001"
    assert len(result["files"]) == 1
    assert result["files"][0]["path"] == str(test_file)
    assert result["files"][0]["count"] == 42
    assert result["total"] == 42


def test_cli_json_format_with_multiple_files(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test JSON format with multiple files."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file1.write_text("Hello")
    file2.write_text("World")

    # Setup mocks
    mock_token_counting(model_id="claude-opus-4-5-20251101", counts=[10, 20])
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("opus", [str(file1), str(file2)], json_output=True)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    result = json.loads(output)
    assert result["model"] == "claude-opus-4-5-20251101"
    assert len(result["files"]) == 2
    assert result["files"][0]["path"] == str(file1)
    assert result["files"][0]["count"] == 10
    assert result["files"][1]["path"] == str(file2)
    assert result["files"][1]["count"] == 20
    assert result["total"] == 30


def test_cli_auth_error_shows_helpful_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Handle CLI authentication error with helpful message.

    Given: Test file exists, mock Anthropic() to raise AuthenticationError
    When: handle_tokens called with model="sonnet", files=[test_file]
    Then: Exits with code 1, stderr has "Authentication failed" and
    "ANTHROPIC_API_KEY"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Mock Anthropic() to raise AuthenticationError
    with patch("claudeutils.tokens_cli.Anthropic") as mock_anthropic_class:
        mock_anthropic_class.side_effect = AuthenticationError(
            "Invalid API key", response=Mock(), body={}
        )
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("sonnet", [str(test_file)])

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Authentication failed" in captured.err
        assert "ANTHROPIC_API_KEY" in captured.err


def test_cli_rate_limit_error_shows_message(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Handle CLI rate limit error.

    Given: Mock count_tokens_for_file to raise ApiRateLimitError
    When: handle_tokens is called
    Then: Exits with code 1, stderr contains "Error: Rate limit exceeded"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks with resolve returning model and count_tokens raising error
    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-sonnet-4-5-20250929"
        mock_count.side_effect = ApiRateLimitError()
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("sonnet", [str(test_file)])

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Rate limit exceeded" in captured.err


def test_cli_file_error_shows_message(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Handle CLI file read error.

    Given: Mock count_tokens_for_file to raise FileReadError
    When: handle_tokens is called
    Then: Exits with code 1, stderr contains "Error:" followed by file error message
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks with resolve returning model and count_tokens raising error
    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-sonnet-4-5-20250929"
        mock_count.side_effect = FileReadError("/path/to/file", "Permission denied")
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("sonnet", [str(test_file)])

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        assert "Failed to read" in captured.err


def test_cli_handles_empty_api_key_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Handle SDK TypeError when API key is empty.

    Given: Test file exists, Anthropic() raises TypeError with auth message
    When: handle_tokens is called
    Then: Exits with code 1, stderr has "Authentication failed" and
    "ANTHROPIC_API_KEY"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Mock Anthropic() to raise TypeError (what SDK does with empty API key)
    with patch("claudeutils.tokens_cli.Anthropic") as mock_anthropic_class:
        mock_anthropic_class.side_effect = TypeError(
            '"Could not resolve authentication method. Expected either '
            'api_key or auth_token to be set."'
        )
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("sonnet", [str(test_file)])

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Authentication failed" in captured.err
        assert "ANTHROPIC_API_KEY" in captured.err
