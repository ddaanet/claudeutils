"""Tests for the account CLI command group."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from claudeutils.cli import cli


def test_account_status(tmp_path: Path) -> None:
    """Test account status reads filesystem state."""
    # Create a mock home directory with account-mode file
    account_mode_file = tmp_path / ".claude" / "account-mode"
    account_mode_file.parent.mkdir(parents=True, exist_ok=True)
    account_mode_file.write_text("api")

    runner = CliRunner()
    with patch("claudeutils.account.cli.Path.home", return_value=tmp_path):
        result = runner.invoke(cli, ["account", "status"])

    # Verify the command reads the file and outputs actual mode
    assert result.exit_code == 0
    assert "Mode: api" in result.output


def test_account_plan(tmp_path: Path) -> None:
    """Test account plan writes files with provider credentials.

    Verifies that switching to plan mode generates a claude-env file containing
    the provider API credentials.
    """
    runner = CliRunner()
    # Mock Keychain.find to return test credentials
    mock_keychain = MagicMock()
    mock_keychain.find.return_value = "test-anthropic-key"
    with (
        patch("claudeutils.account.cli.Path.home", return_value=tmp_path),
        patch("claudeutils.account.cli.Keychain", return_value=mock_keychain),
    ):
        result = runner.invoke(cli, ["account", "plan"])
    assert result.exit_code == 0
    # Verify files were written
    account_mode_file = tmp_path / ".claude" / "account-mode"
    claude_env_file = tmp_path / ".claude" / "claude-env"
    assert account_mode_file.exists()
    assert claude_env_file.exists()
    assert account_mode_file.read_text() == "plan"
    # Verify claude-env contains provider credentials
    claude_env_content = claude_env_file.read_text()
    assert "ANTHROPIC_API_KEY=test-anthropic-key" in claude_env_content


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


def test_account_status_with_issues(tmp_path: Path) -> None:
    """Test account status shows validation issues."""
    # Create a mock home directory with account-mode file set to plan
    account_mode_file = tmp_path / ".claude" / "account-mode"
    account_mode_file.parent.mkdir(parents=True, exist_ok=True)
    account_mode_file.write_text("plan")

    runner = CliRunner()
    # Mock Path.home to use tmp_path
    with patch("claudeutils.account.cli.Path.home", return_value=tmp_path):
        # Mock Keychain instance and its find method to return None
        mock_keychain = MagicMock()
        mock_keychain.find.return_value = None
        with patch("claudeutils.account.state.Keychain", return_value=mock_keychain):
            result = runner.invoke(cli, ["account", "status"])

    assert result.exit_code == 0
    # Verify validation issue is displayed
    assert "Plan mode requires OAuth credentials in keychain" in result.output
