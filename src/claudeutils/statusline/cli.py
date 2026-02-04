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
    try:
        input_data = sys.stdin.read()

        if input_data.strip():
            parsed_input = StatuslineInput.model_validate_json(input_data)
            # Call context functions (store results in local vars, no output yet)
            git_status = get_git_status()
            get_thinking_state()
            context_tokens = calculate_context_tokens(parsed_input)

            # Get account state and route to appropriate usage function
            account_state = get_account_state()
            if account_state.mode == "plan":
                get_plan_usage()
            elif account_state.mode == "api":
                get_api_usage()

            # Format and output two lines
            # Line 1: model emoji + directory + git branch + cost + context tokens
            model_name = parsed_input.model.display_name
            dir_name = parsed_input.workspace.current_dir
            branch = git_status.branch if git_status.branch else "no-branch"
            cost = f"${parsed_input.cost.total_cost_usd:.2f}"
            context_str = f"{context_tokens}t" if context_tokens else "0t"

            line1 = f"{model_name} {dir_name} {branch} {cost} {context_str}"

            # Line 2: mode + usage info
            mode = account_state.mode
            line2 = f"mode: {mode}"

            click.echo(line1)
            click.echo(line2)
        else:
            click.echo("")
            click.echo("")
    except Exception as e:  # noqa: BLE001 - R5: Always exit 0, catch all exceptions
        click.echo(f"Error: {e}", err=True)
