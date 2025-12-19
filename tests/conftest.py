"""Shared pytest fixtures for all tests."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from claudeutils.models import FeedbackItem, FeedbackType


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


# Test Data Factory Fixtures
@pytest.fixture
def feedback_factory() -> Callable[..., FeedbackItem]:
    """Create FeedbackItem instances for testing."""

    def _make(
        content: str,
        session_id: str = "e12d203f-ca65-44f0-9976-cb10b74514c1",
        feedback_type: FeedbackType = FeedbackType.MESSAGE,
        timestamp: str = "2025-12-16T08:00:00.000Z",
        **kwargs: str | None,
    ) -> FeedbackItem:
        return FeedbackItem(
            timestamp=timestamp,
            session_id=session_id,
            feedback_type=feedback_type,
            content=content,
            **kwargs,
        )

    return _make


@pytest.fixture
def build_user_entry() -> Callable[..., dict[str, Any]]:
    """Build user message entry dicts for testing."""

    def _build(
        content: str,
        session_id: str = "e12d203f-ca65-44f0-9976-cb10b74514c1",
        timestamp: str = "2025-12-16T08:00:00.000Z",
        **kwargs: Any,  # noqa: ANN401 - Temporay, function unused.
    ) -> dict[str, Any]:
        """Build user message entry dict."""
        return {
            "type": "user",
            "message": {"role": "user", "content": content},
            "timestamp": timestamp,
            "sessionId": session_id,
            **kwargs,
        }

    return _build
