"""Tests for worktree CLI module."""

from claudeutils.worktree.cli import worktree


def test_package_import() -> None:
    """Verify that worktree package can be imported."""
    assert worktree is not None
