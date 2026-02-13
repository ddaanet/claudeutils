"""Tests for worktree merge operations."""

import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_merge_submodule_ancestry(
    repo_with_submodule: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge performs submodule commit ancestry check.

    Ancestry check logic:
    - Extract worktree's submodule commit from git ls-tree
    - Get local submodule commit via rev-parse
    - Check if worktree commit is ancestor of local (skips if yes)
    """
    monkeypatch.chdir(repo_with_submodule)

    (repo_with_submodule / ".gitignore").write_text("wt/\n")
    subprocess.run(
        ["git", "add", ".gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "branch", "test-feature"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    agent_core_path = repo_with_submodule / "agent-core"
    initial_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    (agent_core_path / "change.txt").write_text("submodule change")
    subprocess.run(
        ["git", "add", "change.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule change"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    new_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert initial_commit != new_commit

    result = subprocess.run(
        ["git", "ls-tree", "test-feature", "--", "agent-core"],
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
        check=True,
    )
    wt_submodule_commit = result.stdout.split()[2]

    assert wt_submodule_commit == initial_commit

    result = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            wt_submodule_commit,
            new_commit,
        ],
        check=False,
    )
    is_ancestor = result.returncode == 0
    assert is_ancestor

    mock_git = MagicMock()
    with patch("claudeutils.worktree.merge._git", mock_git):
        mock_git.return_value = ""
        result = CliRunner().invoke(worktree, ["merge", "test-feature"])
        assert result.exit_code == 0

        ls_tree_called = any("ls-tree" in str(call) for call in mock_git.call_args_list)
        assert ls_tree_called, "merge should extract submodule commit via git ls-tree"
