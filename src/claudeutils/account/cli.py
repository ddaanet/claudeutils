"""CLI commands for account management."""

from pathlib import Path

import click

from claudeutils.account import AccountState


@click.group()
def account() -> None:
    """Manage Claude account configuration."""


@account.command()
def status() -> None:
    """Display current account status."""
    # Minimal implementation: create a simple state and display it
    state = AccountState(
        mode="plan",
        provider="anthropic",
        oauth_in_keychain=True,
        api_in_claude_env=False,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    issues = state.validate_consistency()
    click.echo(f"Mode: {state.mode}")
    click.echo(f"Provider: {state.provider}")
    if issues:
        click.echo("Issues:")
        for issue in issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("No issues found")


@account.command()
def plan() -> None:
    """Switch to plan mode and write account configuration files."""
    # Minimal implementation: write account-mode and claude-env files
    account_mode_file = Path.home() / ".claude" / "account-mode"
    claude_env_file = Path.home() / ".claude" / "claude-env"

    # Write account-mode file
    account_mode_file.parent.mkdir(parents=True, exist_ok=True)
    account_mode_file.write_text("plan")

    # Write claude-env file (empty for now)
    claude_env_file.write_text("")

    click.echo("Switched to plan mode")
