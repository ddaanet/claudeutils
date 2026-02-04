"""CLI command for statusline."""

import sys

import click

from claudeutils.statusline.context import (
    calculate_context_tokens,
    get_git_status,
    get_thinking_state,
)
from claudeutils.statusline.models import StatuslineInput


@click.command("statusline")
def statusline() -> None:
    """Display statusline reading JSON from stdin."""
    input_data = sys.stdin.read()
    if input_data.strip():
        parsed_input = StatuslineInput.model_validate_json(input_data)
        # Call context functions (store results in local vars, no output yet)
        get_git_status()
        get_thinking_state()
        calculate_context_tokens(parsed_input)
    click.echo("OK")
