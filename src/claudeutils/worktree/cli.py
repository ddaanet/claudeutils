"""Worktree CLI module."""

import re
import subprocess

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
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    main_path = result.stdout.strip()

    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = result.stdout.strip().split("\n") if result.stdout.strip() else []

    entries = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("worktree "):
            path = lines[i].split(maxsplit=1)[1]
            i += 1

            branch = ""
            while i < len(lines) and lines[i]:
                if lines[i].startswith("branch "):
                    branch = lines[i].split(maxsplit=1)[1]
                i += 1

            i += 1

            if path != main_path:
                slug = path.split("/")[-1]
                entries.append((slug, branch, path))
        else:
            i += 1

    for slug, branch, path in entries:
        click.echo(f"{slug}\t{branch}\t{path}")


@worktree.command(name="clean-tree")
def clean_tree() -> None:
    """Validate clean state of parent repo and submodule.

    Exits 0 silently if clean, exits 1 with dirty file list if dirty. Session
    context files (agents/session.md, agents/jobs.md, agents/learnings.md) are
    excluded from clean-tree checks.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    parent_status = result.stdout

    result = subprocess.run(
        ["git", "-C", "agent-core", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    submodule_status = result.stdout if result.returncode == 0 else ""

    combined = parent_status + submodule_status

    exempt_files = {"agents/session.md", "agents/jobs.md", "agents/learnings.md"}
    filtered_lines = [
        line
        for line in combined.rstrip().split("\n")
        if line
        and not any(line.endswith(f" {exempt_file}") for exempt_file in exempt_files)
    ]
    filtered_output = "\n".join(filtered_lines)

    if filtered_output:
        click.echo(filtered_output)
        raise SystemExit(1)


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit with message from stdin.

    Idempotent: exits 0 silently if nothing staged. If staged changes exist,
    reads commit message from stdin and outputs commit hash to stdout.
    """
    result = subprocess.run(
        ["git", "diff", "--quiet", "--cached"],
        check=False,
    )
    had_staged_before = result.returncode == 1

    subprocess.run(
        ["git", "add", *list(files)],
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--quiet", "--cached"],
        check=False,
    )
    has_staged_after = result.returncode == 1

    if has_staged_after and (
        had_staged_before
        or any(
            subprocess.run(
                ["git", "ls-files", "--error-unmatch", file],
                capture_output=True,
                check=False,
            ).returncode
            == 0
            for file in files
        )
    ):
        message = click.get_text_stream("stdin").read()
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(result.stdout.strip())
