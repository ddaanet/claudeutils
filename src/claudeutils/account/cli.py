"""CLI commands for account management."""

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
