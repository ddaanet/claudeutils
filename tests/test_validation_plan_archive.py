"""Tests for plan archive coverage validation."""

import subprocess
from pathlib import Path

from claudeutils.validation.plan_archive import (
    check_plan_archive_coverage,
    get_archive_headings,
    get_staged_plan_deletions,
)


class TestGetStagedPlanDeletions:
    """Tests for get_staged_plan_deletions."""

    def test_no_deletions_returns_empty(self, tmp_path: Path) -> None:
        """Repository with no deletions returns empty list."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        result = get_staged_plan_deletions(repo)
        assert result == []

    def test_deleted_plan_detected(self, tmp_path: Path) -> None:
        """Deleted plan directory detected from git staging."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create and commit plan with file
        plans_dir = repo / "plans" / "old-plan"
        plans_dir.mkdir(parents=True)
        (plans_dir / "design.md").write_text("# Design")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Delete the plan and stage deletion
        subprocess.run(
            ["git", "rm", "-r", "plans/old-plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        result = get_staged_plan_deletions(repo)
        assert "old-plan" in result

    def test_multiple_deleted_plans(self, tmp_path: Path) -> None:
        """Multiple deleted plans all detected."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create and commit plans
        for plan_name in ["plan-one", "plan-two"]:
            plans_dir = repo / "plans" / plan_name
            plans_dir.mkdir(parents=True)
            (plans_dir / "design.md").write_text("# Design")
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add plans"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Delete both plans
        for plan_name in ["plan-one", "plan-two"]:
            subprocess.run(
                ["git", "rm", "-r", f"plans/{plan_name}"],
                cwd=repo,
                check=True,
                capture_output=True,
            )

        result = get_staged_plan_deletions(repo)
        assert "plan-one" in result
        assert "plan-two" in result

    def test_plan_with_only_gitkeep_not_deleted(self, tmp_path: Path) -> None:
        """Plans containing only .gitkeep not considered substantive."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create plan with only .gitkeep
        plans_dir = repo / "plans" / "empty-plan"
        plans_dir.mkdir(parents=True)
        (plans_dir / ".gitkeep").touch()
        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add empty plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Delete the plan
        subprocess.run(
            ["git", "rm", "-r", "plans/empty-plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        result = get_staged_plan_deletions(repo)
        # Non-substantive plans should not be in the list
        assert "empty-plan" not in result


class TestGetArchiveHeadings:
    """Tests for get_archive_headings."""

    def test_extracts_h2_headings(self, tmp_path: Path) -> None:
        """H2 headings extracted from archive file."""
        root = tmp_path
        archive_file = root / "agents" / "plan-archive.md"
        archive_file.parent.mkdir(parents=True)
        archive_file.write_text(
            """# Plan Archive

## plan-one

Some content here.

## plan-two

More content.
"""
        )

        result = get_archive_headings(root)
        assert "plan-one" in result
        assert "plan-two" in result

    def test_case_insensitive_matching(self, tmp_path: Path) -> None:
        """Archive headings match case-insensitively."""
        root = tmp_path
        archive_file = root / "agents" / "plan-archive.md"
        archive_file.parent.mkdir(parents=True)
        archive_file.write_text(
            """# Plan Archive

## MyPlan

Content.
"""
        )

        result = get_archive_headings(root)
        # Should find it even with different case
        assert any(h.lower() == "myplan" for h in result)

    def test_missing_archive_file_returns_empty(self, tmp_path: Path) -> None:
        """Missing archive file returns empty set."""
        root = tmp_path

        result = get_archive_headings(root)
        assert result == set()

    def test_ignores_non_h2_headings(self, tmp_path: Path) -> None:
        """Only H2 headings extracted, not H1 or H3."""
        root = tmp_path
        archive_file = root / "agents" / "plan-archive.md"
        archive_file.parent.mkdir(parents=True)
        archive_file.write_text(
            """# Main Title

## good-plan

Content.

### subsection

Details.

## another-plan

More.
"""
        )

        result = get_archive_headings(root)
        assert "good-plan" in result
        assert "another-plan" in result
        assert "subsection" not in result
        assert "Main Title" not in result


class TestCheckPlanArchiveCoverage:
    """Tests for check_plan_archive_coverage."""

    def test_no_deleted_plans_no_errors(self, tmp_path: Path) -> None:
        """No errors when no plans deleted."""
        root = tmp_path
        result = root / "agents" / "plan-archive.md"
        result.parent.mkdir(parents=True)
        result.write_text("# Archive\n")

        errors = check_plan_archive_coverage(root)
        assert errors == []

    def test_deleted_plan_with_archive_entry_no_error(self, tmp_path: Path) -> None:
        """Deleted plan with archive entry produces no error."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create plan and archive entry
        plans_dir = repo / "plans" / "old-plan"
        plans_dir.mkdir(parents=True)
        (plans_dir / "design.md").write_text("# Design")

        agents_dir = repo / "agents"
        agents_dir.mkdir(exist_ok=True)
        (agents_dir / "plan-archive.md").write_text(
            """# Plan Archive

## old-plan

Description of old-plan.
"""
        )

        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Delete the plan
        subprocess.run(
            ["git", "rm", "-r", "plans/old-plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        errors = check_plan_archive_coverage(repo)
        assert errors == []

    def test_deleted_plan_without_archive_entry_error(self, tmp_path: Path) -> None:
        """Deleted plan without archive entry produces error."""
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create plan without archive entry
        plans_dir = repo / "plans" / "undocumented-plan"
        plans_dir.mkdir(parents=True)
        (plans_dir / "design.md").write_text("# Design")

        agents_dir = repo / "agents"
        agents_dir.mkdir(exist_ok=True)
        (agents_dir / "plan-archive.md").write_text("# Plan Archive\n")

        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Delete the plan
        subprocess.run(
            ["git", "rm", "-r", "plans/undocumented-plan"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        errors = check_plan_archive_coverage(repo)
        assert len(errors) == 1
        assert "undocumented-plan" in errors[0]

    def test_multiple_deleted_plans_mixed_coverage(self, tmp_path: Path) -> None:
        """Multiple deleted plans with mixed coverage.

        Reports only missing ones.
        """
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Create plans
        for plan_name in ["covered-plan", "uncovered-plan"]:
            plans_dir = repo / "plans" / plan_name
            plans_dir.mkdir(parents=True)
            (plans_dir / "design.md").write_text("# Design")

        agents_dir = repo / "agents"
        agents_dir.mkdir(exist_ok=True)
        (agents_dir / "plan-archive.md").write_text(
            """# Plan Archive

## covered-plan

This plan is archived.
"""
        )

        subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add plans"],
            cwd=repo,
            check=True,
            capture_output=True,
        )

        # Delete both plans
        for plan_name in ["covered-plan", "uncovered-plan"]:
            subprocess.run(
                ["git", "rm", "-r", f"plans/{plan_name}"],
                cwd=repo,
                check=True,
                capture_output=True,
            )

        errors = check_plan_archive_coverage(repo)
        assert len(errors) == 1
        assert "uncovered-plan" in errors[0]
