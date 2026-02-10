"""Worktree CLI module."""

import re

import click

from claudeutils.worktree.commands import (
    cmd_add_commit,
    cmd_clean_tree,
    cmd_ls,
    cmd_merge,
    cmd_new,
    cmd_rm,
)


def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Transform task name to worktree slug.

    Args:
        task_name: The task name to convert.
        max_length: Maximum slug length (default 30).

    Returns:
        A slugified version: lowercase, hyphens, truncated, no trailing hyphens.
    """
    slug = task_name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    slug = slug[:max_length]
    return slug.rstrip("-")


@click.group(name="_worktree")
def worktree() -> None:
    """Manage git worktrees for parallel task execution."""


@worktree.command()
def ls() -> None:
    """List active worktrees (excluding main)."""
    cmd_ls()


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Validate clean state of parent repo and submodule.

    Exits 0 silently if clean, exits 1 with dirty file list if dirty. Session
    context files (agents/session.md, agents/jobs.md, agents/learnings.md) are
    excluded from clean-tree checks.
    """
    cmd_clean_tree()


@worktree.command()
@click.argument("slug")
@click.option("--base", default="HEAD", help="Base commit for worktree branch")
@click.option("--session", default="", help="Session file path")
def new(slug: str, base: str, session: str) -> None:
    """Create a new git worktree with branch.

    Creates a worktree at wt/{slug}/ checked out to a new branch {slug} based on
    the specified base commit (default HEAD).

    With --session: pre-commits focused session file to branch before creating worktree.
    """
    cmd_new(slug, base, session)


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit with message from stdin.

    Idempotent: exits 0 silently if nothing staged. If staged changes exist,
    reads commit message from stdin and outputs commit hash to stdout.
    """
    cmd_add_commit(files)


@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
    """Remove a git worktree and its branch.

    Removes the worktree directory at wt/{slug}/ and the corresponding git
    branch. Warns if worktree has uncommitted changes or branch is unmerged, but
    proceeds with removal anyway (forced).

    Handles branch-only cleanup: if worktree directory doesn't exist but branch
    does, prunes stale worktree registration then removes the branch (idempotent).
    """
    cmd_rm(slug)


@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Merge a worktree branch back to parent.

    Phase 1 pre-checks:
    - Clean tree validation (source files) — session files exempt
    - Branch validation (verify slug branch exists)
    - Worktree directory check (warn if missing but continue)
    """
    cmd_merge(slug)
