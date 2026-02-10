"""Tests for worktree merge subcommand Phase 2 optimization."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


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


def _setup_repo_with_submodule(repo_path: Path) -> None:
    """Set up a test repo with a simulated submodule (gitlink)."""
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

    # Create gitlink entry in index
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

    # Create .gitmodules
    gitmodules_path = repo_path / ".gitmodules"
    gitmodules_path.write_text(
        '[submodule "agent-core"]\n\tpath = agent-core\n\turl = ./agent-core\n'
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

    # Add .gitignore
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

    # Create minimal justfile for precommit validation
    justfile = repo_path / "justfile"
    justfile.write_text("precommit:\n    exit 0\n")
    subprocess.run(
        ["git", "add", "justfile"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Add minimal justfile"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def test_merge_phase_2_no_divergence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge optimizes when submodule pointers match."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    # Create worktree
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    # Make parent change
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

    # Make worktree change
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

    # Get original submodule pointer
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    original_pointer = git_result.stdout.strip()

    # Invoke merge
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify Phase 2 was skipped
    assert "skipped" in merge_result.output.lower()

    # Verify submodule pointer unchanged
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    final_pointer = git_result.stdout.strip()

    assert final_pointer == original_pointer


def test_merge_phase_2_fast_forward(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge optimizes when local includes worktree submodule."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    # Create worktree
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    # Advance parent's submodule
    agent_core_path = repo_path / "agent-core"
    (agent_core_path / "parent_addition.txt").write_text("parent submodule change")
    subprocess.run(
        ["git", "add", "parent_addition.txt"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent submodule commit"],
        cwd=agent_core_path,
        check=True,
        capture_output=True,
    )

    # Stage new submodule pointer
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update parent submodule pointer"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Make worktree change
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

    # Get submodule commits
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    parent_pointer = git_result.stdout.strip()

    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
        check=True,
    )
    worktree_pointer = git_result.stdout.strip()

    # Verify ancestry
    ancestry_result = subprocess.run(
        [
            "git",
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

    # Invoke merge
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify Phase 2 was skipped with ancestor mention
    assert "skipped" in merge_result.output.lower()
    output_lower = merge_result.output.lower()
    assert (
        "ancestor" in output_lower
        or "fast-forward" in output_lower
        or "included" in output_lower
    )

    # Verify pointer unchanged
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD:agent-core"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    final_pointer = git_result.stdout.strip()

    assert final_pointer == parent_pointer


def test_merge_phase_2_diverged_commits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge with diverged submodule commits."""


def test_merge_phase_3_session_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Resolve conflicts in session.md, learnings.md, jobs.md.

    Tests deterministic conflict resolution in merge context.
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    # Add session.md, learnings.md, jobs.md to parent
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

    subprocess.run(
        ["git", "add", "agents/"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session context files"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    # Make changes in worktree: add new task, new learning, update plan status
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

    subprocess.run(
        ["git", "add", "agents/"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree updates to session files"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Make conflicting changes in parent
    # Different new task, new learning, and status update
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

    subprocess.run(
        ["git", "add", "agents/"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent updates to session files"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Invoke merge - should detect and resolve conflicts
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify conflicts were resolved:
    # 1. session.md should have both tasks
    merged_session = (repo_path / "agents" / "session.md").read_text()
    assert "Initial task" in merged_session
    assert "Worktree task" in merged_session
    assert "Parent task" in merged_session

    # 2. learnings.md should have both new learnings
    merged_learnings = (repo_path / "agents" / "learnings.md").read_text()
    assert "Initial learning" in merged_learnings
    assert "Worktree learning" in merged_learnings
    assert "Parent learning" in merged_learnings

    # 3. jobs.md should have higher status (planned > designed)
    merged_jobs = (repo_path / "agents" / "jobs.md").read_text()
    assert "| test-plan | planned |" in merged_jobs

    # 4. No unresolved conflicts should remain
    git_result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert git_result.stdout.strip() == "", f"Unresolved conflicts: {git_result.stdout}"


def test_merge_phase_3_clean_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify parent merge with no conflicts."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    # Create worktree
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"
    assert worktree_path.exists()

    # Make parent change (different file)
    (repo_path / "parent_file.txt").write_text("parent change")
    subprocess.run(
        ["git", "add", "parent_file.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent change"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Make worktree change (different file)
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

    # Invoke merge
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify merge commit exists
    git_result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    log_output = git_result.stdout.strip()
    assert "🔀 Merge wt/test-feature" in log_output

    # Verify both branches' changes are integrated
    git_result = subprocess.run(
        ["git", "ls-tree", "HEAD", "-r"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    tree_output = git_result.stdout
    assert "parent_file.txt" in tree_output
    assert "worktree_file.txt" in tree_output

    # Test custom message
    (worktree_path / "worktree_file2.txt").write_text("worktree change 2")
    subprocess.run(
        ["git", "add", "worktree_file2.txt"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree change 2"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    (repo_path / "parent_file2.txt").write_text("parent change 2")
    subprocess.run(
        ["git", "add", "parent_file2.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent change 2"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    merge_result = runner.invoke(
        worktree, ["merge", "test-feature", "--message", "Integrate test feature"]
    )
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify custom message
    git_result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    log_output = git_result.stdout.strip()
    assert "🔀 Integrate test feature" in log_output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
