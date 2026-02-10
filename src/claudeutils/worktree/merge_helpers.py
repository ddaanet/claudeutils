"""Helper functions for worktree merge operations."""

import re
import subprocess
from pathlib import Path

import click

from claudeutils.worktree.conflicts import (
    resolve_jobs_conflict,
    resolve_learnings_conflict,
    resolve_session_conflict,
)


def run_git(
    args: list[str],
    *,
    check: bool = True,
    env: dict[str, str] | None = None,
    stdin_input: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run git command with common defaults."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
        env=env,
        input=stdin_input,
    )


def capture_untracked_files() -> set[str]:
    """Capture current untracked files."""
    result = run_git(["status", "--porcelain"])
    untracked = set()
    for line in result.stdout.strip().split("\n"):
        if line.startswith("??"):
            tokens = line.split()
            if len(tokens) >= 2:
                untracked.add(tokens[-1])
    return untracked


def parse_precommit_failures(stderr_output: str) -> list[str]:
    """Parse precommit stderr to extract failed file paths."""
    failed_files = []
    patterns = [
        r"^([^:]+):\s+FAILED",
        r"^([^:]+):\s+Error",
        r"^([^:]+)\s+\(.*\)\s+failed",
    ]

    for line in stderr_output.split("\n"):
        if not line.strip():
            continue
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                filepath = match.group(1)
                if filepath and filepath not in failed_files:
                    failed_files.append(filepath)
                break

    return failed_files


def apply_theirs_resolution(failed_files: list[str]) -> bool:
    """Apply theirs resolution to failed files.

    Returns True if all resolved.
    """
    for filepath in failed_files:
        if run_git(["checkout", "--theirs", filepath], check=False).returncode != 0:
            return False
        if run_git(["add", filepath], check=False).returncode != 0:
            return False
    return True


def get_dirty_files_helper() -> str:
    """Get dirty files without circular import."""
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
    dirty_files = get_dirty_files_helper()
    if dirty_files:
        click.echo(
            "Error: uncommitted changes prevent merge (session files exempt):",
            err=True,
        )
        click.echo(dirty_files, err=True)
        raise SystemExit(1)


def resolve_conflicts(conflict_files: list[str], slug: str) -> bool:
    """Resolve conflicts in session context files.

    Returns True if all resolved.
    """
    conflict_resolver_map = {
        "agents/session.md": lambda ours, theirs: resolve_session_conflict(
            ours, theirs, slug=slug
        ),
        "agents/learnings.md": resolve_learnings_conflict,
        "agents/jobs.md": resolve_jobs_conflict,
    }

    for filepath in conflict_files:
        resolver = conflict_resolver_map.get(filepath)
        if not resolver:
            return False

        ours_content = run_git(["show", f":2:{filepath}"]).stdout
        theirs_content = run_git(["show", f":3:{filepath}"]).stdout

        resolved = resolver(ours_content, theirs_content)
        Path(filepath).write_text(resolved)
        run_git(["add", filepath])

    return True
