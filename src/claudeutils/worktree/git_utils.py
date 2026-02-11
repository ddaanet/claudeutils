"""Git utility functions for worktree operations."""

import subprocess
import time
from pathlib import Path

import click


def run_git(
    args: list[str],
    *,
    check: bool = True,
    env: dict[str, str] | None = None,
    stdin_input: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run git command with common defaults and lock file retry logic."""
    max_retries = 2
    retry_delay = 1.0

    for attempt in range(max_retries + 1):
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
            env=env,
            input=stdin_input,
        )

        if result.returncode == 0 or not check:
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode, ["git", *args], result.stdout, result.stderr
                )
            return result

        is_lock_error = (
            "index.lock" in result.stderr or "Unable to create" in result.stderr
        )

        if is_lock_error and attempt < max_retries:
            time.sleep(retry_delay)
            continue

        if check:
            raise subprocess.CalledProcessError(
                result.returncode, ["git", *args], result.stdout, result.stderr
            )
        return result

    return result


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
