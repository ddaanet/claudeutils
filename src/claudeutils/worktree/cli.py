"""Worktree CLI module."""

import os
import re
import subprocess
import tempfile
from pathlib import Path

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
                slug = Path(path).name
                entries.append((slug, branch, path))
        else:
            i += 1

    for slug, branch, path in entries:
        click.echo(f"{slug}\t{branch}\t{path}")


def _create_session_commit(slug: str, base: str, session: str) -> str:
    """Pre-commit session.md to branch using isolated temp index.

    Avoids polluting main worktree index by using GIT_INDEX_FILE isolation.

    Returns:
        Commit hash for the session commit.
    """
    session_path = Path(session)
    try:
        session_content = session_path.read_text()
    except (FileNotFoundError, PermissionError) as e:
        click.echo(f"Error reading session file {session}: {e}", err=True)
        raise SystemExit(1) from e

    with tempfile.NamedTemporaryFile(delete=False, suffix=".index") as tmp_index:
        tmp_index_path = tmp_index.name

    try:
        env = {**os.environ, "GIT_INDEX_FILE": tmp_index_path}

        result = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=session_content,
            capture_output=True,
            text=True,
            check=True,
        )
        blob_hash = result.stdout.strip()

        result = subprocess.run(
            ["git", "rev-parse", f"{base}^{{tree}}"],
            capture_output=True,
            text=True,
            check=True,
        )
        base_tree = result.stdout.strip()

        subprocess.run(
            ["git", "read-tree", base_tree],
            env=env,
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob_hash},agents/session.md",
            ],
            env=env,
            check=True,
            capture_output=True,
        )

        result = subprocess.run(
            ["git", "write-tree"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        new_tree = result.stdout.strip()

        result = subprocess.run(
            [
                "git",
                "commit-tree",
                new_tree,
                "-p",
                base,
                "-m",
                f"Focused session for {slug}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    finally:
        Path(tmp_index_path).unlink()


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

    # Graceful degradation: if agent-core doesn't exist, treat as clean
    result = subprocess.run(
        ["git", "-C", "agent-core", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    submodule_status = result.stdout if result.returncode == 0 else ""

    combined = parent_status + submodule_status

    exempt_filenames = {"session.md", "jobs.md", "learnings.md"}
    filtered_lines = []
    for line in combined.rstrip().split("\n"):
        if not line:
            continue
        tokens = line.split()
        if len(tokens) >= 2:
            filepath = tokens[-1]
            filename = Path(filepath).name
            if filename in exempt_filenames and filepath.startswith("agents/"):
                continue
        filtered_lines.append(line)
    filtered_output = "\n".join(filtered_lines)

    if filtered_output:
        click.echo(filtered_output)
        raise SystemExit(1)


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
    worktree_path = Path(f"wt/{slug}")

    # Check for directory collision
    if worktree_path.exists():
        click.echo(f"Error: existing directory {worktree_path}", err=True)
        raise SystemExit(1)

    # Check for branch collision
    result = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        click.echo(f"Error: existing branch {slug}", err=True)
        raise SystemExit(1)

    try:
        if session:
            branch_commit = _create_session_commit(slug, base, session)
            subprocess.run(
                ["git", "branch", slug, branch_commit],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), slug],
                check=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), "-b", slug, base],
                check=True,
                capture_output=True,
            )

        # Initialize submodules in the new worktree
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        project_root = result.stdout.strip()

        # Get the agent-core path (if submodule exists in parent)
        agent_core_local = Path(project_root) / "agent-core"
        if agent_core_local.exists() and (agent_core_local / ".git").exists():
            # Use git submodule update with --reference to use local objects
            # This avoids fetching from remote
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(worktree_path),
                    "submodule",
                    "update",
                    "--init",
                    "--reference",
                    str(agent_core_local),
                ],
                check=False,
                capture_output=True,
            )

            # Create and checkout branch in submodule matching the worktree slug
            submodule_path = worktree_path / "agent-core"
            if submodule_path.exists():
                result = subprocess.run(
                    ["git", "-C", str(submodule_path), "checkout", "-B", slug],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    click.echo(result.stderr, err=True)
                    raise SystemExit(1)

        click.echo(str(worktree_path))
    except subprocess.CalledProcessError as e:
        click.echo(f"Error creating worktree: {e.stderr}", err=True)
        raise SystemExit(1) from e


@worktree.command(name="add-commit")
@click.argument("files", nargs=-1, required=True)
def add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit with message from stdin.

    Idempotent: exits 0 silently if nothing staged. If staged changes exist,
    reads commit message from stdin and outputs commit hash to stdout.
    """
    subprocess.run(
        ["git", "add", *list(files)],
        check=True,
    )

    result = subprocess.run(
        ["git", "diff", "--quiet", "--cached"],
        check=False,
    )
    has_staged = result.returncode == 1

    if has_staged:
        message = click.get_text_stream("stdin").read()
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(result.stdout.strip())


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
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "status", "--porcelain"],
            check=False,
            capture_output=True,
            text=True,
        )
        has_uncommitted = bool(result.stdout.strip())
        if has_uncommitted:
            click.echo(f"Warning: {slug} has uncommitted changes")

        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree_path)],
            check=True,
            capture_output=True,
        )
    else:
        # Worktree directory doesn't exist; prune stale registration
        subprocess.run(
            ["git", "worktree", "prune"],
            check=True,
            capture_output=True,
        )

    result = subprocess.run(
        ["git", "branch", "-D", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        click.echo(result.stderr)

    click.echo(f"Removed worktree {slug}")
