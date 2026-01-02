"""Tests for CLI markdown command."""

import io
import subprocess
import sys
from pathlib import Path

import pytest

from claudeutils import cli


def test_help_shows_markdown_command() -> None:
    """Test: Help text shows markdown command."""
    result = subprocess.run(
        ["uv", "run", "claudeutils", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "markdown" in result.stdout


def test_markdown_processes_file_from_stdin(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test: markdown command processes file from stdin."""
    filepath = tmp_path / "test.md"
    filepath.write_text("## About __init__.py\n")

    monkeypatch.setattr(sys, "argv", ["claudeutils", "markdown"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(str(filepath) + "\n"))
    monkeypatch.chdir(tmp_path)

    cli.main()

    captured = capsys.readouterr()
    assert str(filepath) in captured.out
    assert filepath.read_text() == "## About `__init__.py`\n"


def test_markdown_skips_unchanged_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test: markdown command skips unchanged files."""
    filepath = tmp_path / "test.md"
    filepath.write_text("## About `__init__.py`\n")

    monkeypatch.setattr(sys, "argv", ["claudeutils", "markdown"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(str(filepath) + "\n"))
    monkeypatch.chdir(tmp_path)

    cli.main()

    captured = capsys.readouterr()
    assert captured.out == ""


def test_markdown_errors_on_non_md_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test: markdown command errors on non-.md file."""
    filepath = tmp_path / "test.txt"
    filepath.write_text("content")

    monkeypatch.setattr(sys, "argv", ["claudeutils", "markdown"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(str(filepath) + "\n"))
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "not a markdown file" in captured.err


def test_markdown_errors_on_missing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test: markdown command errors on missing file."""
    filepath = tmp_path / "missing.md"

    monkeypatch.setattr(sys, "argv", ["claudeutils", "markdown"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(str(filepath) + "\n"))
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "does not exist" in captured.err


def test_markdown_processes_multiple_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test: markdown command processes multiple files."""
    file1 = tmp_path / "test1.md"
    file2 = tmp_path / "test2.md"
    file3 = tmp_path / "test3.md"

    file1.write_text("## About __init__.py\n")
    file2.write_text("## About __name__.py\n")
    file3.write_text("## About `__init__.py`\n")

    input_text = f"{file1}\n{file2}\n{file3}\n"

    monkeypatch.setattr(sys, "argv", ["claudeutils", "markdown"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(input_text))
    monkeypatch.chdir(tmp_path)

    cli.main()

    captured = capsys.readouterr()
    assert str(file1) in captured.out
    assert str(file2) in captured.out
    assert str(file3) not in captured.out


def test_markdown_batch_processes_all_valid_files_despite_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test: markdown command processes all valid files even when some are invalid."""
    valid1 = tmp_path / "valid1.md"
    invalid = tmp_path / "invalid.txt"
    valid2 = tmp_path / "valid2.md"
    missing = tmp_path / "missing.md"
    valid3 = tmp_path / "valid3.md"

    valid1.write_text("## About __init__.py\n")
    invalid.write_text("content")
    valid2.write_text("## About __name__.py\n")
    # missing.md doesn't exist
    valid3.write_text("## About __main__.py\n")

    input_text = f"{valid1}\n{invalid}\n{valid2}\n{missing}\n{valid3}\n"

    monkeypatch.setattr(sys, "argv", ["claudeutils", "markdown"])
    monkeypatch.setattr(sys, "stdin", io.StringIO(input_text))
    monkeypatch.chdir(tmp_path)

    # Should exit with error code due to invalid files
    with pytest.raises(SystemExit) as exc_info:
        cli.main()
    assert exc_info.value.code == 1

    captured = capsys.readouterr()

    # But should still process all valid files
    assert str(valid1) in captured.out
    assert str(valid2) in captured.out
    assert str(valid3) in captured.out
    assert str(invalid) not in captured.out
    assert str(missing) not in captured.out

    # Should report all errors
    assert "not a markdown file" in captured.err
    assert "does not exist" in captured.err

    # Verify valid files were actually modified
    assert valid1.read_text() == "## About `__init__.py`\n"
    assert valid2.read_text() == "## About `__name__.py`\n"
    assert valid3.read_text() == "## About `__main__.py`\n"
