"""Tests for worktree rm subcommand."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import _is_merge_commit, worktree


def _create_worktree(
    repo_path: Path, slug: str, init_repo: Callable[[Path], None]
) -> Path:
    """Create worktree and return its path."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", slug])
    assert result.exit_code == 0
    container_path = repo_path.parent / f"{repo_path.name}-wt"
    return container_path / slug


def _branch_exists(name: str) -> bool:
    """Check if branch exists."""
    result = subprocess.run(
        ["git", "branch", "--list", name],
        capture_output=True,
        text=True,
        check=True,
    )
    return name in result.stdout


def test_rm_basic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Removes worktree directory and branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "removed" in result.output.lower()


def test_rm_dirty_warning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Warns about uncommitted changes but proceeds with removal."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    (worktree_path / "newfile.txt").write_text("uncommitted")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
    assert not _branch_exists("test-feature")
    assert "uncommitted" in result.output.lower() or "warning" in result.output.lower()


def test_rm_branch_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Cleans up branch when directory removed externally."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert _branch_exists("test-feature")

    subprocess.run(["rm", "-rf", str(worktree_path)], check=True, capture_output=True)
    assert not worktree_path.exists()
    assert _branch_exists("test-feature")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0
    assert not _branch_exists("test-feature")
    assert (
        "error" not in result.output.lower()
        or "no such file" not in result.output.lower()
    )


def test_rm_detects_merge_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Detects merge commit via parent count."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Normal commit has 1 parent
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


def test_rm_amends_merge_commit_when_session_modified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """When rm() is called on merge commit, amends session.md if modified."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    # Create a worktree task entry in session.md
    session_file = repo_path / "agents" / "session.md"
    session_file.parent.mkdir(exist_ok=True)
    session_file.write_text(
        "## Worktree Tasks\n\n- [ ] **Task One** → `test-feature` — description\n"
    )
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session"], check=True, capture_output=True
    )

    # Create merge commit by branching, making a change, and merging
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

    # Verify we're on a merge commit
    assert _is_merge_commit()
    # Get parent commits to verify merge structure is preserved
    subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip().split()
    merge_msg = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Create and setup worktree
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    # Run rm command
    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "test-feature"])

    assert result.exit_code == 0

    # Verify still on a merge commit (2+ parents)
    assert _is_merge_commit()

    # Verify commit message unchanged (--no-edit preserves message)
    current_msg = subprocess.run(
        ["git", "log", "-1", "--format=%B"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert current_msg == merge_msg

    # Verify session.md was staged and amended into HEAD commit
    session_content = subprocess.run(
        ["git", "show", "HEAD:agents/session.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    # Task should be removed from Worktree Tasks
    assert "test-feature" not in session_content
