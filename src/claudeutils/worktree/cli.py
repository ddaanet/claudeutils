"""Worktree CLI module."""

import click


@click.group(name="_worktree")
def worktree() -> None:
    """Worktree command group."""
