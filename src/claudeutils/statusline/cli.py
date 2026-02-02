"""CLI command for statusline."""

import json
import sys

import click


@click.command("statusline")
def statusline() -> None:
    """Display statusline reading JSON from stdin."""
    input_data = sys.stdin.read()
    if input_data.strip():
        json.loads(input_data)  # Validate JSON
    click.echo("OK")
