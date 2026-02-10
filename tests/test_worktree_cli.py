"""Tests for worktree CLI module."""

from click.testing import CliRunner

from claudeutils.worktree.cli import derive_slug, worktree


def test_package_import() -> None:
    """Verify that worktree package can be imported."""
    assert worktree is not None


def test_worktree_command_group() -> None:
    """Verify _worktree command group displays help output."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["--help"])
    assert result.exit_code == 0
    assert "_worktree" in result.output


def test_derive_slug() -> None:
    """Verify derive_slug transforms task names to valid worktree slugs."""
    assert derive_slug("Implement ambient awareness") == "implement-ambient-awareness"
    assert derive_slug("Design runbook identifiers") == "design-runbook-identifiers"
    assert (
        derive_slug("Review agent-core orphaned revisions")
        == "review-agent-core-orphaned-rev"
    )
    assert derive_slug("Multiple    spaces   here") == "multiple-spaces-here"
    assert derive_slug("Special!@#$%chars") == "special-chars"


def test_ls_empty() -> None:
    """Verify ls exits 0 with empty output when no worktrees exist."""
    runner = CliRunner()
    result = runner.invoke(worktree, ["ls"])
    assert result.exit_code == 0
    assert result.output == ""
