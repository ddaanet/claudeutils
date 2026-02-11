"""Tests for worktree merge Phase 2 (submodule resolution)."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from tests.conftest_git import run_git, setup_repo_with_submodule


def test_merge_phase_2_no_divergence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge optimizes when submodule pointers match."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    (repo_path / "new_file.txt").write_text("parent change")
    run_git(["add", "new_file.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent change"], cwd=repo_path, check=True)

    (worktree_path / "worktree_file.txt").write_text("worktree change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree change"], cwd=worktree_path, check=True)

    original_pointer = run_git(
        ["rev-parse", "HEAD:agent-core"], cwd=repo_path, check=True
    ).stdout.strip()

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    assert "skipped" in merge_result.output.lower()

    final_pointer = run_git(
        ["rev-parse", "HEAD:agent-core"], cwd=repo_path, check=True
    ).stdout.strip()
    assert final_pointer == original_pointer


def test_merge_phase_2_fast_forward(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge optimizes when local includes worktree submodule."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    agent_core_path = repo_path / "agent-core"

    (agent_core_path / "parent_addition.txt").write_text("parent submodule change")
    run_git(["add", "parent_addition.txt"], cwd=agent_core_path, check=True)
    run_git(
        ["commit", "-m", "Parent submodule commit"], cwd=agent_core_path, check=True
    )

    run_git(["add", "agent-core"], cwd=repo_path, check=True)
    run_git(
        ["commit", "-m", "Update parent submodule pointer"], cwd=repo_path, check=True
    )

    (worktree_path / "worktree_file.txt").write_text("worktree change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree change"], cwd=worktree_path, check=True)

    parent_pointer = run_git(
        ["rev-parse", "HEAD:agent-core"], cwd=repo_path, check=True
    ).stdout.strip()
    worktree_pointer = run_git(
        ["rev-parse", "HEAD:agent-core"], cwd=worktree_path, check=True
    ).stdout.strip()

    ancestry_result = run_git(
        [
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            worktree_pointer,
            parent_pointer,
        ],
        check=False,
    )
    assert ancestry_result.returncode == 0

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    assert "skipped" in merge_result.output.lower()
    output_lower = merge_result.output.lower()
    assert (
        "ancestor" in output_lower
        or "fast-forward" in output_lower
        or "included" in output_lower
    )

    final_pointer = run_git(
        ["rev-parse", "HEAD:agent-core"], cwd=repo_path, check=True
    ).stdout.strip()
    assert final_pointer == parent_pointer


def test_merge_phase_2_diverged_commits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge with diverged submodule commits.

    Fetches and merges both histories, verifies both original commits are
    ancestors.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    agent_core_path = repo_path / "agent-core"
    worktree_ac_path = worktree_path / "agent-core"

    initial_commit = run_git(
        ["rev-parse", "HEAD"], cwd=agent_core_path, check=True
    ).stdout.strip()

    (agent_core_path / "parent_file.txt").write_text("parent submodule change")
    run_git(["add", "parent_file.txt"], cwd=agent_core_path, check=True)
    run_git(
        ["commit", "-m", "Parent submodule commit"], cwd=agent_core_path, check=True
    )
    parent_commit = run_git(
        ["rev-parse", "HEAD"], cwd=agent_core_path, check=True
    ).stdout.strip()

    run_git(["add", "agent-core"], cwd=repo_path, check=True)
    run_git(
        ["commit", "-m", "Update parent submodule pointer"], cwd=repo_path, check=True
    )

    run_git(["checkout", initial_commit], cwd=worktree_ac_path, check=True)
    (worktree_ac_path / "worktree_file.txt").write_text("worktree submodule change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_ac_path, check=True)
    run_git(
        ["commit", "-m", "Worktree submodule commit"], cwd=worktree_ac_path, check=True
    )
    wt_commit = run_git(
        ["rev-parse", "HEAD"], cwd=worktree_ac_path, check=True
    ).stdout.strip()

    run_git(["add", "agent-core"], cwd=worktree_path, check=True)
    run_git(
        ["commit", "-m", "Update worktree submodule pointer"],
        cwd=worktree_path,
        check=True,
    )

    (worktree_path / "worktree_file.txt").write_text("worktree parent change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree parent change"], cwd=worktree_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    assert "merged" in merge_result.output.lower()

    final_head = run_git(
        ["rev-parse", "HEAD"], cwd=agent_core_path, check=True
    ).stdout.strip()

    wt_ancestor = run_git(
        [
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            wt_commit,
            final_head,
        ],
        check=False,
    )
    assert wt_ancestor.returncode == 0

    parent_ancestor = run_git(
        [
            "-C",
            str(agent_core_path),
            "merge-base",
            "--is-ancestor",
            parent_commit,
            final_head,
        ],
        check=False,
    )
    assert parent_ancestor.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
