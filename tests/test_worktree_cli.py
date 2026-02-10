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
    """Clean-tree exits 1 and prints dirty source files (not session files).

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
