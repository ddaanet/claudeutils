"""Tests for worktree merge conflict auto-resolution."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree


def test_merge_conflict_agent_core(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve agent-core conflict (already merged in Phase 2)."""
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    subprocess.run(
        ["git", "branch", "test-merge"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0, f"new command should succeed, got: {result.output}"

    worktree_path = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "test-merge"
    )

    # Add a change on the worktree branch to a non-agent-core file
    commit_file(worktree_path, "branch-file.txt", "branch content\n", "Branch change")

    # Also update submodule on branch
    (worktree_path / "agent-core" / "branch-change.txt").write_text("branch change\n")
    subprocess.run(
        ["git", "add", "branch-change.txt"],
        cwd=worktree_path / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Branch change in submodule"],
        cwd=worktree_path / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update agent-core submodule on branch"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add a conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    commit_file(repo_with_submodule, "main-file.txt", "main content\n", "Main change")

    # Also update agent-core on main to different commit
    (repo_with_submodule / "agent-core" / "main-change.txt").write_text("main change\n")
    subprocess.run(
        ["git", "add", "main-change.txt"],
        cwd=repo_with_submodule / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Main change in submodule"],
        cwd=repo_with_submodule / "agent-core",
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "add", "agent-core"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update agent-core on main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Check that agent-core is NOT in unmerged paths (it should have been auto-resolved)
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    conflicts = [c for c in unmerged.stdout.strip().split("\n") if c.strip()]
    assert "agent-core" not in conflicts, (
        f"agent-core should be auto-resolved, but found in conflicts: {conflicts}"
    )

    # Verify merge is complete (MERGE_HEAD should not exist after commit)
    merge_head = subprocess.run(
        ["git", "rev-parse", "MERGE_HEAD"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    assert merge_head.returncode != 0, (
        "MERGE_HEAD should not exist after merge completes"
    )


def test_merge_conflict_session_md(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve session.md, extract and warn about new tasks."""
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    subprocess.run(
        ["git", "branch", "test-merge"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0, f"new command should succeed, got: {result.output}"

    worktree_path = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "test-merge"
    )

    # Create agents dir and initial session.md on both sides
    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (worktree_path / "agents").mkdir(exist_ok=True)

    # Main: session.md with task A
    (repo_with_submodule / "agents" / "session.md").write_text(
        "# Session\n\n- [ ] **Task A** — `/design` | sonnet\n"
    )
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session.md with Task A"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Worktree: start with same, then add task B
    (worktree_path / "agents" / "session.md").write_text(
        "# Session\n\n- [ ] **Task A** — `/design` | sonnet\n"
    )
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Worktree: add Task B
    (worktree_path / "agents" / "session.md").write_text(
        "# Session\n\n- [ ] **Task A** — `/design` | sonnet\n"
        "- [ ] **Task B** — `/runbook` | haiku\n"
    )
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add Task B in worktree"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Main: update session.md (different change, will conflict)
    (repo_with_submodule / "agents" / "session.md").write_text(
        "# Session\n\n- [ ] **Task A** — `/design` | opus\n"
    )
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update session.md on main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Verify session.md is NOT in unmerged paths (auto-resolved)
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    conflicts = [c for c in unmerged.stdout.strip().split("\n") if c.strip()]
    msg = (
        "agents/session.md should be auto-resolved, "
        f"but found in conflicts: {conflicts}"
    )
    assert "agents/session.md" not in conflicts, msg

    # Verify Task B was extracted from worktree and added to main session
    session_content = (repo_with_submodule / "agents" / "session.md").read_text()
    assert "Task B" in session_content, (
        f"Task B should be extracted and present in session.md, got: {session_content}"
    )


def test_merge_conflict_session_md_multiline_blocks(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve session.md conflict preserving multi-line task blocks."""
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    subprocess.run(
        ["git", "branch", "test-merge"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0, f"new command should succeed, got: {result.output}"

    worktree_path = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "test-merge"
    )

    # Create agents dir and initial session.md on both sides
    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (worktree_path / "agents").mkdir(exist_ok=True)

    # Main: session.md with task A
    main_session = (
        "# Session\n\n## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | sonnet\n\n## Blockers\n"
    )
    (repo_with_submodule / "agents" / "session.md").write_text(main_session)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session.md with Task A"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Worktree: start with same base
    (worktree_path / "agents" / "session.md").write_text(main_session)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Worktree: add Task B with multi-line block
    (worktree_path / "agents" / "session.md").write_text(
        "# Session\n\n## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | sonnet\n"
        "- [ ] **Task B** — `/runbook plans/foo/runbook.md` | haiku\n"
        "  - Plan: foo | Status: planned\n"
        "  - Notes: Multi-line task block\n\n"
        "## Blockers\n"
    )
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add Task B with continuation lines"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Main: update Task A (different change, will conflict)
    main_updated = (
        "# Session\n\n## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | opus\n\n## Blockers\n"
    )
    (repo_with_submodule / "agents" / "session.md").write_text(main_updated)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update Task A on main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Verify session.md is NOT in unmerged paths (auto-resolved)
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    conflicts = [c for c in unmerged.stdout.strip().split("\n") if c.strip()]
    assert "agents/session.md" not in conflicts

    # Verify Task B was extracted WITH continuation lines
    session_content = (repo_with_submodule / "agents" / "session.md").read_text()
    assert "Task B" in session_content, f"Task B missing in: {session_content}"
    assert "Plan: foo | Status: planned" in session_content, (
        f"Continuation line 1 missing in: {session_content}"
    )
    assert "Notes: Multi-line task block" in session_content, (
        f"Continuation line 2 missing in: {session_content}"
    )


def test_merge_conflict_session_md_insertion_position(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Verify new tasks inserted at correct position with blank line separation.

    Tests that _resolve_session_md_conflict() uses find_section_bounds() to
    locate the insertion point and inserts new blocks before the next section
    header with proper blank line separation.
    """
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    subprocess.run(
        ["git", "branch", "test-merge"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0, f"new command should succeed, got: {result.output}"

    worktree_path = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "test-merge"
    )

    # Create agents dir and initial session.md on both sides with structured sections
    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (worktree_path / "agents").mkdir(exist_ok=True)

    # Main: session.md with Pending Tasks and Blockers sections
    main_content = (
        "# Session\n\n"
        "## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | sonnet\n\n"
        "## Blockers / Gotchas\n\n"
        "- Some blocker note\n"
    )
    (repo_with_submodule / "agents" / "session.md").write_text(main_content)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session.md with sections"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Worktree: start with same base
    (worktree_path / "agents" / "session.md").write_text(main_content)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Worktree: add Task B (new task between Pending Tasks and Blockers)
    worktree_content = (
        "# Session\n\n"
        "## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | sonnet\n"
        "- [ ] **Task B** — `/runbook` | haiku\n\n"
        "## Blockers / Gotchas\n\n"
        "- Some blocker note\n"
    )
    (worktree_path / "agents" / "session.md").write_text(worktree_content)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add Task B"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Main: update Task A metadata (creates conflict)
    main_update = (
        "# Session\n\n"
        "## Pending Tasks\n\n"
        "- [ ] **Task A** — `/design` | opus\n\n"
        "## Blockers / Gotchas\n\n"
        "- Some blocker note\n"
    )
    (repo_with_submodule / "agents" / "session.md").write_text(main_update)
    subprocess.run(
        ["git", "add", "agents/session.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update Task A"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Verify Task B was inserted before Blockers section with blank line separation
    session_content = (repo_with_submodule / "agents" / "session.md").read_text()

    # Task B should exist
    assert "Task B" in session_content, f"Task B missing in: {session_content}"

    # Verify insertion position: Task B should appear BEFORE Blockers section
    task_b_idx = session_content.find("Task B")
    blockers_idx = session_content.find("## Blockers")
    assert task_b_idx < blockers_idx, (
        f"Task B should appear before Blockers section. "
        f"Task B at {task_b_idx}, Blockers at {blockers_idx}. "
        f"Content:\n{session_content}"
    )

    # Verify blank line separation before Blockers section
    lines = session_content.split("\n")
    blockers_line_idx = next(i for i, line in enumerate(lines) if "## Blockers" in line)
    assert lines[blockers_line_idx - 1] == "", (
        f"Expected blank line before Blockers section at line {blockers_line_idx - 1}, "
        f"got: {lines[blockers_line_idx - 1]!r}"
    )


def test_merge_conflict_learnings_md(
    repo_with_submodule: Path,
    monkeypatch: pytest.MonkeyPatch,
    mock_precommit: None,
    commit_file: Callable[[Path, str, str, str], None],
) -> None:
    """Auto-resolve learnings.md by keeping ours and appending theirs-only."""
    monkeypatch.chdir(repo_with_submodule)

    commit_file(repo_with_submodule, ".gitignore", "wt/\n", "Add gitignore")

    subprocess.run(
        ["git", "branch", "test-merge"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    result = CliRunner().invoke(worktree, ["new", "test-merge"])
    assert result.exit_code == 0, f"new command should succeed, got: {result.output}"

    worktree_path = (
        repo_with_submodule.parent / f"{repo_with_submodule.name}-wt" / "test-merge"
    )

    # Create agents dir and initial learnings.md on both sides
    (repo_with_submodule / "agents").mkdir(exist_ok=True)
    (worktree_path / "agents").mkdir(exist_ok=True)

    # Main: learnings.md with learning A
    (repo_with_submodule / "agents" / "learnings.md").write_text(
        "# Learnings\n\n- Learning A: Common content\n"
    )
    subprocess.run(
        ["git", "add", "agents/learnings.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add learnings.md with Learning A"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Worktree: start with same, then add learning B
    (worktree_path / "agents" / "learnings.md").write_text(
        "# Learnings\n\n- Learning A: Common content\n"
    )
    subprocess.run(
        ["git", "add", "agents/learnings.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add learnings.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Worktree: add Learning B
    (worktree_path / "agents" / "learnings.md").write_text(
        "# Learnings\n\n- Learning A: Common content\n"
        "- Learning B: Worktree-only learning\n"
    )
    subprocess.run(
        ["git", "add", "agents/learnings.md"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add Learning B in worktree"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Switch back to main and add conflicting change
    subprocess.run(
        ["git", "checkout", "main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    # Main: update learnings.md (different change, will conflict)
    (repo_with_submodule / "agents" / "learnings.md").write_text(
        "# Learnings\n\n- Learning A: Common content (modified on main)\n"
    )
    subprocess.run(
        ["git", "add", "agents/learnings.md"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Update learnings.md on main"],
        cwd=repo_with_submodule,
        check=True,
        capture_output=True,
    )

    result = CliRunner().invoke(worktree, ["merge", "test-merge"])
    assert result.exit_code == 0, f"merge command should succeed: {result.output}"

    # Verify learnings.md is NOT in unmerged paths (auto-resolved)
    unmerged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=repo_with_submodule,
        capture_output=True,
        text=True,
    )
    conflicts = [c for c in unmerged.stdout.strip().split("\n") if c.strip()]
    msg = (
        "agents/learnings.md should be auto-resolved, "
        f"but found in conflicts: {conflicts}"
    )
    assert "agents/learnings.md" not in conflicts, msg

    # Verify merged result contains both ours content and theirs-only content
    merged_content = (repo_with_submodule / "agents" / "learnings.md").read_text()
    assert "Common content (modified on main)" in merged_content, (
        f"Merged should contain ours content, got: {merged_content}"
    )
    assert "Learning B" in merged_content, (
        f"Merged should contain theirs-only learning, got: {merged_content}"
    )
