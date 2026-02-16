"""Tests for worktree merge error handling."""

import subprocess
from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.merge import _format_git_error
from claudeutils.worktree.utils import _git


def test_format_git_error_includes_stderr() -> None:
    """Error formatter extracts stderr from CalledProcessError."""
    e = subprocess.CalledProcessError(
        returncode=128,
        cmd=["git", "add", "nonexistent.txt"],
        stderr="fatal: pathspec 'nonexistent.txt' did not match any files\n",
    )
    result = _format_git_error(e)
    assert "git add nonexistent.txt" in result
    assert "Exit code: 128" in result
    assert "pathspec 'nonexistent.txt' did not match any files" in result
    assert "Resolve the issue and retry" in result


def test_format_git_error_handles_missing_stderr() -> None:
    """Error formatter handles CalledProcessError without stderr."""
    e = subprocess.CalledProcessError(
        returncode=1,
        cmd=["git", "status"],
        stderr=None,
    )
    result = _format_git_error(e)
    assert "git status" in result
    assert "Exit code: 1" in result
    assert "(no error output)" in result


def test_merge_cli_surfaces_git_error(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """CLI merge command surfaces git error without traceback."""
    # Create a git repo
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    (repo / "file.txt").write_text("content")
    subprocess.run(
        ["git", "add", "file.txt"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial"], cwd=repo, check=True, capture_output=True
    )

    # Change to repo directory
    monkeypatch.chdir(repo)

    # Run merge on non-existent branch
    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "nonexistent-branch"])

    # Should fail with clean error (not traceback)
    # Exit code 2 = branch not found (per merge.py:182)
    assert result.exit_code == 2
    assert "Branch nonexistent-branch not found" in result.output
    assert "Traceback" not in result.output


def test_git_helper_preserves_stderr_in_exception(tmp_path: Path) -> None:
    """_git() raises CalledProcessError with stderr populated."""
    # Create a git repo
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)

    # Try to add non-existent file
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        _git("-C", str(repo), "add", "nonexistent.txt")

    # Verify stderr is present
    assert exc_info.value.stderr is not None
    assert (
        "pathspec" in exc_info.value.stderr.lower()
        or "did not match" in exc_info.value.stderr.lower()
    )


def test_merge_conflict_surfaces_git_error(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """Merge with conflict surfaces git error, not traceback."""
    # Create a git repo with conflicting changes
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Create file on main
    (repo / "file.txt").write_text("main content")
    subprocess.run(
        ["git", "add", "file.txt"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Main"], cwd=repo, check=True, capture_output=True
    )

    # Create branch with different content
    subprocess.run(
        ["git", "checkout", "-b", "branch"], cwd=repo, check=True, capture_output=True
    )
    (repo / "file.txt").write_text("branch content")
    subprocess.run(
        ["git", "add", "file.txt"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Branch"], cwd=repo, check=True, capture_output=True
    )

    # Go back to main and create conflicting change
    subprocess.run(
        ["git", "checkout", "main"], cwd=repo, check=True, capture_output=True
    )
    (repo / "file.txt").write_text("different main content")
    subprocess.run(
        ["git", "add", "file.txt"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Main 2"], cwd=repo, check=True, capture_output=True
    )

    # Change to repo directory
    monkeypatch.chdir(repo)

    # Attempt merge - should fail with conflict
    runner = CliRunner()
    result = runner.invoke(worktree, ["merge", "branch"])

    # Should report conflict, not crash with traceback
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    # Either clean error message or conflict abort message
    assert "conflict" in result.output.lower() or "aborted" in result.output.lower()
