"""Tests for worktree merge subcommand."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def _init_git_repo(repo_path: Path) -> None:
    """Initialize a basic git repository.

    Args:
        repo_path: Root directory for the git repository.
    """
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


def _setup_repo_with_submodule(repo_path: Path) -> None:
    """Set up a test repo with a simulated submodule (gitlink).

    Args:
        repo_path: Root directory for the test repository.
    """
    _init_git_repo(repo_path)

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(
        ["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create agent-core submodule
    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    _init_git_repo(agent_core_path)

    (agent_core_path / "core.txt").write_text("core content")
    subprocess.run(
        ["git", "add", "core.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial core commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    # Create .gitmodules
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
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", ".gitmodules"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add .gitignore with wt/ entry
    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(
        ["git", "add", ".gitignore"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add gitignore"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def test_merge_phase_2_no_divergence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge optimizes when submodule pointers match (no divergence).

    When a worktree submodule is at the same commit as the parent, Phase 2
    should detect this and skip all submodule operations, proceeding directly to
    Phase 3 (parent merge).
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    # Create worktree with submodule initialized at same commit as parent
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    # Make a change in the parent branch (non-overlapping with submodule)
    (repo_path / "new_file.txt").write_text("parent change")
    subprocess.run(
        ["git", "add", "new_file.txt"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent change"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Make a change in the worktree branch (non-overlapping)
    (worktree_path / "worktree_file.txt").write_text("worktree change")
    subprocess.run(
        ["git", "add", "worktree_file.txt"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree change"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Get original submodule commit before merge
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    original_parent_submodule_pointer = git_result.stdout.strip()

    # (Commit count before merge not needed for Phase 2 verification)

    # Now invoke merge
    # This should detect that submodule pointers match and skip Phase 2
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])

    # Merge should exit 0 (Phase 1 checks pass, Phase 2 optimizes, Phase 3 proceeds)
    # Phase 3 may or may not complete depending on implementation
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify Phase 2 skip was detected and logged
    assert "skipped" in merge_result.output.lower(), (
        f"Expected skip in output, got: {merge_result.output}"
    )

    # Verify submodule pointer unchanged (Phase 2 was skipped)
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    final_submodule_pointer = git_result.stdout.strip()

    assert final_submodule_pointer == original_parent_submodule_pointer

    # Verify no submodule fetch/merge commands were executed
    # This is implicit: if Phase 2 skipped, no submodule operations occurred
    # We can verify by checking that the submodule object store wasn't updated
    # (in a real merge, we'd see fetch refs and merge commits)

    # If merge proceeds to Phase 3, merge commit may be created
    # (Phase 3 implementation is next cycle, so this is expected to not change yet)
    # At minimum, Phase 2 optimization should not create any commits
    # Phase 3 would create merge commit (handled in next cycle)
    # For this cycle, we verify Phase 2 skipped (output message is proof)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
