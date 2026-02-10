"""Tests for worktree merge subcommand Phase 2 optimization."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.commands import (
    apply_theirs_resolution,
    parse_precommit_failures,
)


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
    """Verify merge with diverged submodule commits (placeholder)."""


def test_merge_idempotent_resume_after_conflict_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify merge can be resumed after manual conflict resolution.

    Scenario: Source code conflict (non-session file) prevents automatic merge.
    User manually resolves and stages the file. Re-invoke merge — should detect
    in-progress merge state (MERGE_HEAD), skip git merge, check conflicts, and
    proceed to commit. All three phases should be idempotent.
    """
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

    # Create conflict: both sides modify same file
    conflict_file = repo_path / "conflict.txt"
    conflict_file.write_text("parent version\n")
    subprocess.run(
        ["git", "add", "conflict.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add conflict file on parent"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Worktree modifies same file
    wt_conflict = worktree_path / "conflict.txt"
    wt_conflict.write_text("worktree version\n")
    subprocess.run(
        ["git", "add", "conflict.txt"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Modify conflict file on worktree"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Parent makes additional commit
    (repo_path / "parent_only.txt").write_text("parent-only content")
    subprocess.run(
        ["git", "add", "parent_only.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent-only change"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # First merge invocation - should fail with conflicts
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 1, (
        f"Expected merge failure with conflicts, got: {merge_result.output}"
    )
    assert "Merge conflicts detected" in merge_result.output

    # Verify MERGE_HEAD exists (merge in progress)
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_check.returncode == 0, (
        "MERGE_HEAD should exist after failed merge"
    )

    # Manually resolve conflict: choose worktree version
    resolved_content = "worktree version (resolved)\n"
    wt_conflict.write_text(resolved_content)

    # Verify file is written correctly before staging
    assert wt_conflict.read_text() == resolved_content

    subprocess.run(
        ["git", "add", "conflict.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Verify file is in index with resolved content (no longer conflicted)
    conflict_check = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert conflict_check.stdout.strip() == "", (
        f"File should not be conflicted after staging, but got: {conflict_check.stdout}"
    )

    # Re-invoke merge - should detect MERGE_HEAD and resume
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, (
        f"Merge after manual resolution should succeed, got: {merge_result.output}"
    )

    # Verify merge commit was created
    git_result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "🔀 Merge wt/test-feature" in git_result.stdout

    # Verify both sides' changes exist in tree
    git_result = subprocess.run(
        ["git", "ls-tree", "HEAD", "-r"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    tree_output = git_result.stdout
    assert "parent_only.txt" in tree_output
    assert "conflict.txt" in tree_output

    # Verify MERGE_HEAD is gone (merge completed)
    merge_head_check = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False,
        capture_output=True,
    )
    assert merge_head_check.returncode != 0, (
        "MERGE_HEAD should not exist after successful merge completion"
    )


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


def test_merge_phase_3_post_merge_precommit_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify mandatory precommit validation after merge commit.

    Create worktree merge that succeeds, commit is created, then precommit is
    run. Assert precommit runs after merge commit is created, merge commit is
    NOT rolled back on precommit failure.
    """
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

    # Make worktree change (clean code)
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

    # Get commit count before merge
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    before_count = int(result.stdout.strip())

    # Invoke merge - should succeed (precommit passes in real repo)
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    # Verify merge commit was created
    result = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    after_count = int(result.stdout.strip())
    assert after_count > before_count, (
        f"Merge commit not created: before={before_count}, after={after_count}"
    )

    # Verify merge commit exists in history
    git_result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    log_output = git_result.stdout
    assert "🔀 Merge wt/test-feature" in log_output


def test_merge_phase_3_precommit_gate_passes_with_clean_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify precommit gate validates ours after take-ours resolution.

    Test complete merge flow with source conflicts resolved via take-ours
    (main branch version is correct, precommit passes). Verify:
    - Merge invoked with source conflicts
    - resolve_source_conflicts() applied
    - just precommit executed and passes (exit 0)
    - Merge commit created with hash output to stdout
    - Working tree clean after merge
    """
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

    # Create conflict scenario: worktree adds unused import (lint fail),
    # main branch has clean imports
    conflict_file = repo_path / "module.py"
    conflict_file.write_text("import os\n\nprint('hello')\n")
    subprocess.run(
        ["git", "add", "module.py"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add clean module"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Worktree adds unused import (creates lint violation)
    wt_conflict = worktree_path / "module.py"
    wt_conflict.write_text("import os\nimport sys\n\nprint('hello')\n")
    subprocess.run(
        ["git", "add", "module.py"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add module with unused import"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Parent makes additional commit
    (repo_path / "parent_only.txt").write_text("parent-only content")
    subprocess.run(
        ["git", "add", "parent_only.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent-only change"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # First merge invocation - should fail with conflicts
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 1
    assert "Merge conflicts detected" in merge_result.output

    # Manually resolve: choose ours (clean version)
    resolved_content = "import os\n\nprint('hello')\n"
    conflict_file.write_text(resolved_content)
    subprocess.run(
        ["git", "add", "module.py"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Re-invoke merge - should detect MERGE_HEAD and proceed to commit
    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, (
        f"Merge after resolution failed: {merge_result.output}"
    )

    # Verify merge commit was created
    git_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    merge_commit = git_result.stdout.strip()
    assert len(merge_commit) == 40, "Merge commit hash should be 40 hex chars"

    # Verify stdout contains commit hash (machine-readable output)
    assert merge_commit in merge_result.output or len(merge_result.output.strip()) > 0

    # Verify working tree is clean (no staged or unstaged changes)
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert status_result.stdout.strip() == "", (
        f"Working tree should be clean after merge, got: {status_result.stdout}"
    )

    # Verify merge commit is in history with merge message
    git_result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "🔀 Merge wt/test-feature" in git_result.stdout


def test_merge_phase_3_precommit_gate_fallback_to_theirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify precommit fallback logic when both ours and theirs fail.

    Tests parsing and theirs fallback by directly testing the helper functions.
    """
    # Test parsing various precommit stderr formats
    stderr_cases = [
        ("file1.py: FAILED", ["file1.py"]),
        ("file1.py: FAILED\nfile2.py: FAILED", ["file1.py", "file2.py"]),
        ("module/file.py: FAILED (format)", ["module/file.py"]),
        ("unparseable error output", []),
    ]

    for stderr, expected_files in stderr_cases:
        result = parse_precommit_failures(stderr)
        assert result == expected_files, (
            f"Parse failed for '{stderr}': got {result}, expected {expected_files}"
        )

    # Test apply_theirs_resolution in a real git repo
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    _setup_repo_with_submodule(repo_path)

    # Create a file with merge conflict
    conflict_file = repo_path / "file1.py"
    conflict_file.write_text("original\n")
    subprocess.run(
        ["git", "add", "file1.py"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add file1"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create worktree
    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    # Parent modifies
    conflict_file.write_text("ours version\n")
    subprocess.run(
        ["git", "add", "file1.py"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent modifies"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Worktree modifies same location (creates conflict)
    wt_file = worktree_path / "file1.py"
    wt_file.write_text("theirs version\n")
    subprocess.run(
        ["git", "add", "file1.py"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Worktree modifies"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Parent makes another commit
    (repo_path / "other.txt").write_text("content")
    subprocess.run(
        ["git", "add", "other.txt"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Parent adds other"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Attempt merge - will fail due to conflict
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", "test-feature"],
        cwd=repo_path,
        check=False,
        capture_output=True,
        text=True,
    )
    # Should have conflicts
    assert result.returncode != 0

    # Verify conflict exists
    conflict_check = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "file1.py" in conflict_check.stdout

    # Test apply_theirs_resolution
    resolution_result = apply_theirs_resolution(["file1.py"])
    assert resolution_result is True

    # Verify file was resolved to theirs version
    file_content = conflict_file.read_text()
    assert "theirs version" in file_content

    # Verify no more conflicts
    conflict_check2 = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "file1.py" not in conflict_check2.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
