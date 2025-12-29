"""Integration tests for tokens CLI subcommand."""

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

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

    assert result.returncode == 1
    assert "model" in result.stderr.lower() or "required" in result.stderr.lower()


def test_cli_accepts_single_file(tmp_path: Path) -> None:
    """Test that CLI accepts single file with model."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-sonnet-4-5-20250929"
        mock_count.return_value = 42
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


def test_cli_handles_multiple_files(tmp_path: Path) -> None:
    """Test that CLI handles multiple files."""
    file1 = tmp_path / "a.md"
    file2 = tmp_path / "b.md"
    file1.write_text("Hello")
    file2.write_text("World")

    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-opus-4-5-20251101"
        mock_count.side_effect = [10, 20]
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


def test_cli_text_format_with_model_id(tmp_path: Path) -> None:
    """Test default text format shows model ID and file counts."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-sonnet-4-5-20250929"
        mock_count.return_value = 42
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


def test_cli_json_format_with_model_id(tmp_path: Path) -> None:
    """Test JSON format outputs structured data with model ID."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-haiku-4-5-20251001"
        mock_count.return_value = 42
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            handle_tokens("haiku", [str(test_file), "--json"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

    result = json.loads(output)
    assert result["model"] == "claude-haiku-4-5-20251001"
    assert len(result["files"]) == 1
    assert result["files"][0]["path"] == str(test_file)
    assert result["files"][0]["count"] == 42
    assert result["total"] == 42


def test_cli_json_format_with_multiple_files(tmp_path: Path) -> None:
    """Test JSON format with multiple files."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file1.write_text("Hello")
    file2.write_text("World")

    with (
        patch("claudeutils.tokens_cli.resolve_model_alias") as mock_resolve,
        patch("claudeutils.tokens_cli.count_tokens_for_file") as mock_count,
    ):
        mock_resolve.return_value = "claude-opus-4-5-20251101"
        mock_count.side_effect = [10, 20]
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            handle_tokens("opus", [str(file1), str(file2), "--json"])
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
