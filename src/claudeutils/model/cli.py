"""CLI commands for model management."""

from pathlib import Path

import click

from claudeutils.model import load_litellm_config


@click.group()
def model() -> None:
    """Manage Claude models and configuration."""


@model.command("list")
def list_models() -> None:
    """List available models from LiteLLM configuration."""
    config_path = Path.home() / ".config" / "litellm" / "config.yaml"
    if config_path.exists():
        models = load_litellm_config(config_path)
        for m in models:
            click.echo(m.name)
    else:
        click.echo("No LiteLLM configuration found")
