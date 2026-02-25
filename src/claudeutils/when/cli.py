"""CLI command for when memory recall."""

import os
import sys
from pathlib import Path

import click

from claudeutils.when.resolver import ResolveError, resolve

VALID_OPERATORS = {"when", "how"}


def _strip_operator(arg: str) -> str:
    """Strip optional operator prefix (when/how), return bare trigger."""
    parts = arg.split(" ", 1)
    if len(parts) >= 2 and parts[0].lower() in VALID_OPERATORS:
        return parts[1]
    return arg


@click.command(name="when")
@click.argument("queries", nargs=-1, required=True)
def when_cmd(queries: tuple[str, ...]) -> None:
    """Query memory index with fuzzy matching.

    QUERIES: One or more trigger queries. Operator prefix (when/how) is optional.
    Examples: "writing mock tests", "when writing mock tests", "how encode paths"
    """
    project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", "."))
    index_path = project_root / "agents" / "memory-index.md"
    decisions_dir = project_root / "agents" / "decisions"

    results: list[str] = []
    errors: list[str] = []
    for arg in queries:
        query_str = _strip_operator(arg)
        if not query_str.strip():
            errors.append(f"Error: Empty query body in '{arg}'.")
            continue

        try:
            results.append(resolve(query_str, str(index_path), str(decisions_dir)))
        except ResolveError as e:
            errors.append(str(e))

    # Print successes first
    if results:
        click.echo("\n---\n".join(results))

    # Then errors to stdout
    if errors:
        for err in errors:
            click.echo(err)
        sys.exit(1)
