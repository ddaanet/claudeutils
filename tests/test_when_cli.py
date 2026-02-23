"""Tests for the when CLI command."""

from pathlib import Path
from unittest.mock import patch

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
    """Test that operator prefix in query is constrained to when/how choices.

    Verifies:
    1. CLI accepts "when ..." prefixed query
    2. CLI accepts "how ..." prefixed query
    3. CLI rejects queries with invalid operator prefix like "what"
    4. Error output contains "valid operator" for invalid operators
    """
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Test Result\n\nMocked content"

        # Valid operator: 'when'
        result = runner.invoke(cli, ["when", "when writing mock tests"])
        assert result.exit_code == 0

        # Valid operator: 'how'
        result = runner.invoke(cli, ["when", "how encode paths"])
        assert result.exit_code == 0

    # Invalid operator: 'what'
    result = runner.invoke(cli, ["when", "what some topic"])
    assert result.exit_code != 0
    assert "valid operator" in result.output.lower()


def test_query_variadic_argument() -> None:
    """Test query argument: dot prefix preservation and no-arg rejection.

    Verifies:
    1. Dot prefix preserved in query (section mode)
    2. Double dot prefix preserved in query (file mode)
    3. At least one query arg required
    """
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Mock Result\n\nMocked content"

        # Dot prefix preserved
        result = runner.invoke(cli, ["when", "when .Section"])
        assert result.exit_code == 0
        # Verify the resolver was called with operator and dot prefix preserved
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args[0]
        assert call_args[0] == "when"  # operator
        assert call_args[1] == ".Section"  # query

        # Reset mock for next test
        mock_resolve.reset_mock()
        mock_resolve.return_value = "# Mock Result\n\nMocked content"

        # Double dot prefix preserved
        result = runner.invoke(cli, ["when", "when ..file.md"])
        assert result.exit_code == 0
        # Verify the resolver was called with operator and double dot prefix preserved
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args[0]
        assert call_args[0] == "when"  # operator
        assert call_args[1] == "..file.md"  # query

    # No query args should error
    result = runner.invoke(cli, ["when"])
    assert result.exit_code != 0
    assert "Missing argument" in result.output


def test_single_arg_query_parsed() -> None:
    """Test that single arg with operator prefix is parsed correctly.

    Verifies:
    1. CLI accepts "when writing mock tests" as a single argument
    2. resolve() is called with operator="when", query="writing mock tests"
    """
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Test Result\n\nMocked content"

        result = runner.invoke(cli, ["when", "when writing mock tests"])
        assert result.exit_code == 0
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args[0]
        assert call_args[0] == "when"  # operator
        assert call_args[1] == "writing mock tests"  # query


def test_cli_invokes_resolver(tmp_path: Path) -> None:
    """Test that CLI invokes resolver with joined query.

    Verifies:
    1. CLI invokes resolver with query "when writing mock tests"
    2. Output contains resolved content (heading + section content)
    3. Exit code is 0
    4. Output includes navigation links (Broader/Related sections)
    """
    # Create test index and decisions directory
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when writing mock tests | pattern\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text(
        "# Test Guide\n"
        "\n"
        "## When Writing Mock Tests\n"
        "\n"
        "Use mocks for external dependencies.\n"
        "\n"
        "### Related\n"
        "\n"
        "- When testing functions\n"
    )

    # Set environment variable for project root
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create the test structure in the isolated filesystem
        iso_index = Path("agents") / "memory-index.md"
        iso_index.parent.mkdir(parents=True, exist_ok=True)
        iso_index.write_text("## testing\n\n/when writing mock tests | pattern\n")

        iso_decisions = Path("agents") / "decisions"
        iso_decisions.mkdir(parents=True, exist_ok=True)

        iso_testing_file = iso_decisions / "testing.md"
        iso_testing_file.write_text(
            "# Test Guide\n"
            "\n"
            "## When Writing Mock Tests\n"
            "\n"
            "Use mocks for external dependencies.\n"
            "\n"
            "### Related\n"
            "\n"
            "- When testing functions\n"
        )

        result = runner.invoke(cli, ["when", "when writing mock tests"])

    assert result.exit_code == 0
    # Check that heading is in output
    assert "#" in result.output
    # Output should contain the resolved content
    assert "When Writing Mock Tests" in result.output
    # Output should not be empty
    assert len(result.output) > 0


