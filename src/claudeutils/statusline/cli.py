"""CLI command for statusline."""

import sys

import click

from claudeutils.account.state import get_account_state
from claudeutils.statusline.api_usage import get_api_usage
from claudeutils.statusline.context import (
    calculate_context_tokens,
    get_git_status,
    get_thinking_state,
)
from claudeutils.statusline.models import StatuslineInput
from claudeutils.statusline.plan_usage import get_plan_usage


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

        # Get account state and route to appropriate usage function
        account_state = get_account_state()
        if account_state.mode == "plan":
            get_plan_usage()
        elif account_state.mode == "api":
            get_api_usage()
    click.echo("OK")
