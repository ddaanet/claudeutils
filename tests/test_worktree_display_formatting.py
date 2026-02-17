"""Tests for worktree display formatting (rich ls output)."""

import subprocess
from pathlib import Path
from unittest import mock

from claudeutils.planstate.aggregation import AggregatedStatus
from claudeutils.planstate.models import PlanState
from claudeutils.worktree.display import format_rich_ls


def test_format_rich_ls_renders_gate_lines(tmp_path: Path) -> None:
    """Test that format_rich_ls correctly renders Gate lines when present.

    Verifies the gate display path works correctly when PlanState objects have
    gate set. Uses mock to inject pre-built PlanState with gate value.
    """
    # Create a temporary git repo with main tree
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
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

    # Create initial commit (needed for git status and git log in format_tree_header)
    (repo_path / "file.txt").write_text("content")
    (repo_path / ".gitignore").write_text("wt/\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "initial"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create a worktree with branch "feature"
    worktree_path = repo_path / "wt" / "test-wt"
    subprocess.run(
        ["git", "worktree", "add", "-b", "feature", str(worktree_path)],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create session.md in worktree
    agents_dir = worktree_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\nTest session")
    subprocess.run(
        ["git", "add", "."],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add session"],
        cwd=worktree_path,
        check=True,
        capture_output=True,
    )

    # Get porcelain output
    result = subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    porcelain_output = result.stdout

    # Create PlanState objects: one with gate, one without
    plan_with_gate = PlanState(
        name="gated-plan",
        status="designed",
        next_action="/runbook plans/gated-plan/design.md",
        gate="design vet stale — re-vet before planning",
        artifacts={"design.md"},
        tree_path=str(repo_path),
    )
    plan_without_gate = PlanState(
        name="normal-plan",
        status="planned",
        next_action="agent-core/bin/prepare-runbook.py plans/normal-plan",
        gate=None,
        artifacts={"design.md", "runbook-phase-1.md"},
        tree_path=str(worktree_path),
    )

    # Mock aggregate_trees to return our test plans
    mock_aggregated = AggregatedStatus(plans=[plan_with_gate, plan_without_gate])
    with mock.patch(
        "claudeutils.worktree.display.aggregate_trees",
        return_value=mock_aggregated,
    ):
        output = format_rich_ls(str(repo_path), porcelain_output)

    # Verify gate line appears for plan_with_gate
    assert "  Gate: design vet stale — re-vet before planning" in output, (
        f"Expected gate line in output, got: {output}"
    )

    # Verify no gate line for plan_without_gate (gate is None)
    assert output.count("  Gate:") == 1, (
        f"Expected exactly 1 gate line, got: {output}"
    )

    # Verify plan lines are present
    assert "  Plan: gated-plan [designed]" in output, (
        f"Expected gated-plan line in output, got: {output}"
    )
    assert "  Plan: normal-plan [planned]" in output, (
        f"Expected normal-plan line in output, got: {output}"
    )
