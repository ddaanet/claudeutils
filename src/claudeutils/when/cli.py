"""CLI command for when memory recall."""

import click


@click.command(name="when")
@click.argument("operator", type=click.Choice(["when", "how"]))
@click.argument("query", nargs=-1, required=True)
def when_cmd(operator: str, query: tuple[str, ...]) -> None:
    """Query memory index with fuzzy matching operators.

    OPERATOR: Matching operator (fuzzy, exact, section, file)
    QUERY: Search query (multiple words joined with spaces)
    """
    query_str = " ".join(query)
    click.echo(f"Operator: {operator}, Query: {query_str}")
