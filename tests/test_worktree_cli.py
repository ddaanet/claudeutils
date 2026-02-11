"""Tests for worktree CLI module."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from tests.conftest_git import init_repo


def test_package_import() -> None:
    """Verifies module loads."""
    assert worktree is not None


def test_worktree_command_group() -> None:
    """Help output includes command group name."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["--help"])
    assert result.exit_code == 0
    assert "_worktree" in result.output


def test_ls_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty output when no worktrees exist."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])
    assert result.exit_code == 0
    assert result.output == ""


def test_ls_multiple_worktrees(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Parses porcelain output and extracts slug from path."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    subprocess.run(["git", "branch", "task-a"], check=True, capture_output=True)
    subprocess.run(["git", "branch", "task-b"], check=True, capture_output=True)

    worktree_a = repo_path / "wt" / "task-a"
    worktree_b = repo_path / "wt" / "task-b"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_a), "task-a"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "worktree", "add", str(worktree_b), "task-b"],
        check=True,
        capture_output=True,
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])

    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert len(lines) == 2

    line_a = lines[0].split("\t")
    line_b = lines[1].split("\t")

    assert line_a[0] == "task-a"
    assert line_a[1] == "refs/heads/task-a"
    assert str(worktree_a) in line_a[2]

    assert line_b[0] == "task-b"
    assert line_b[1] == "refs/heads/task-b"
    assert str(worktree_b) in line_b[2]


def test_new_session_precommit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Session file committed to worktree branch before worktree creation."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)

    session_file = tmp_path / "test-session.md"
    session_file.write_text("# Focused Session\n\nTask content")

    runner = CliRunner()
    result = runner.invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    session_md_path = worktree_path / "agents" / "session.md"
    assert session_md_path.exists()
    assert session_md_path.read_text() == "# Focused Session\n\nTask content"

    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD..test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    commits_ahead = int(result.stdout.strip())
    assert commits_ahead == 1

    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""

    result = subprocess.run(
        ["git", "log", "-1", "--format=%s", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_msg = result.stdout.strip()
    assert commit_msg == "Focused session for test-feature"
