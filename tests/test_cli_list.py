"""Tests for CLI list command."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from claudeutils import cli
from claudeutils.models import SessionInfo

if TYPE_CHECKING:
    from pathlib import Path


def test_cli_no_args_shows_usage(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI invoked with no arguments exits with code 2."""
    monkeypatch.setattr("sys.argv", ["claudeutils"])

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 2


def test_list_command_default_project(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """List command uses current directory by default."""
    # Track what list_top_level_sessions is called with
    called_with = []

    def mock_list(project_dir: str) -> list[SessionInfo]:
        called_with.append(project_dir)
        return []

    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    assert called_with == [str(project_dir)]


def test_list_command_with_project_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """List command respects --project flag."""
    # Track what list_top_level_sessions is called with
    called_with = []

    def mock_list(project_dir: str) -> list[SessionInfo]:
        called_with.append(project_dir)
        return []

    monkeypatch.setattr(
        "sys.argv", ["claudeutils", "list", "--project", "/custom/path"]
    )
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    assert called_with == ["/custom/path"]


def test_list_output_format(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """List output is formatted as [prefix] title."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
                title="Design a python script",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    captured = capsys.readouterr()
    assert captured.out == "[e12d203f] Design a python script\n"


def test_list_sorted_by_timestamp(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """List shows sessions in sorted order (most recent first)."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="id1111111111111111111111111111111",
                title="Third session",
                timestamp="2025-12-16T10:00:00.000Z",
            ),
            SessionInfo(
                session_id="id2222222222222222222222222222222",
                title="Second session",
                timestamp="2025-12-16T09:00:00.000Z",
            ),
            SessionInfo(
                session_id="id3333333333333333333333333333333",
                title="First session",
                timestamp="2025-12-16T08:00:00.000Z",
            ),
        ]

    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert "Third session" in lines[0]
    assert "Second session" in lines[1]
    assert "First session" in lines[2]


def test_list_long_title_truncated(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Long titles are truncated to 80 characters with ellipsis."""
    # format_title() truncates to 80 chars and adds ...
    # So a 77-char title + ... = 80 chars
    long_title = (
        "This is a very long title that exceeds the eighty character limit "
        "and should be t..."
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
                title=long_title,
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    captured = capsys.readouterr()
    # Output ends with ... (truncated by format_title in list_top_level_sessions)
    assert captured.out.endswith("...\n")


def test_list_no_sessions_message(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Empty sessions list prints 'No sessions found'."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return []

    monkeypatch.setattr("sys.argv", ["claudeutils", "list"])
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    captured = capsys.readouterr()
    assert captured.out == "No sessions found\n"


def test_list_nonexistent_project_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Nonexistent project gracefully returns 'No sessions found'."""

    def mock_list(project_dir: str) -> list[SessionInfo]:
        # Simulates what list_top_level_sessions does for nonexistent dirs
        return []

    monkeypatch.setattr(
        "sys.argv", ["claudeutils", "list", "--project", "/nonexistent/path"]
    )
    monkeypatch.setattr(cli, "list_top_level_sessions", mock_list)

    cli.main()

    captured = capsys.readouterr()
    assert captured.out == "No sessions found\n"
