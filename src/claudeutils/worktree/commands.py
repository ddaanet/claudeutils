"""Worktree subcommand implementations."""

import os
import subprocess
import tempfile
from pathlib import Path

import click

from claudeutils.worktree.merge_helpers import (
    apply_theirs_resolution,
    capture_untracked_files,
    parse_precommit_failures,
    run_git,
)
from claudeutils.worktree.merge_phases import (
    merge_phase_1_prechecks,
    merge_phase_2_submodule,
    merge_phase_3_commit_and_precommit,
    merge_phase_3_parent,
)

__all__ = [
    "apply_theirs_resolution",
    "capture_untracked_files",
    "cmd_add_commit",
    "cmd_clean_tree",
    "cmd_ls",
    "cmd_merge",
    "cmd_new",
    "cmd_rm",
    "create_session_commit",
    "get_dirty_files",
    "parse_precommit_failures",
]


def get_dirty_files() -> str:
    """Return porcelain-format dirty files, excluding session context files."""
    parent_status = run_git(["status", "--porcelain"]).stdout
    result = run_git(["-C", "agent-core", "status", "--porcelain"], check=False)
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

        blob_hash = run_git(
            ["hash-object", "-w", "--stdin"], stdin_input=session_content
        ).stdout.strip()
        base_tree = run_git(["rev-parse", f"{base}^{{tree}}"]).stdout.strip()

        run_git(["read-tree", base_tree], env=env)
        run_git(
            [
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob_hash},agents/session.md",
            ],
            env=env,
        )

        new_tree = run_git(["write-tree"], env=env).stdout.strip()
        return run_git(
            ["commit-tree", new_tree, "-p", base, "-m", f"Focused session for {slug}"]
        ).stdout.strip()
    finally:
        Path(tmp_index_path).unlink()


def cmd_ls() -> None:
    """List active worktrees."""
    main_path = run_git(["rev-parse", "--show-toplevel"]).stdout.strip()
    result = run_git(["worktree", "list", "--porcelain"])
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

    if worktree_path.exists():
        click.echo(f"Error: existing directory {worktree_path}", err=True)
        raise SystemExit(1)

    if run_git(["rev-parse", "--verify", slug], check=False).returncode == 0:
        click.echo(f"Error: existing branch {slug}", err=True)
        raise SystemExit(1)

    try:
        if session:
            branch_commit = create_session_commit(slug, base, session)
            run_git(["branch", slug, branch_commit])
            run_git(["worktree", "add", str(worktree_path), slug])
        else:
            run_git(["worktree", "add", str(worktree_path), "-b", slug, base])

        project_root = run_git(["rev-parse", "--show-toplevel"]).stdout.strip()
        agent_core_local = Path(project_root) / "agent-core"

        if agent_core_local.exists() and (agent_core_local / ".git").exists():
            run_git(
                [
                    "-C",
                    str(worktree_path),
                    "submodule",
                    "update",
                    "--init",
                    "--reference",
                    str(agent_core_local),
                ],
                check=False,
            )

            submodule_path = worktree_path / "agent-core"
            if submodule_path.exists():
                result = run_git(
                    ["-C", str(submodule_path), "checkout", "-B", slug], check=False
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
    run_git(["add", *list(files)])
    has_staged = run_git(["diff", "--quiet", "--cached"], check=False).returncode == 1

    if has_staged:
        message = click.get_text_stream("stdin").read()
        result = run_git(["commit", "-m", message])
        click.echo(result.stdout.strip())


def cmd_rm(slug: str) -> None:
    """Remove worktree and branch (forced).

    Handles branch-only cleanup.
    """
    worktree_path = Path(f"wt/{slug}")

    if worktree_path.exists():
        result = run_git(
            ["-C", str(worktree_path), "status", "--porcelain"], check=False
        )
        if result.stdout.strip():
            click.echo(f"Warning: {slug} has uncommitted changes")

        run_git(["worktree", "remove", "--force", str(worktree_path)])
    else:
        run_git(["worktree", "prune"])

    result = run_git(["branch", "-D", slug], check=False)
    if result.returncode != 0 and "not found" not in result.stderr.lower():
        click.echo(result.stderr)

    click.echo(f"Removed worktree {slug}")


def cmd_merge(slug: str, message: str = "") -> None:
    """Merge worktree branch.

    Phase 1: clean tree, branch, worktree directory checks.
    Phase 2: submodule resolution with no-divergence optimization.
    Phase 3: parent merge with conflict resolution and precommit gate.
    """
    merge_in_progress, worktree_path = merge_phase_1_prechecks(slug)

    if not merge_in_progress:
        merge_phase_2_submodule(slug, worktree_path)

    merge_phase_3_parent(slug)
    merge_phase_3_commit_and_precommit(slug, message)
