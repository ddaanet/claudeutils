"""Pytest helper functions for test setup and assertions."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest

# Test Constants
SESSION_ID_MAIN = "e12d203f-ca65-44f0-9976-cb10b74514c1"
SESSION_ID_ALT = "a1b2c3d4-1234-5678-9abc-def012345678"
TS_BASE = "2025-12-16T08:00:00.000Z"
TS_EARLY = "2025-12-16T10:00:00.000Z"
TS_MID = "2025-12-16T11:00:00.000Z"
TS_LATE = "2025-12-16T12:00:00.000Z"


def make_mock_history_dir(history_dir: Path) -> Callable[[str], Path]:
    """Create mock function that returns fixed history directory."""

    def mock_get_history(proj: str) -> Path:
        return history_dir

    return mock_get_history


def setup_cli_mocks(
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    cwd: str | None = None,
    history_dir: Path | None = None,
) -> None:
    """Set up common CLI test mocks.

    Args:
        monkeypatch: pytest monkeypatch fixture
        argv: sys.argv to set
        cwd: Current working directory to mock (optional)
        history_dir: History directory to mock (optional)
    """
    monkeypatch.setattr("sys.argv", argv)
    if cwd:
        monkeypatch.setattr("os.getcwd", lambda: cwd)
    if history_dir:
        monkeypatch.setattr(
            "claudeutils.cli.get_project_history_dir",
            make_mock_history_dir(history_dir),
        )


def assert_json_output(
    capsys: pytest.CaptureFixture[str], expected_length: int | None = None
) -> list[dict[str, object]]:
    """Capture stdout and validate JSON list output.

    Args:
        capsys: pytest capture fixture
        expected_length: Optional expected list length to assert

    Returns:
        Parsed JSON output list
    """
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert isinstance(output, list)
    if expected_length is not None:
        assert len(output) == expected_length
    return output
