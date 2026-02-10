"""Worktree CLI module."""

import re

import click


def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Transform task name to worktree slug.

    Args:
        task_name: The task name to convert.
        max_length: Maximum slug length (default 30).

    Returns:
        A slugified version: lowercase, hyphens, truncated, no trailing hyphens.
    """
    slug = task_name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    slug = slug[:max_length]
    slug = slug.rstrip('-')
    return slug


@click.group(name="_worktree")
def worktree() -> None:
    """Worktree command group."""
