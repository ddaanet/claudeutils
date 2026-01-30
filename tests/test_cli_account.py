"""Tests for the account CLI command group."""

from click.testing import CliRunner

from claudeutils.cli import cli


def test_account_status() -> None:
    """Test that account status command returns account state."""
    runner = CliRunner()
    result = runner.invoke(cli, ["account", "status"])
    # The command should exist and return exit code 0
    assert result.exit_code == 0
