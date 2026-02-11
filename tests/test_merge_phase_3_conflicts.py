"""Tests for worktree merge Phase 3 conflict resolution."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.merge_phases import merge_phase_3_parent
from tests.conftest_git import run_git, setup_repo_with_submodule


def test_merge_idempotent_resume_after_conflict_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge can be resumed after manual conflict resolution."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    conflict_file = repo_path / "conflict.txt"
    conflict_file.write_text("parent version\n")
    run_git(["add", "conflict.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add conflict file on parent"], cwd=repo_path, check=True)

    wt_conflict = worktree_path / "conflict.txt"
    wt_conflict.write_text("worktree version\n")
    run_git(["add", "conflict.txt"], cwd=worktree_path, check=True)
    run_git(
        ["commit", "-m", "Modify conflict file on worktree"],
        cwd=worktree_path,
        check=True,
    )

    (repo_path / "parent_only.txt").write_text("parent-only content")
    run_git(["add", "parent_only.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent-only change"], cwd=repo_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 1, (
        f"Expected merge failure with conflicts, got: {merge_result.output}"
    )
    assert "Merge conflicts detected" in merge_result.output

    merge_head_check = run_git(["rev-parse", "--verify", "MERGE_HEAD"], check=False)
    assert merge_head_check.returncode == 0, (
        "MERGE_HEAD should exist after failed merge"
    )

    resolved_content = "worktree version (resolved)\n"
    wt_conflict.write_text(resolved_content)
    assert wt_conflict.read_text() == resolved_content

    run_git(["add", "conflict.txt"], cwd=repo_path, check=True)

    conflict_check = run_git(
        ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path, check=True
    )
    assert conflict_check.stdout.strip() == "", (
        f"File should not be conflicted after staging, but got: {conflict_check.stdout}"
    )

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, (
        f"Merge after manual resolution should succeed, got: {merge_result.output}"
    )

    log_result = run_git(["log", "--oneline", "-1"], cwd=repo_path, check=True)
    assert "🔀 Merge wt/test-feature" in log_result.stdout

    tree_result = run_git(["ls-tree", "HEAD", "-r"], cwd=repo_path, check=True)
    assert "parent_only.txt" in tree_result.stdout
    assert "conflict.txt" in tree_result.stdout

    merge_head_check = run_git(["rev-parse", "--verify", "MERGE_HEAD"], check=False)
    assert merge_head_check.returncode != 0, (
        "MERGE_HEAD should not exist after successful merge completion"
    )


def test_merge_phase_3_session_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resolve conflicts in session.md, learnings.md, jobs.md."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    session_content = """# Session

## Pending Tasks

- [ ] **Initial task** — some metadata

## Blockers / Gotchas

None yet.
"""
    learnings_content = """# Learnings

## Initial learning

First learning text.
"""
    jobs_content = """# Jobs

| Plan | Status |
|------|--------|
| test-plan | requirements |
"""

    (repo_path / "agents" / "session.md").parent.mkdir(exist_ok=True)
    (repo_path / "agents" / "session.md").write_text(session_content)
    (repo_path / "agents" / "learnings.md").write_text(learnings_content)
    (repo_path / "agents" / "jobs.md").write_text(jobs_content)

    run_git(["add", "agents/"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add session context files"], cwd=repo_path, check=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    worktree_session = """# Session

## Pending Tasks

- [ ] **Initial task** — some metadata
- [ ] **Worktree task** — worktree metadata

## Blockers / Gotchas

None yet.
"""
    worktree_learnings = """# Learnings

## Initial learning

First learning text.

## Worktree learning

Worktree learning text.
"""
    worktree_jobs = """# Jobs

| Plan | Status |
|------|--------|
| test-plan | designed |
"""

    (worktree_path / "agents" / "session.md").write_text(worktree_session)
    (worktree_path / "agents" / "learnings.md").write_text(worktree_learnings)
    (worktree_path / "agents" / "jobs.md").write_text(worktree_jobs)

    run_git(["add", "agents/"], cwd=worktree_path, check=True)
    run_git(
        ["commit", "-m", "Worktree updates to session files"],
        cwd=worktree_path,
        check=True,
    )

    parent_session = """# Session

## Pending Tasks

