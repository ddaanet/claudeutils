"""Tests for the account CLI command group."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from claudeutils.cli import cli


def test_account_status() -> None:
    """Test that account status command returns account state."""
    runner = CliRunner()
    result = runner.invoke(cli, ["account", "status"])
    # The command should exist and return exit code 0
    assert result.exit_code == 0


def test_account_plan(tmp_path: Path) -> None:
    """Test that account plan command switches mode and writes files."""
    runner = CliRunner()
    with patch("pathlib.Path.home", return_value=tmp_path):
        result = runner.invoke(cli, ["account", "plan"])
    assert result.exit_code == 0
    # Verify files were written
    account_mode_file = tmp_path / ".claude" / "account-mode"
    claude_env_file = tmp_path / ".claude" / "claude-env"
    assert account_mode_file.exists()
    assert claude_env_file.exists()
    assert account_mode_file.read_text() == "plan"


def test_account_api(tmp_path: Path) -> None:
    """Test that account api command switches to API mode."""
    runner = CliRunner()
    with patch("pathlib.Path.home", return_value=tmp_path):
        result = runner.invoke(cli, ["account", "api", "--provider", "anthropic"])
    assert result.exit_code == 0
    # Verify files were written
    account_mode_file = tmp_path / ".claude" / "account-mode"
    provider_file = tmp_path / ".claude" / "account-provider"
    assert account_mode_file.exists()
    assert provider_file.exists()
    assert account_mode_file.read_text() == "api"
    assert provider_file.read_text() == "anthropic"
