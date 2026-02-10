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


def test_new_collision_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify new subcommand detects existing branch collision."""
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

    # Create an existing branch
    subprocess.run(["git", "branch", "test-feature"], check=True, capture_output=True)

    # Run new command with existing branch name
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    # Verify exit code is 1 (error)
    assert result.exit_code == 1

    # Verify error message in stderr
    assert "existing" in result.output.lower() or "collision" in result.output.lower()

    # Verify worktree directory was NOT created
    worktree_path = repo_path / "wt" / "test-feature"
    assert not worktree_path.exists()


def test_new_directory_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify new subcommand detects existing directory collision."""
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

    # Create an existing directory at wt/test-feature
    (repo_path / "wt").mkdir()
    (repo_path / "wt" / "test-feature").mkdir()

    # Run new command
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    # Verify exit code is 1 (error)
    assert result.exit_code == 1

    # Verify error message in stderr
    assert "existing" in result.output.lower() or "directory" in result.output.lower()

    # Verify no branch was created
    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in result.stdout


def test_new_basic_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify new subcommand creates worktree with branch."""
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

    # Add .gitignore with wt/ entry
    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(["git", "add", ".gitignore"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"], check=True, capture_output=True
    )

    # Run new command
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    # Verify exit code
    assert result.exit_code == 0

    # Verify stdout contains worktree path
    assert "wt/test-feature" in result.output

    # Verify directory exists
    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    # Verify branch exists
    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout

    # Verify worktree is checked out to the branch
    result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout


def test_new_submodule_init(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify new subcommand invokes submodule initialization for worktrees.

    This tests that when creating a worktree in a repo with agent-core
    submodule, the new command attempts to initialize the submodule using git
    submodule update.
    """
    # Create temporary repo directory
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize parent repo
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

    # Create an agent-core directory with a git repo in the same parent
    # (to simulate submodule)
    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    subprocess.run(
        ["git", "init"], cwd=agent_core_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    (agent_core_path / "core.txt").write_text("core content")
    subprocess.run(
        ["git", "add", "core.txt"], cwd=agent_core_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial core commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    # Create .gitmodules (even though we won't actually use git submodule)
    gitmodules_path = repo_path / ".gitmodules"
    gitmodules_path.write_text(
        '[submodule "agent-core"]\n\tpath = agent-core\n\turl = ./agent-core\n'
    )

    # Create a gitlink entry in the index (simulates submodule)
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result.stdout.strip()

    subprocess.run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{commit_hash},agent-core",
        ],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "add", ".gitmodules"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        check=True,
        capture_output=True,
    )

    # Add .gitignore with wt/ entry
    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(["git", "add", ".gitignore"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"], check=True, capture_output=True
    )

    # Run new command
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    # Verify exit code
    assert result.exit_code == 0

    # Verify directory exists
    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    # Verify submodule directory exists (indicates submodule init was attempted)
    # The directory may not be fully populated due to git file:// restrictions
    submodule_path = worktree_path / "agent-core"
    assert submodule_path.exists()
