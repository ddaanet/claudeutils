"""Worktree subcommand implementations."""

import os
import subprocess
import tempfile
from pathlib import Path

import click


def get_dirty_files() -> str:
    """Return porcelain-format dirty files, excluding session context files."""
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
    return "\n".join(filtered_lines)


def check_clean_tree() -> None:
    """Validate clean tree, exempting session context files.

    Exits 1 if dirty.
    """
    dirty_files = get_dirty_files()
    if dirty_files:
        click.echo(
            "Error: uncommitted changes prevent merge (session files exempt):",
            err=True,
        )
        click.echo(dirty_files, err=True)
        raise SystemExit(1)


def create_session_commit(slug: str, base: str, session: str) -> str:
    """Pre-commit session.md via isolated temp index."""
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


def cmd_ls() -> None:
    """List active worktrees."""
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


def cmd_clean_tree() -> None:
    """Validate clean tree, excluding session files.

    Exit 0 if clean, 1 if dirty.
    """
    dirty_files = get_dirty_files()
    if dirty_files:
        click.echo(dirty_files)
        raise SystemExit(1)


def cmd_new(slug: str, base: str, session: str) -> None:
    """Create worktree with optional pre-committed session."""
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
            branch_commit = create_session_commit(slug, base, session)
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


def cmd_add_commit(files: tuple[str, ...]) -> None:
    """Stage files and commit (idempotent).

    Reads message from stdin if staged.
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


def cmd_rm(slug: str) -> None:
    """Remove worktree and branch (forced).

    Handles branch-only cleanup (idempotent).
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


def cmd_merge(slug: str) -> None:
    """Merge worktree branch.

    Phase 1: clean tree, branch, worktree directory checks.
    Phase 2: submodule resolution with no-divergence optimization.
    """
    # Phase 1: Pre-checks
    check_clean_tree()

    # Validate branch exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        click.echo(f"Error: branch {slug} not found", err=True)
        raise SystemExit(1)

    # Warn if worktree directory missing but continue
    worktree_path = Path(f"wt/{slug}")
    if not worktree_path.exists():
        click.echo(f"Warning: worktree directory {worktree_path} not found", err=True)

    # Phase 2: Submodule resolution with no-divergence optimization
    # Extract worktree submodule commit pointer using git ls-tree
    result = subprocess.run(
        ["git", "ls-tree", slug, "--", "agent-core"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0 and result.stdout.strip():
        # Parse "160000 commit <sha>    agent-core"
        parts = result.stdout.strip().split()
        if len(parts) >= 3 and parts[0] == "160000":
            wt_submodule_commit = parts[2]

            # Extract local submodule commit using git -C agent-core rev-parse HEAD
            result = subprocess.run(
                ["git", "-C", "agent-core", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                local_submodule_commit = result.stdout.strip()

                # Compare commits - if equal, skip to Phase 3
                if wt_submodule_commit == local_submodule_commit:
                    short_sha = wt_submodule_commit[:7]
                    msg = f"Submodule agent-core: skipped (no divergence, {short_sha})"
                    click.echo(msg, err=True)
                    # Phase 3 would be implemented in next cycle
                    return
