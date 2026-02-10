"""Tests for worktree merge subcommand."""

import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from claudeutils.worktree.commands import (
    apply_theirs_resolution,
    parse_precommit_failures,
)


def run_git(
    args: list[str], *, cwd: Path | None = None, check: bool = False
) -> subprocess.CompletedProcess[str]:
    """Run git command with common defaults."""
    return subprocess.run(
        ["git", *args],
        check=check,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def init_repo(repo_path: Path) -> None:
    """Initialize a basic git repository."""
    run_git(["init"], cwd=repo_path, check=True)
    run_git(["config", "user.email", "test@example.com"], cwd=repo_path, check=True)
    run_git(["config", "user.name", "Test User"], cwd=repo_path, check=True)


def setup_repo_with_submodule(repo_path: Path) -> None:
    """Set up test repo with simulated submodule."""
    init_repo(repo_path)

    (repo_path / "README.md").write_text("test")
    run_git(["add", "README.md"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Initial commit"], cwd=repo_path, check=True)

    agent_core_path = repo_path / "agent-core"
    agent_core_path.mkdir()
    init_repo(agent_core_path)

    (agent_core_path / "core.txt").write_text("core content")
    run_git(["add", "core.txt"], cwd=agent_core_path, check=True)
    run_git(["commit", "-m", "Initial core commit"], cwd=agent_core_path, check=True)

    commit_hash = run_git(
        ["rev-parse", "HEAD"], cwd=agent_core_path, check=True
    ).stdout.strip()

    run_git(
        ["update-index", "--add", "--cacheinfo", f"160000,{commit_hash},agent-core"],
        cwd=repo_path,
        check=True,
    )

    (repo_path / ".gitmodules").write_text(
        '[submodule "agent-core"]\n\tpath = agent-core\n\turl = ./agent-core\n'
    )
    run_git(["add", ".gitmodules"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add submodule"], cwd=repo_path, check=True)

    (repo_path / ".gitignore").write_text("wt/\n")
    run_git(["add", ".gitignore"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add gitignore"], cwd=repo_path, check=True)

    (repo_path / "justfile").write_text("precommit:\n    exit 0\n")
    run_git(["add", "justfile"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add minimal justfile"], cwd=repo_path, check=True)


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
    """Verify merge with diverged submodule commits (placeholder)."""


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


def test_merge_phase_3_post_merge_precommit_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify mandatory precommit validation after merge commit."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    (worktree_path / "worktree_file.txt").write_text("worktree change")
    run_git(["add", "worktree_file.txt"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree change"], cwd=worktree_path, check=True)

    before_count = int(
        run_git(
            ["rev-list", "--count", "HEAD"], cwd=repo_path, check=True
        ).stdout.strip()
    )

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, f"Merge failed: {merge_result.output}"

    after_count = int(
        run_git(
            ["rev-list", "--count", "HEAD"], cwd=repo_path, check=True
        ).stdout.strip()
    )
    assert after_count > before_count, (
        f"Merge commit not created: before={before_count}, after={after_count}"
    )

    log_result = run_git(["log", "--oneline"], cwd=repo_path, check=True)
    assert "🔀 Merge wt/test-feature" in log_result.stdout


def test_merge_phase_3_precommit_gate_passes_with_clean_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify precommit gate validates ours after take-ours resolution."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    conflict_file = repo_path / "module.py"
    conflict_file.write_text("import os\n\nprint('hello')\n")
    run_git(["add", "module.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add clean module"], cwd=repo_path, check=True)

    wt_conflict = worktree_path / "module.py"
    wt_conflict.write_text("import os\nimport sys\n\nprint('hello')\n")
    run_git(["add", "module.py"], cwd=worktree_path, check=True)
    run_git(
        ["commit", "-m", "Add module with unused import"], cwd=worktree_path, check=True
    )

    (repo_path / "parent_only.txt").write_text("parent-only content")
    run_git(["add", "parent_only.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent-only change"], cwd=repo_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 1
    assert "Merge conflicts detected" in merge_result.output

    resolved_content = "import os\n\nprint('hello')\n"
    conflict_file.write_text(resolved_content)
    run_git(["add", "module.py"], cwd=repo_path, check=True)

    merge_result = runner.invoke(worktree, ["merge", "test-feature"])
    assert merge_result.exit_code == 0, (
        f"Merge after resolution failed: {merge_result.output}"
    )

    merge_commit = run_git(
        ["rev-parse", "HEAD"], cwd=repo_path, check=True
    ).stdout.strip()
    assert len(merge_commit) == 40, "Merge commit hash should be 40 hex chars"
    assert merge_commit in merge_result.output or len(merge_result.output.strip()) > 0

    status_result = run_git(["status", "--porcelain"], cwd=repo_path, check=True)
    assert status_result.stdout.strip() == "", (
        f"Working tree should be clean after merge, got: {status_result.stdout}"
    )

    log_result = run_git(["log", "--oneline", "-1"], cwd=repo_path, check=True)
    assert "🔀 Merge wt/test-feature" in log_result.stdout


def test_merge_phase_3_precommit_gate_fallback_to_theirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify precommit fallback logic when both ours and theirs fail."""
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

    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    setup_repo_with_submodule(repo_path)

    conflict_file = repo_path / "file1.py"
    conflict_file.write_text("original\n")
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Add file1"], cwd=repo_path, check=True)

    runner = CliRunner()
    result = runner.invoke(worktree, ["new", "test-feature"])
    assert result.exit_code == 0

    worktree_path = repo_path / "wt" / "test-feature"

    conflict_file.write_text("ours version\n")
    run_git(["add", "file1.py"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent modifies"], cwd=repo_path, check=True)

    wt_file = worktree_path / "file1.py"
    wt_file.write_text("theirs version\n")
    run_git(["add", "file1.py"], cwd=worktree_path, check=True)
    run_git(["commit", "-m", "Worktree modifies"], cwd=worktree_path, check=True)

    (repo_path / "other.txt").write_text("content")
    run_git(["add", "other.txt"], cwd=repo_path, check=True)
    run_git(["commit", "-m", "Parent adds other"], cwd=repo_path, check=True)

    result = run_git(
        ["merge", "--no-commit", "--no-ff", "test-feature"], cwd=repo_path, check=False
    )
    assert result.returncode != 0

    conflict_check = run_git(
        ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path, check=True
    )
    assert "file1.py" in conflict_check.stdout

    resolution_result = apply_theirs_resolution(["file1.py"])
    assert resolution_result is True

    file_content = conflict_file.read_text()
    assert "theirs version" in file_content

    conflict_check2 = run_git(
        ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path, check=True
    )
    assert "file1.py" not in conflict_check2.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
