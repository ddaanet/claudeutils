"""Commit pipeline: staging, validation, commit execution."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from claudeutils.session.commit import CommitInput


@dataclass
class CommitResult:
    """Result of commit pipeline execution."""

    success: bool
    output: str


def _run_precommit(cwd: Path | None = None) -> tuple[bool, str]:
    """Run ``just precommit`` and return (passed, output).

    Patchable in tests.
    """
    result = subprocess.run(
        ["just", "precommit"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0, result.stdout.strip()


def _stage_files(files: list[str], *, cwd: Path | None = None) -> None:
    """Stage listed files via git add."""
    subprocess.run(
        ["git", "add", "--", *files],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


def _git_commit(message: str, *, cwd: Path | None = None) -> str:
    """Run git commit and return output."""
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def commit_pipeline(
    ci: CommitInput,
    *,
    cwd: Path | None = None,
) -> CommitResult:
    """Execute commit pipeline: stage, validate, commit."""
    _stage_files(ci.files, cwd=cwd)

    passed, precommit_output = _run_precommit(cwd=cwd)
    if not passed:
        return CommitResult(
            success=False,
            output=f"**Precommit:** failed\n\n{precommit_output}",
        )

    if ci.message is None:
        return CommitResult(
            success=False,
            output="**Error:** No commit message provided",
        )

    commit_output = _git_commit(ci.message, cwd=cwd)
    return CommitResult(success=True, output=commit_output)