- [ ] **Initial task** — some metadata
- [ ] **Parent task** — parent metadata

## Blockers / Gotchas

None yet.
"""
    parent_learnings = """# Learnings

## Initial learning

First learning text.

## Parent learning

Parent learning text.
"""
    parent_jobs = """# Jobs

| Plan | Status |
|------|--------|
| test-plan | planned |
"""

    (repo_path / "agents" / "session.md").write_text(parent_session)
    (repo_path / "agents" / "learnings.md").write_text(parent_learnings)
    (repo_path / "agents" / "jobs.md").write_text(parent_jobs)

    run_git(["add", "agents/"], cwd=repo_path, check=True)
    run_git(
        ["commit", "-m", "Parent updates to session files"], cwd=repo_path, check=True
    )

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    merged_session = (repo_path / "agents" / "session.md").read_text()
    assert "Initial task" in merged_session
    assert "Worktree task" in merged_session
    assert "Parent task" in merged_session

    merged_learnings = (repo_path / "agents" / "learnings.md").read_text()
    assert "Initial learning" in merged_learnings
    assert "Worktree learning" in merged_learnings
    assert "Parent learning" in merged_learnings

    merged_jobs = (repo_path / "agents" / "jobs.md").read_text()
    assert "| test-plan | planned |" in merged_jobs

    conflict_check = run_git(
        ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path, check=True
    )
    assert conflict_check.stdout.strip() == "", (
        f"Unresolved conflicts: {conflict_check.stdout}"
    )


def test_merge_phase_3_clean_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify parent merge with no conflicts."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    (repo_path / "parent_file.txt").write_text("parent change")
    run_git(["add", "parent_file.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent change"], cwd=repo_path, check=True)

    (worktree_path / "worktree_file.txt").write_text("worktree change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree change"], cwd=worktree_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    log_result = run_git(["log", "--oneline", "-1"], cwd=repo_path, check=True)
    assert "🔀 Merge wt/test-feature" in log_result.stdout.strip()

    tree_result = run_git(["ls-tree", "HEAD", "-r"], cwd=repo_path, check=True)
    assert "parent_file.txt" in tree_result.stdout
    assert "worktree_file.txt" in tree_result.stdout

    (worktree_path / "worktree_file2.txt").write_text("worktree change 2")
    run_git(["add", "worktree_file2.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree change 2"], cwd=worktree_path, check=True)

    (repo_path / "parent_file2.txt").write_text("parent change 2")
    run_git(["add", "parent_file2.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent change 2"], cwd=repo_path, check=True)

    merge_result = runner.invoke(
        worktree, ["merge", "test-feature", "--message", "Integrate test feature"]
    )
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    log_result = run_git(["log", "--oneline", "-1"], cwd=repo_path, check=True)
    assert "🔀 Integrate test feature" in log_result.stdout.strip()


def test_merge_debris_cleanup_before_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify clean_merge_debris removes untracked files before merge attempt."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    # Add new file in worktree branch that will appear in incoming diff
    new_file = worktree_path / "new_feature.txt"
    new_file.write_text("new feature content\n")
    run_git(["add", "new_feature.txt"], cwd=worktree_path, check=True)
    run_git(
        ["commit", "-m", "Add new feature file"],
        cwd=worktree_path,
        check=True,
    )

    # Create untracked debris file in parent that conflicts with incoming
    debris_file = repo_path / "new_feature.txt"
    debris_file.write_text("debris content\n")

    # Verify debris exists before merge
    assert debris_file.exists(), "Debris file should exist before merge"
    status_result = run_git(["status", "--porcelain"], cwd=repo_path, check=True)
    assert (
        "?? new_feature.txt" in status_result.stdout
        or "new_feature.txt" in status_result.stdout
    ), f"Debris should be untracked, got: {status_result.stdout}"

    # Invoke merge_phase_3_parent directly (bypasses clean tree check)
    # This exercises clean_merge_debris before merge attempt
    merge_phase_3_parent("test-feature")

    # Verify the staged file has incoming content, not debris content
    assert debris_file.exists(), "File should exist after merge"
    final_content = debris_file.read_text()
    assert final_content == "new feature content\n", (
        f"File should have incoming content (debris was cleaned). Got: {final_content}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
