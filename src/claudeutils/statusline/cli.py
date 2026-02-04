"""CLI command for statusline."""

import sys

import click

from claudeutils.statusline.models import StatuslineInput


@click.command("statusline")
def statusline() -> None:
    """Display statusline reading JSON from stdin."""
    input_data = sys.stdin.read()
    if input_data.strip():
        StatuslineInput.model_validate_json(input_data)
    click.echo("OK")
