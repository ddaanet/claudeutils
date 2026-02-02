"""Tests for the statusline CLI command."""

from click.testing import CliRunner

from claudeutils.cli import cli


def test_statusline_reads_stdin() -> None:
    """Test that statusline command reads JSON from stdin."""
    runner = CliRunner()
    result = runner.invoke(cli, ["statusline"], input='{"test": "data"}')
    # The command should exist and return exit code 0
    assert result.exit_code == 0
