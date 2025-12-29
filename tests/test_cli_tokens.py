"""Integration tests for tokens CLI subcommand."""

import io
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from claudeutils.cli import handle_tokens


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

    with patch("claudeutils.cli.count_tokens_for_file") as mock_count:
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

    with patch("claudeutils.cli.count_tokens_for_file") as mock_count:
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
