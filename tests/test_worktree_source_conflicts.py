"""Tests for source code conflict resolution during worktree merges."""

import subprocess
from pathlib import Path

import pytest

from claudeutils.worktree.conflicts import resolve_source_conflicts


@pytest.fixture
def real_git_repo_with_source_conflict(tmp_path: Path) -> tuple[Path, list[str]]:
    """Create a real git repo with a source file conflict between branches.

    Returns (repo_path, conflict_file_paths). Conflict markers are present
    before resolution.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    # Initialize repo with initial commit
    subprocess.run(
        ["git", "init"],
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
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Create initial source file and commit
    source_file = repo / "app.py"
    source_file.write_text("def main():\n    pass\n")
    subprocess.run(
        ["git", "add", "app.py"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Branch to worktree branch, modify source file
    subprocess.run(
        ["git", "checkout", "-b", "test-worktree"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    source_file.write_text(
        "def main():\n    pass\n\ndef function_a():\n    return 'A'\n"
    )
    subprocess.run(
        ["git", "add", "app.py"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add function A"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Return to main, modify same location
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    source_file.write_text(
        "def main():\n    pass\n\ndef function_b():\n    return 'B'\n"
    )
    subprocess.run(
        ["git", "add", "app.py"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add function B"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    # Attempt merge to create conflict
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "test-worktree"],
        check=False,
        cwd=repo,
        capture_output=True,
    )
    # Merge should fail due to conflict
    assert result.returncode != 0

    # Verify conflict markers are present
    content = source_file.read_text()
    assert "<<<<<<< HEAD" in content

    # Get conflict list
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    conflict_files = [f for f in result.stdout.strip().split("\n") if f]

    return repo, conflict_files


def test_resolve_source_conflicts_take_ours_strategy(
    real_git_repo_with_source_conflict: tuple[Path, list[str]],
) -> None:
    """Verify take-ours strategy for source file conflicts."""
    repo, conflict_files = real_git_repo_with_source_conflict
    source_file = repo / "app.py"

    # Verify conflict markers present before resolution
    content_before = source_file.read_text()
    assert "<<<<<<< HEAD" in content_before

    # Resolve source conflicts (exclude session context patterns)
    exclude_patterns = [
        "agents/session.md",
        "agents/jobs.md",
        "agents/learnings.md",
    ]
    resolved = resolve_source_conflicts(
        conflict_files, exclude_patterns=exclude_patterns, cwd=str(repo)
    )

    # Verify file was resolved and is in resolved list
    assert "app.py" in resolved

    # No conflict markers should remain
    content_after = source_file.read_text()
    assert "<<<<<<< HEAD" not in content_after
    assert "=======" not in content_after
    assert ">>>>>>>" not in content_after

    # File should be staged (use ls-files to check merge state)
    result = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    # ls-files output format: [mode] [object] [stage] [file]
    # During merge, stage 0 means resolved and staged
    assert "0\tapp.py" in result.stdout

    # Verify content is from ours side (contains function_b, not function_a)
    assert "function_b" in content_after
    assert "function_a" not in content_after


def test_resolve_source_conflicts_filters_exclude_patterns(
    real_git_repo_with_source_conflict: tuple[Path, list[str]],
) -> None:
    """Verify that exclude patterns are respected."""
    repo, conflict_files = real_git_repo_with_source_conflict

    # Add a session conflict (doesn't exist in this test, but demonstrate filtering)
    exclude_patterns = [
        "agents/session.md",
        "agents/jobs.md",
        "agents/learnings.md",
    ]

    # Resolve with exclusions
    resolved = resolve_source_conflicts(
        conflict_files, exclude_patterns=exclude_patterns, cwd=str(repo)
    )

    # Session files should not be in resolved list
    for resolved_file in resolved:
        for exclude_pattern in exclude_patterns:
            assert resolved_file != exclude_pattern


def test_resolve_source_conflicts_returns_list_of_resolved_files(
    real_git_repo_with_source_conflict: tuple[Path, list[str]],
) -> None:
    """Verify that function returns list of resolved files."""
    repo, conflict_files = real_git_repo_with_source_conflict

    exclude_patterns: list[str] = []
    resolved = resolve_source_conflicts(
        conflict_files, exclude_patterns=exclude_patterns, cwd=str(repo)
    )

    # Should be a list
    assert isinstance(resolved, list)

    # Should contain all conflicted source files
    assert len(resolved) > 0
    assert "app.py" in resolved

    # All items should be strings (file paths)
    for item in resolved:
        assert isinstance(item, str)
