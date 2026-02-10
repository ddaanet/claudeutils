"""Tests for worktree CLI module."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import derive_slug, worktree


def test_package_import() -> None:
    """Verify that worktree package can be imported."""
    assert worktree is not None


def test_worktree_command_group() -> None:
    """Verify _worktree command group displays help output."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["--help"])
    assert result.exit_code == 0
    assert "_worktree" in result.output


def test_derive_slug() -> None:
    """Verify derive_slug transforms task names to valid worktree slugs."""
    assert derive_slug("Implement ambient awareness") == "implement-ambient-awareness"
    assert derive_slug("Design runbook identifiers") == "design-runbook-identifiers"
    assert (
        derive_slug("Review agent-core orphaned revisions")
        == "review-agent-core-orphaned-rev"
    )
    assert derive_slug("Multiple    spaces   here") == "multiple-spaces-here"
    assert derive_slug("Special!@#$%chars") == "special-chars"
    # Mid-word truncation creating trailing hyphen
    assert derive_slug("A" * 35 + "test") == "a" * 30


def test_ls_empty() -> None:
    """Verify ls exits 0 with empty output when no worktrees exist."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])
    assert result.exit_code == 0
    assert result.output == ""


def test_ls_multiple_worktrees(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify ls parses and outputs multiple worktrees with slug extraction."""
    # Create a temporary git repo
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize git repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Create two worktree branches and worktrees
    subprocess.run(["git", "branch", "task-a"], check=True, capture_output=True)
    subprocess.run(["git", "branch", "task-b"], check=True, capture_output=True)

    # Create worktrees
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

    # Run ls command
    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])

    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert len(lines) == 2

    # Parse output lines
    line_a = lines[0].split("\t")
    line_b = lines[1].split("\t")

    # Verify first line
    assert line_a[0] == "task-a"
    assert line_a[1] == "refs/heads/task-a"
    assert str(worktree_a) in line_a[2]

    # Verify second line
    assert line_b[0] == "task-b"
    assert line_b[1] == "refs/heads/task-b"
    assert str(worktree_b) in line_b[2]


def test_new_session_precommit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify new --session flag pre-commits focused session to worktree branch.

    Tests that session file content is committed to the branch before worktree
    creation.
    """
    # Create a temporary git repo
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize git repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Create focused session file
    session_file = tmp_path / "test-session.md"
    session_file.write_text("# Focused Session\n\nTask content")

    # Run new command with --session
    runner = CliRunner()
    result = runner.invoke(
        worktree, ["new", "test-feature", "--session", str(session_file)]
    )
    assert result.exit_code == 0

    # Verify worktree exists
    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    # Verify session.md was committed to branch
    session_md_path = worktree_path / "agents" / "session.md"
    assert session_md_path.exists()
    assert session_md_path.read_text() == "# Focused Session\n\nTask content"

    # Verify branch has one commit ahead of HEAD
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD..test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    commits_ahead = int(result.stdout.strip())
    assert commits_ahead == 1

    # Verify main worktree index is unmodified
    result = subprocess.run(
        ["git", "diff", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout == ""

    # Verify commit message
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    commit_msg = result.stdout.strip()
    assert commit_msg == "Focused session for test-feature"
