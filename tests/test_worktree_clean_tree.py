"""Tests for worktree clean-tree and add-commit commands."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_clean_tree_session_files_exempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean-tree exits 0 when only session context files are modified.

    Integration test verifying that agents/session.md, agents/jobs.md, and
    agents/learnings.md are exempted from dirty tree checks.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize main repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )

    # Create initial commit with session files
    (repo_path / "README.md").write_text("test")
    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n")
    (agents_dir / "jobs.md").write_text("# Jobs\n")
    (agents_dir / "learnings.md").write_text("# Learnings\n")
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Initialize submodule (agent-core)
    submodule_path = repo_path / "agent-core"
    submodule_path.mkdir()
    subprocess.run(["git", "init"], cwd=submodule_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    (submodule_path / "README.md").write_text("submodule")
    subprocess.run(
        ["git", "add", "README.md"], cwd=submodule_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule initial"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )

    # Add submodule to main repo
    subprocess.run(
        ["git", "submodule", "add", str(submodule_path), "agent-core"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Modify session files
    (agents_dir / "session.md").write_text("# Session\nModified\n")
    (agents_dir / "jobs.md").write_text("# Jobs\nModified\n")
    (agents_dir / "learnings.md").write_text("# Learnings\nModified\n")

    # Run clean-tree command
    runner = CliRunner()
    result = runner.invoke(worktree, ["clean-tree"])

    # Should exit 0 silently (session files exempted)
    assert result.exit_code == 0
    assert result.output == ""


def test_clean_tree_clean(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Clean-tree exits 0 with no output in clean repo with submodule.

    Integration test creating real git repos with submodule to verify command
    behavior.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize main repo
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

    # Initialize submodule (agent-core)
    submodule_path = repo_path / "agent-core"
    submodule_path.mkdir()
    subprocess.run(["git", "init"], cwd=submodule_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    (submodule_path / "README.md").write_text("submodule")
    subprocess.run(
        ["git", "add", "README.md"], cwd=submodule_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule initial"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )

    # Add submodule to main repo
    subprocess.run(
        ["git", "submodule", "add", str(submodule_path), "agent-core"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Run clean-tree command
    runner = CliRunner()
    result = runner.invoke(worktree, ["clean-tree"])

    assert result.exit_code == 0
    assert result.output == ""


def test_clean_tree_dirty_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clean-tree exits 1 and prints dirty source files.

    When source files are modified, clean-tree should print the dirty files in
    porcelain format and exit 1. Session context files are exempt.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize main repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )

    # Create initial commit with source and session files
    src_dir = repo_path / "src" / "claudeutils"
    src_dir.mkdir(parents=True)
    (src_dir / "cli.py").write_text('"""Main CLI module."""\n')
    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n")
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Initialize submodule
    submodule_path = repo_path / "agent-core"
    submodule_path.mkdir()
    subprocess.run(["git", "init"], cwd=submodule_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    (submodule_path / "README.md").write_text("submodule")
    subprocess.run(
        ["git", "add", "README.md"], cwd=submodule_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule initial"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )

    # Add submodule
    subprocess.run(
        ["git", "submodule", "add", str(submodule_path), "agent-core"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Modify source file and session file
    (src_dir / "cli.py").write_text('"""Main CLI module."""\nprint("hello")\n')
    (agents_dir / "session.md").write_text("# Session\nModified\n")

    # Run clean-tree command
    runner = CliRunner()
    result = runner.invoke(worktree, ["clean-tree"])

    # Should exit 1 with dirty file list
    assert result.exit_code == 1
    assert " M src/claudeutils/cli.py" in result.output


def test_add_commit_nothing_staged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Add-commit with no staged changes exits 0 with no output.

    In a clean repo, add-commit should exit 0 silently when nothing is staged.
    This idempotent behavior is critical for merge flow.
    """
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

    # Create agents directory and session file, then commit it
    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n")
    subprocess.run(["git", "add", "agents/session.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session file"], check=True, capture_output=True
    )

    # Run add-commit with message from stdin (nothing staged - file unchanged)
    runner = CliRunner()
    result = runner.invoke(
        worktree,
        ["add-commit", "agents/session.md"],
        input="Test commit message\n",
    )

    # Should exit 0 with empty output (idempotent no-op)
    assert result.exit_code == 0
    assert result.output == ""
