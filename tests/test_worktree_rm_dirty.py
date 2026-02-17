"""Tests for dirty tree checks in worktree rm."""

from collections.abc import Callable
from pathlib import Path

import pytest
from click.testing import CliRunner

from claudeutils.worktree.cli import worktree
from tests.fixtures_worktree import _create_worktree


def test_rm_blocks_on_dirty_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Blocks removal if parent repo has uncommitted changes."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    (repo_path / "dirty.txt").write_text("dirty content")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 2
    assert "uncommitted" in result.output.lower() or "parent" in result.output.lower()


def test_rm_blocks_on_dirty_submodule(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Blocks removal if submodule has uncommitted changes."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    monkeypatch.setattr(
        "claudeutils.worktree.cli._is_submodule_dirty",
        lambda: True,
    )

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--confirm", "test-feature"])

    assert result.exit_code == 2
    assert (
        "uncommitted" in result.output.lower()
        or "submodule" in result.output.lower()
    )


def test_rm_force_bypasses_dirty_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, init_repo: Callable[[Path], None]
) -> None:
    """Force flag bypasses dirty check."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    init_repo(repo_path)
    worktree_path = _create_worktree(repo_path, "test-feature", init_repo)
    assert worktree_path.exists()

    (repo_path / "dirty.txt").write_text("dirty")

    runner = CliRunner()
    result = runner.invoke(worktree, ["rm", "--force", "test-feature"])

    assert result.exit_code == 0
    assert not worktree_path.exists()
