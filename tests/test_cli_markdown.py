"""Tests for CLI markdown command."""

import subprocess
from pathlib import Path

from click.testing import CliRunner

from claudeutils.cli import cli


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
) -> None:
    """Test: markdown command processes file from stdin."""
    filepath = tmp_path / "test.md"
    filepath.write_text("## About __init__.py\n")

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert str(filepath) in result.output
    assert filepath.read_text() == "## About `__init__.py`\n"


def test_markdown_skips_unchanged_files(
    tmp_path: Path,
) -> None:
    """Test: markdown command skips unchanged files."""
    filepath = tmp_path / "test.md"
    filepath.write_text("## About `__init__.py`\n")

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert result.output == ""


def test_markdown_errors_on_non_md_file(
    tmp_path: Path,
) -> None:
    """Test: markdown command errors on non-.md file."""
    filepath = tmp_path / "test.txt"
    filepath.write_text("content")

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert result.exit_code == 1
    # Error message could be in output or exception
    assert "not a markdown file" in result.output or (
        result.exception and "not a markdown file" in str(result.exception)
    )


def test_markdown_errors_on_missing_file(
    tmp_path: Path,
) -> None:
    """Test: markdown command errors on missing file."""
    filepath = tmp_path / "missing.md"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert result.exit_code == 1
    # Error message could be in output or exception
    assert "does not exist" in result.output or (
        result.exception and "does not exist" in str(result.exception)
    )


def test_markdown_processes_multiple_files(
    tmp_path: Path,
) -> None:
    """Test: markdown command processes multiple files."""
    file1 = tmp_path / "test1.md"
    file2 = tmp_path / "test2.md"
    file3 = tmp_path / "test3.md"

    file1.write_text("## About __init__.py\n")
    file2.write_text("## About __name__.py\n")
    file3.write_text("## About `__init__.py`\n")

    input_text = f"{file1}\n{file2}\n{file3}\n"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=input_text)

    assert str(file1) in result.output
    assert str(file2) in result.output
    assert str(file3) not in result.output


def test_markdown_batch_processes_all_valid_files_despite_errors(
    tmp_path: Path,
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

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=input_text)

    # Should exit with error code due to invalid files
    assert result.exit_code == 1

    # But should still process all valid files (their paths appear in success messages)
    assert str(valid1) in result.output
    assert str(valid2) in result.output
    assert str(valid3) in result.output

    # Error messages include invalid paths, valid ones were processed
    # Check that errors were reported for invalid files
    output_text = result.output
    error_messages = (
        output_text[output_text.find("Error:") :]
        if "Error:" in output_text
        else output_text
    )
    assert (
        "not a markdown file" in error_messages or "not a markdown file" in output_text
    )
    assert "does not exist" in error_messages or "does not exist" in output_text

    # Verify valid files were actually modified
    assert valid1.read_text() == "## About `__init__.py`\n"
    assert valid2.read_text() == "## About `__name__.py`\n"
    assert valid3.read_text() == "## About `__main__.py`\n"


def test_markdown_reports_multiple_processing_errors(
    tmp_path: Path,
) -> None:
    """Test: markdown command reports all processing errors together."""
    error1 = tmp_path / "error1.md"
    error2 = tmp_path / "error2.md"
    valid = tmp_path / "valid.md"

    # Create files with inner fence errors (non-markdown blocks with inner fences)
    error1.write_text(
        "```python\n"
        "def foo():\n"
        '    """\n'
        "    Example:\n"
        "    ```\n"
        "    code\n"
        "    ```\n"
        '    """\n'
        "```\n"
    )

    error2.write_text("```bash\n# Example\n```\ninner content\n```\n```\n")

    valid.write_text("## About __init__.py\n")

    input_text = f"{error1}\n{error2}\n{valid}\n"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=input_text)

    # Should exit with error code
    assert result.exit_code == 1

    # Should still process the valid file
    assert str(valid) in result.output
    assert valid.read_text() == "## About `__init__.py`\n"

    # Should report all errors together at the end
    output_lines = result.output.strip().split("\n")
    error_lines = [
        line
        for line in output_lines
        if "error" in line.lower() or "inner fence" in line.lower()
    ]

    # Should have at least 2 error messages (one for each failed file)
    assert len(error_lines) >= 2

    # Both error files should be mentioned in the error output
    error_text = "\n".join(error_lines)
    assert str(error1) in error_text
    assert str(error2) in error_text
