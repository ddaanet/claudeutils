"""Tests for CLI extract command - output formatting and integration."""

import json
from pathlib import Path

import pytest

from claudeutils import cli
from claudeutils.models import FeedbackItem, FeedbackType

from . import pytest_helpers


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

    pytest_helpers.setup_cli_mocks(
        monkeypatch,
        ["claudeutils", "extract", "a1234567"],
        cwd=str(project_dir),
        history_dir=history_dir,
    )
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    pytest_helpers.assert_json_output(capsys, expected_length=2)


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

    pytest_helpers.setup_cli_mocks(
        monkeypatch,
        ["claudeutils", "extract", "b1234567"],
        cwd=str(project_dir),
        history_dir=history_dir,
    )
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

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

    pytest_helpers.setup_cli_mocks(
        monkeypatch,
        ["claudeutils", "extract", "c1234567"],
        cwd=str(project_dir),
        history_dir=history_dir,
    )
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    # Should have all 3 feedback items from recursive extraction
    assert len(output) == 3
    assert output[0]["content"] == "Main session feedback"
    assert output[1]["content"] == "Agent feedback"
    assert output[2]["content"] == "Nested agent feedback"
