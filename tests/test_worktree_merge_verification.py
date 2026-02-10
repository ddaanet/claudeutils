"""Tests for worktree merge post-verification logic."""

import subprocess
from pathlib import Path

import pytest


def _init_git_repo(repo_path: Path) -> None:
    """Initialize a basic git repository."""
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def test_merge_phase_2_post_verification_success(
    tmp_path: Path,
) -> None:
    """Verify post-verification validates ancestry after submodule merge.

    When post-merge verification checks both original commits against final
    HEAD, it should confirm both are ancestors (indicating successful merge).
    This test manually merges submodule history and verifies the ancestry check
    logic.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Setup basic submodule structure
    _init_git_repo(repo_path)

    # Create initial agent-core with commit
    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    _init_git_repo(agent_core_path)

    (agent_core_path / "core.txt").write_text("initial")
    subprocess.run(
        ["git", "add", "core.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial core"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    initial_commit = git_result.stdout.strip()

    # Create parent submodule commit (diverge from initial)
    (agent_core_path / "parent.txt").write_text("parent")
    subprocess.run(
        ["git", "add", "parent.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    parent_commit = git_result.stdout.strip()

    # Create worktree submodule commits (branch from initial)
    subprocess.run(
        ["git", "checkout", "-b", "wt-branch", initial_commit],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    (agent_core_path / "wt.txt").write_text("worktree")
    subprocess.run(
        ["git", "add", "wt.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    wt_commit = git_result.stdout.strip()

    # Merge wt-branch into main (creating a merge commit that includes both parents)
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "merge", "--no-edit", "wt-branch"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    final_head = git_result.stdout.strip()

    # Post-verification: both original commits should be ancestors
    # Verify parent commit is ancestor
    ancestry_result = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            parent_commit,
            final_head,
        ],
        check=False,
    )
    assert ancestry_result.returncode == 0, (
        f"Parent commit {parent_commit[:7]} should be ancestor of {final_head[:7]}"
    )

    # Verify worktree commit is ancestor
    ancestry_result = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            wt_commit,
            final_head,
        ],
        check=False,
    )
    assert ancestry_result.returncode == 0, (
        f"Worktree commit {wt_commit[:7]} should be ancestor of {final_head[:7]}"
    )


def test_merge_phase_2_post_verification_corrupted(
    tmp_path: Path,
) -> None:
    """Verify post-verification detects corrupted merge state.

    If submodule HEAD is reset to wrong commit (not including both parents),
    post-verification should detect ancestry failure and exit with error.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Setup basic submodule structure
    _init_git_repo(repo_path)

    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    _init_git_repo(agent_core_path)

    (agent_core_path / "core.txt").write_text("initial")
    subprocess.run(
        ["git", "add", "core.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial core"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    initial_commit = git_result.stdout.strip()

    # Create parent submodule commit
    (agent_core_path / "parent.txt").write_text("parent")
    subprocess.run(
        ["git", "add", "parent.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    parent_commit = git_result.stdout.strip()

    # Create worktree branch
    subprocess.run(
        ["git", "checkout", "-b", "wt-branch", initial_commit],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    (agent_core_path / "wt.txt").write_text("worktree")
    subprocess.run(
        ["git", "add", "wt.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=agent_core_path,
        capture_output=True,
        text=True,
        check=True,
    )
    wt_commit = git_result.stdout.strip()

    # Merge wt-branch into main
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    subprocess.run(
        ["git", "merge", "--no-edit", "wt-branch"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    # Corrupt: reset to initial commit (neither parent is ancestor of this state)
    subprocess.run(
        ["git", "reset", "--hard", initial_commit],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    # Post-verification should detect that original commits are NOT ancestors
    # Verify parent commit is NOT ancestor of corrupted HEAD
    ancestry_result = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            parent_commit,
            "HEAD",
        ],
        check=False,
    )
    assert ancestry_result.returncode != 0, (
        "Parent commit should NOT be ancestor of corrupted state"
    )

    # Verify worktree commit is NOT ancestor of corrupted HEAD
    ancestry_result = subprocess.run(
        [
            "git",
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            wt_commit,
            "HEAD",
        ],
        check=False,
    )
    assert ancestry_result.returncode != 0, (
        "Worktree commit should NOT be ancestor of corrupted state"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
