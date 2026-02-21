"""Tests for worktree rm amend safety — verifies amend targets correct merge."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.git_ops import _is_merge_commit
from tests.fixtures_worktree import _create_worktree


def test_rm_does_not_amend_wrong_branch_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Rm must not amend HEAD when merge commit is from a different branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task for "other-wt"
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `other-wt` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # Create and merge "merged-branch" (a DIFFERENT branch, not "other-wt")
    subprocess.run(
        ["git", "checkout", "-b", "merged-branch"], check=True, capture_output=True
    )
    (repo_path / "merged.txt").write_text("merged content")
    subprocess.run(["git", "add", "merged.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Merged branch commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "merged-branch"], check=True, capture_output=True
    )

    assert _is_merge_commit()

    # Create worktree for "other-wt" (not the branch that was merged)
    worktree_path = _create_worktree(repo_path, "other-wt", init_repo)
    assert worktree_path.exists()

    # Record HEAD commit hash before rm
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "other-wt"])
    assert result.exit_code == 0

    # HEAD should NOT have been amended — commit hash unchanged
    head_after = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert head_before == head_after
    assert "amend" not in result.output.lower()


def test_rm_force_does_not_amend_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """--force rm must never amend, even when HEAD is a merge commit."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create session.md with worktree task
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `force-wt` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # Create and merge a different branch to make HEAD a merge commit
    subprocess.run(
        ["git", "checkout", "-b", "some-feature"], check=True, capture_output=True
    )
    (repo_path / "feature.txt").write_text("feature")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Feature"], check=True, capture_output=True)
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "some-feature"], check=True, capture_output=True
    )

    assert _is_merge_commit()

    # Create worktree for force-wt (never merged)
    worktree_path = _create_worktree(repo_path, "force-wt", init_repo)
    assert worktree_path.exists()

    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--force", "force-wt"])
    assert result.exit_code == 0

    # HEAD must not be amended
    head_after = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert head_before == head_after
    assert "amend" not in result.output.lower()
