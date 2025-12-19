"""Shared pytest fixtures for all tests."""

from pathlib import Path

import pytest


# Project Directory Fixture
@pytest.fixture
def temp_project_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Create temporary project and history directories.

    Returns:
        Tuple of (project_dir, history_dir) with mocked get_project_history_dir.
    """
    project = tmp_path / "myproject"
    project.mkdir()

    history_dir = tmp_path / ".claude" / "projects" / "-tmp-myproject"
    history_dir.mkdir(parents=True)

    def mock_get_history(proj: str) -> Path:
        return history_dir

    # Patch for discovery module (used in test_discovery and test_agent_files)
    monkeypatch.setattr(
        "claudeutils.discovery.get_project_history_dir", mock_get_history
    )

    return project, history_dir


# History Directory Fixture for extraction tests
@pytest.fixture
def temp_history_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Mock history directory for extraction and agent file testing.

    Patches both extraction and discovery modules for recursive testing.

    Returns:
        Tuple of (project_dir, history_dir) with mocked get_project_history_dir.
    """
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    def mock_get_history(proj: str) -> Path:
        return history_dir

    # Patch both modules for recursive extraction testing
    monkeypatch.setattr(
        "claudeutils.extraction.get_project_history_dir", mock_get_history
    )
    monkeypatch.setattr(
        "claudeutils.discovery.get_project_history_dir", mock_get_history
    )

    return tmp_path / "project", history_dir
