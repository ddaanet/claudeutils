"""Helper functions for worktree merge operations."""

import re
from pathlib import Path

from claudeutils.worktree.conflicts import (
    resolve_jobs_conflict,
    resolve_learnings_conflict,
    resolve_session_conflict,
)
from claudeutils.worktree.git_utils import run_git


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

    During active merge (MERGE_HEAD exists): uses --theirs.
    Post-commit (MERGE_HEAD consumed): uses HEAD^2 (second parent).
    Returns True if all resolved.
    """
    in_merge = (
        run_git(["rev-parse", "--verify", "MERGE_HEAD"], check=False).returncode == 0
    )
    for filepath in failed_files:
        if in_merge:
            cmd = ["checkout", "--theirs", filepath]
        else:
            cmd = ["checkout", "HEAD^2", "--", filepath]
        if run_git(cmd, check=False).returncode != 0:
            return False
        if run_git(["add", filepath], check=False).returncode != 0:
            return False
    return True


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
