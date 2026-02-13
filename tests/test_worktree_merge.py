"""Tests for worktree merge operations."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_branch_existence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Verify branch exists and warn about missing worktree directory."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)
    init_repo(repo_path)

    # Test 1: Branch doesn't exist
    result = CliRunner().invoke(worktree, ["merge", "nonexistent-branch"])
    assert result.exit_code == 2
    assert "Branch nonexistent-branch not found" in result.output

    # Test 2: Branch exists but worktree directory doesn't
    subprocess.run(["git", "branch", "branch-only"], check=True, capture_output=True)
    result = CliRunner().invoke(worktree, ["merge", "branch-only"])
    assert result.exit_code == 0
    assert "Worktree directory not found, merging branch only" in result.output

    # Test 3: Both branch and worktree directory exist
    subprocess.run(["git", "branch", "full-merge"], check=True, capture_output=True)
    result = CliRunner().invoke(worktree, ["new", "full-merge"])
    assert result.exit_code == 0

    result = CliRunner().invoke(worktree, ["merge", "full-merge"])
    assert result.exit_code == 0
    assert "Worktree directory not found" not in result.output