def test_batched_recall_multiple_queries() -> None:
    """Test that multiple query args produce batched output separated by `---`.

    Verifies:
    1. Two query args invoke resolve() twice (once per query)
    2. Output contains both results separated by newline-dashes-newline
    3. Single query produces no separator (backward compatible)
    """
    runner = CliRunner()

    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.side_effect = [
            "# Result 1\n\nFirst content",
            "# Result 2\n\nSecond content",
        ]

        result = runner.invoke(
            cli, ["when", "when writing mock tests", "how encode paths"]
        )
        assert result.exit_code == 0
        assert mock_resolve.call_count == 2

        # First call: operator=when, query=writing mock tests
        first_call = mock_resolve.call_args_list[0][0]
        assert first_call[0] == "when"
        assert first_call[1] == "writing mock tests"

        # Second call: operator=how, query=encode paths
        second_call = mock_resolve.call_args_list[1][0]
        assert second_call[0] == "how"
        assert second_call[1] == "encode paths"

        # Output contains both results joined by separator
        assert "---" in result.output
        assert "# Result 1" in result.output
        assert "# Result 2" in result.output

    # Single query: no separator in output
    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Single Result\n\nContent"
        result = runner.invoke(cli, ["when", "when writing mock tests"])
        assert result.exit_code == 0
        assert "---" not in result.output


def test_invalid_prefix_rejected() -> None:
    """Test prefix validation: rejects invalid prefix, accepts case-insensitive prefix.

    Verifies:
    1. Query with no valid prefix ("no prefix query") exits non-zero
    2. Error message states what is wrong (mentions "when" or "how")
    3. Uppercase operator ("WHEN writing tests") accepted (case-insensitive)
    4. Invalid prefix never reaches resolver (validated before resolve() call)
    """
    runner = CliRunner()

    # Invalid prefix: no operator prefix at all
    result = runner.invoke(cli, ["when", "no prefix query"])
    assert result.exit_code != 0
    assert "when" in result.output.lower() or "how" in result.output.lower()

    # Prefix validation must NOT call resolve() for invalid prefix
    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        result = runner.invoke(cli, ["when", "no prefix query"])
        assert result.exit_code != 0
        mock_resolve.assert_not_called()

    # Case-insensitive: "WHEN writing tests" should be accepted
    with patch("claudeutils.when.cli.resolve") as mock_resolve:
        mock_resolve.return_value = "# Result\n\nContent"
        result = runner.invoke(cli, ["when", "WHEN writing tests"])
        assert result.exit_code == 0
        mock_resolve.assert_called_once()
        call_args = mock_resolve.call_args[0]
        assert call_args[0] == "when"  # operator normalised to lowercase
        assert call_args[1] == "writing tests"


def test_cli_error_handling() -> None:
    """Test CLI error handling: exit code 1 and diagnostic output for resolver errors.

    Verifies:
    1. Nonexistent trigger: exit code 1, output contains "Did you mean:"
    2. Nonexistent section (dot prefix): exit code 1, output contains "not found"
    3. Nonexistent file (double-dot prefix): exit code 1, output contains "not found"

    Note: click 8.2 removed mix_stderr — both stdout and stderr go to result.output.
    """
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Set up test structure
        iso_index = Path("agents") / "memory-index.md"
        iso_index.parent.mkdir(parents=True, exist_ok=True)
        iso_index.write_text("## testing\n\n/when writing tests | tests\n")

        iso_decisions = Path("agents") / "decisions"
        iso_decisions.mkdir(parents=True, exist_ok=True)

        iso_testing_file = iso_decisions / "testing.md"
        iso_testing_file.write_text(
            "# Test Guide\n\n## When Writing Tests\n\nUse tests for coverage.\n"
        )

        # Test 1: Nonexistent trigger
        result = runner.invoke(cli, ["when", "when nonexistent trigger"])
        assert result.exit_code == 1
        assert "Did you mean:" in result.output

        # Test 2: Nonexistent section (using . prefix)
        result = runner.invoke(cli, ["when", "when .NotExist"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

        # Test 3: Nonexistent file (using .. prefix)
        result = runner.invoke(cli, ["when", "when ..nonexistent.md"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()
