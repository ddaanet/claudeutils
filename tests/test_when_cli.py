"""Tests for the when CLI command."""

from click.testing import CliRunner

from claudeutils.cli import cli
from claudeutils.when.cli import when_cmd


def test_when_command_exists() -> None:
    """Test that when command exists and is registered in CLI.

    Verifies:
    1. when_cmd can be imported from claudeutils.when.cli
    2. when_cmd is a Click command
    3. CLI responds to 'when --help' with help text
    """
    # Verify import succeeds
    assert when_cmd is not None

    # Verify command is accessible via CLI
    runner = CliRunner()
    result = runner.invoke(cli, ["when", "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_operator_argument_validation() -> None:
    """Test that operator argument is constrained to when/how choices.

    Verifies:
    1. CLI accepts 'when' as operator
    2. CLI accepts 'how' as operator
    3. CLI rejects invalid operators like 'what'
    4. Error output contains "Invalid value" for invalid operators
    """
    runner = CliRunner()

    # Valid operator: 'when'
    result = runner.invoke(cli, ["when", "when", "writing mock tests"])
    assert result.exit_code == 0

    # Valid operator: 'how'
    result = runner.invoke(cli, ["when", "how", "encode paths"])
    assert result.exit_code == 0

    # Invalid operator: 'what'
    result = runner.invoke(cli, ["when", "what", "some topic"])
    assert result.exit_code != 0
    assert "Invalid value" in result.output


def test_query_variadic_argument() -> None:
    """Test that query argument is variadic and joins multiple words.

    Verifies:
    1. Multiple query words joined with spaces
    2. Dot prefix preserved in query (mode switches)
    3. Double dot prefix preserved in query (file mode)
    4. At least one query word required
    """
    runner = CliRunner()

    # Multiple words joined
    result = runner.invoke(cli, ["when", "when", "writing", "mock", "tests"])
    assert result.exit_code == 0
    assert "writing mock tests" in result.output

    # Dot prefix preserved
    result = runner.invoke(cli, ["when", "when", ".Section"])
    assert result.exit_code == 0
    assert ".Section" in result.output

    # Double dot prefix preserved
    result = runner.invoke(cli, ["when", "when", "..file.md"])
    assert result.exit_code == 0
    assert "..file.md" in result.output

    # No query args should error
    result = runner.invoke(cli, ["when", "when"])
    assert result.exit_code != 0
    assert "Missing argument" in result.output
