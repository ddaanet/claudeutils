"""Tests for null mode in when CLI."""

from click.testing import CliRunner

from claudeutils.cli import cli


def test_null_query_exits_silently() -> None:
    """Null query is a D+B gate anchor — exit 0, empty output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["when", "null"])
    assert result.exit_code == 0
    assert result.output.strip() == ""
