"""Tests for from_main direction support in the merge pipeline."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.merge import merge
from tests.fixtures_worktree import _run_git


def _setup_main_merged_into_branch(
    repo: Path, init_repo: Callable[[Path], None]
) -> None:
    """Set up repo where main is ancestor of HEAD.

    Creates a branch with one commit, merges main into it from the branch side.
    HEAD is on a branch that has main as an ancestor.
    """
    repo.mkdir(exist_ok=True)
    init_repo(repo)

    # Add a commit on main so it's non-trivial
    (repo / "main-file.txt").write_text("main content")
    _run_git(repo, "add", "main-file.txt")
    _run_git(repo, "commit", "-m", "main commit")

    # Create branch off main, add a commit
    _run_git(repo, "checkout", "-b", "feature")
    (repo / "feature.txt").write_text("feature content")
    _run_git(repo, "add", "feature.txt")
    _run_git(repo, "commit", "-m", "feature commit")

    # Return to main — now HEAD is on main, which is an ancestor of feature
    _run_git(repo, "checkout", "main")

    # Merge feature into main so main is ancestor of HEAD
    _run_git(repo, "merge", "--no-edit", "feature")


def test_merge_accepts_from_main_keyword(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    init_repo: Callable[[Path], None],
    mock_precommit: None,
) -> None:
    """Merge() accepts from_main=True keyword argument.

    When called as merge("main", from_main=True) on a repo where main is already
    an ancestor of HEAD (merged state), the function should accept the keyword
    without raising TypeError and return normally.
    """
    repo = tmp_path / "repo"
    _setup_main_merged_into_branch(repo, init_repo)
    monkeypatch.chdir(repo)

    # main is now merged (feature is ancestor), but we want main as the slug
    # Verify main is ancestor of HEAD
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", "main", "HEAD"],
        cwd=repo,
        check=False,
    )
    assert result.returncode == 0, "main should be ancestor of HEAD"

    exit_code = 0
    try:
        merge("main", from_main=True)
    except SystemExit as e:
        exit_code = e.code

    assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
