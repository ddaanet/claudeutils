"""Tests for worktree new subcommand."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from tests.conftest_git import init_repo, setup_repo_with_submodule


def test_new_collision_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify new subcommand detects existing branch collision."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path, with_commit=False)

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

    assert result.exit_code == 1
    assert "existing" in result.output.lower() or "collision" in result.output.lower()
    assert not (repo_path / "wt" / "test-feature").exists()


def test_new_directory_collision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify new subcommand detects existing directory collision."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path, with_commit=False)

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Create an existing directory at wt/test-feature
    (repo_path / "wt").mkdir()
    (repo_path / "wt" / "test-feature").mkdir()

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 1
    assert "existing" in result.output.lower() or "directory" in result.output.lower()

    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" not in result.stdout


def test_new_slug_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject invalid slug formats."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path, with_commit=False)
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial"], check=True, capture_output=True
    )

    runner = CliRunner()

    invalid_slugs = [
        ("", "empty string", 1),
        ("..", "path traversal", 1),
        ("/foo", "absolute path", 1),
        ("../foo", "relative path", 1),
        ("foo/bar", "directory separator", 1),
        ("Foo", "uppercase", 1),
        ("foo_bar", "underscore", 1),
        ("foo bar", "space", 1),
        ("foo!bar", "special char", 1),
        ("-foo", "leading hyphen", 2),  # Click intercepts as option
        ("foo-", "trailing hyphen", 1),
    ]

    for slug, description, expected_exit in invalid_slugs:
        result = runner.invoke(worktree, ["new", slug])
        assert (
            result.exit_code == expected_exit
        ), f"Expected rejection for {description}: {slug}"
        if expected_exit == 1:
            assert "invalid slug" in result.output.lower()


def test_new_basic_flow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify new subcommand creates worktree with branch."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path, with_commit=False)

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

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0
    assert "wt/test-feature" in result.output

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    result = subprocess.run(
        ["git", "branch", "--list", "test-feature"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout

    result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout


def test_new_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify new subcommand initializes submodule and creates branch.

    When creating a worktree in a repo with agent-core submodule:
    - Submodule is initialized via git submodule update
    - Submodule is on a branch matching the worktree slug (not detached HEAD)
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])

    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()
    assert worktree_path.is_dir()

    submodule_path = worktree_path / "agent-core"
    assert submodule_path.exists()

    result = subprocess.run(
        [
            "git",
            "-C",
            str(submodule_path),
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    branch_name = result.stdout.strip()
    assert branch_name == "test-feature"

    result = subprocess.run(
        ["git", "-C", str(submodule_path), "branch", "--list"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "test-feature" in result.stdout
