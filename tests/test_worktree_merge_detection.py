"""Tests for merge commit detection functions in git_ops."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from claudeutils.worktree.git_ops import _is_merge_commit, _is_merge_of


def test_detects_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects merge commit via parent count."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Root commit (0 parents) is not a merge commit
    assert not _is_merge_commit()

    # Normal commit (1 parent) is not a merge commit
    (repo_path / "second.txt").write_text("second")
    subprocess.run(["git", "add", "second.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Second commit"], check=True, capture_output=True
    )
    assert not _is_merge_commit()

    # Create another branch and merge to create merge commit
    subprocess.run(
        ["git", "checkout", "-b", "feature"], check=True, capture_output=True
    )
    (repo_path / "feature.txt").write_text("feature content")
    subprocess.run(["git", "add", "feature.txt"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Feature commit"], check=True, capture_output=True
    )
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "feature"], check=True, capture_output=True
    )

    # Merge commit has 2 parents
    assert _is_merge_commit()


def test_is_merge_of_distinguishes_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """_is_merge_of returns True only when slug's branch is a merge parent."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create and merge "feature-a"
    subprocess.run(
        ["git", "checkout", "-b", "feature-a"], check=True, capture_output=True
    )
    (repo_path / "a.txt").write_text("a")
    subprocess.run(["git", "add", "a.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add a"], check=True, capture_output=True)
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "feature-a"], check=True, capture_output=True
    )

    assert _is_merge_commit()
    assert _is_merge_of("feature-a")
    assert not _is_merge_of("feature-b")  # branch doesn't exist — not a parent

    # Create "feature-b" (not merged) — verify it's not identified as merge parent
    subprocess.run(
        ["git", "checkout", "-b", "feature-b"], check=True, capture_output=True
    )
    (repo_path / "b.txt").write_text("b")
    subprocess.run(["git", "add", "b.txt"], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add b"], check=True, capture_output=True)
    subprocess.run(["git", "checkout", "main"], check=True, capture_output=True)

    # HEAD is still the merge of feature-a, not feature-b
    assert _is_merge_of("feature-a")
    assert not _is_merge_of("feature-b")
