"""Tests for CLI extract command."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from claudeutils import cli
from claudeutils.models import FeedbackItem, FeedbackType

if TYPE_CHECKING:
    from pathlib import Path


def test_extract_command_basic(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Extract command outputs JSON array to stdout."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-test-project"
    history_dir.mkdir(parents=True)

    session_id = "e12d203f-ca65-44f0-9976-cb10b74514c1"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=session_id,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "e12d203f"])
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    captured = capsys.readouterr()
    # Should output valid JSON
    output = json.loads(captured.out)
    assert isinstance(output, list)
    assert len(output) == 1


def test_extract_with_output_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract command with --output writes to file."""
    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return [feedback_item]

    output_file = tmp_path / "feedback.json"

    monkeypatch.setattr(
        "sys.argv",
        ["claudeutils", "extract", "e12d203f", "--output", str(output_file)],
    )
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    # Verify file was written with valid JSON
    content = output_file.read_text()
    output = json.loads(content)
    assert isinstance(output, list)
    assert len(output) == 1


def test_extract_with_project_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract command respects --project flag."""
    history_dir = tmp_path / ".claude" / "projects" / "-custom"
    history_dir.mkdir(parents=True)

    session_id = "abc123de-f123-4567-89ab-cdef0123456a"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    called_with = []

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        called_with.append((sid, proj))
        return []

    monkeypatch.setattr(
        "sys.argv",
        ["claudeutils", "extract", "abc123", "--project", "/custom/path"],
    )
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    assert called_with == [(session_id, "/custom/path")]


def test_extract_full_session_id(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Extract with full session ID finds and extracts from session."""
    # Create mock history directory
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id = "e12d203f-ca65-44f0-9976-cb10b74514c1"
    session_file = history_dir / f"{session_id}.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Test"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"'
        + session_id
        + '"}\n'
    )

    def mock_get_history(proj: str) -> Path:
        return history_dir

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=session_id,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr(
        "sys.argv", ["claudeutils", "extract", "e12d203f-ca65-44f0-9976-cb10b74514c1"]
    )
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert len(output) == 1


def test_extract_partial_prefix(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Extract with partial prefix finds matching session."""
    # Create mock history directory
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id = "e12d203f-ca65-44f0-9976-cb10b74514c1"
    session_file = history_dir / f"{session_id}.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Test"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"'
        + session_id
        + '"}\n'
    )

    def mock_get_history(proj: str) -> Path:
        return history_dir

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=session_id,
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )

    called_with = []

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        called_with.append(sid)
        return [feedback_item]

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "e12d203f"])
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    # Should call extract with full session ID, not the prefix
    assert called_with == [session_id]


def test_extract_ambiguous_prefix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract with ambiguous prefix errors."""
    # Create mock history directory with 2 matching sessions
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id1 = "e12d203f-ca65-44f0-9976-cb10b74514c1"
    session_id2 = "e12d203f-aaaa-bbbb-cccc-dddddddddddd"

    (history_dir / f"{session_id1}.jsonl").write_text('{"test": 1}\n')
    (history_dir / f"{session_id2}.jsonl").write_text('{"test": 2}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "e12d203f"])
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1


def test_extract_no_matching_session(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Extract with no matching session errors."""
    # Create mock history directory with sessions but no match
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-tmp-project"
    history_dir.mkdir(parents=True)

    session_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "zzzzzzz"])
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))

    with pytest.raises(SystemExit) as exc_info:
        cli.main()

    assert exc_info.value.code == 1


def test_extract_json_format_valid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Extract outputs valid JSON that can be parsed."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-test-project"
    history_dir.mkdir(parents=True)

    session_id = "a1234567-b890-cdef-0123-456789abcdef"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    feedback_items = [
        FeedbackItem(
            timestamp="2025-12-16T08:43:43.872Z",
            session_id=session_id,
            feedback_type=FeedbackType.MESSAGE,
            content="Test feedback 1",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:43:44.872Z",
            session_id=session_id,
            feedback_type=FeedbackType.TOOL_DENIAL,
            content="Test feedback 2",
        ),
    ]

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return feedback_items

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "a1234567"])
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    captured = capsys.readouterr()
    # Should be valid JSON array
    output = json.loads(captured.out)
    assert isinstance(output, list)
    assert len(output) == 2


def test_extract_json_includes_all_fields(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Extract JSON output includes all fields."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-test-project"
    history_dir.mkdir(parents=True)

    session_id = "b1234567-b890-cdef-0123-456789abcdef"
    (history_dir / f"{session_id}.jsonl").write_text('{"test": 1}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:43:43.872Z",
        session_id=session_id,
        feedback_type=FeedbackType.TOOL_DENIAL,
        content="Request denied",
        agent_id="a6755ed",
        slug="test-slug",
        tool_use_id="toolu_123",
    )

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return [feedback_item]

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "b1234567"])
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert len(output) == 1
    item = output[0]
    assert item["timestamp"] == "2025-12-16T08:43:43.872Z"
    assert item["session_id"] == session_id
    assert item["feedback_type"] == "tool_denial"
    assert item["content"] == "Request denied"
    assert item["agent_id"] == "a6755ed"
    assert item["slug"] == "test-slug"
    assert item["tool_use_id"] == "toolu_123"


def test_extract_recursive_integration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Extract recursively integrates through CLI."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    history_dir = tmp_path / ".claude" / "projects" / "-test-project"
    history_dir.mkdir(parents=True)

    main_session = "c1234567-b890-cdef-0123-456789abcdef"
    (history_dir / f"{main_session}.jsonl").write_text('{"test": 1}\n')

    def mock_get_history(proj: str) -> Path:
        return history_dir

    feedback_items = [
        FeedbackItem(
            timestamp="2025-12-16T08:00:00.000Z",
            session_id=main_session,
            feedback_type=FeedbackType.MESSAGE,
            content="Main session feedback",
        ),
        FeedbackItem(
            timestamp="2025-12-16T08:30:00.000Z",
            session_id="agent-a1",
            feedback_type=FeedbackType.MESSAGE,
            content="Agent feedback",
            agent_id="a1",
        ),
        FeedbackItem(
            timestamp="2025-12-16T09:00:00.000Z",
            session_id="agent-a2",
            feedback_type=FeedbackType.MESSAGE,
            content="Nested agent feedback",
            agent_id="a2",
        ),
    ]

    def mock_extract(sid: str, proj: str) -> list[FeedbackItem]:
        return feedback_items

    monkeypatch.setattr("sys.argv", ["claudeutils", "extract", "c1234567"])
    monkeypatch.setattr("claudeutils.cli.get_project_history_dir", mock_get_history)
    monkeypatch.setattr("os.getcwd", lambda: str(project_dir))
    monkeypatch.setattr(cli, "extract_feedback_recursively", mock_extract)

    cli.main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    # Should have all 3 feedback items from recursive extraction
    assert len(output) == 3
    assert output[0]["content"] == "Main session feedback"
    assert output[1]["content"] == "Agent feedback"
    assert output[2]["content"] == "Nested agent feedback"
