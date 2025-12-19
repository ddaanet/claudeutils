"""Tests for CLI collect command."""

import json
from pathlib import Path

import pytest

from claudeutils import cli
from claudeutils.models import FeedbackItem, FeedbackType, SessionInfo

from . import pytest_helpers


def test_collect_single_session_with_feedback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Collect extracts feedback from single session."""
    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        feedback_type=FeedbackType.MESSAGE,
        content="This is feedback",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
                title="Test session",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return [feedback_item]

    pytest_helpers.setup_cli_mocks(monkeypatch, ["claudeutils", "collect"])
    monkeypatch.setattr("claudeutils.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    output = pytest_helpers.assert_json_output(capsys, expected_length=1)
    assert output[0]["content"] == "This is feedback"


def test_collect_multiple_sessions(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Collect aggregates feedback from multiple sessions."""
    feedback_1 = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Feedback from session 1",
    )
    feedback_2 = FeedbackItem(
        timestamp="2025-12-16T09:39:26.932Z",
        session_id="session2",
        feedback_type=FeedbackType.MESSAGE,
        content="Feedback from session 2",
    )
    feedback_3 = FeedbackItem(
        timestamp="2025-12-16T10:39:26.932Z",
        session_id="session3",
        feedback_type=FeedbackType.MESSAGE,
        content="Feedback from session 3",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Session 1",
                timestamp="2025-12-16T08:39:26.932Z",
            ),
            SessionInfo(
                session_id="session2",
                title="Session 2",
                timestamp="2025-12-16T09:39:26.932Z",
            ),
            SessionInfo(
                session_id="session3",
                title="Session 3",
                timestamp="2025-12-16T10:39:26.932Z",
            ),
        ]

    feedback_by_session = {
        "session1": [feedback_1],
        "session2": [feedback_2],
        "session3": [feedback_3],
    }

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return feedback_by_session.get(session_id, [])

    pytest_helpers.setup_cli_mocks(monkeypatch, ["claudeutils", "collect"])
    monkeypatch.setattr("claudeutils.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    output = pytest_helpers.assert_json_output(capsys, expected_length=3)
    assert output[0]["content"] == "Feedback from session 1"
    assert output[1]["content"] == "Feedback from session 2"
    assert output[2]["content"] == "Feedback from session 3"


def test_collect_with_subagents(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Collect includes feedback from nested sub-agents."""
    # Main session has 2 feedback items
    main_1 = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Main feedback 1",
    )
    main_2 = FeedbackItem(
        timestamp="2025-12-16T08:39:27.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Main feedback 2",
    )
    # Sub-agent has 2 feedback items
    sub_1 = FeedbackItem(
        timestamp="2025-12-16T08:39:28.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Subagent feedback 1",
        agent_id="agent1",
    )
    sub_2 = FeedbackItem(
        timestamp="2025-12-16T08:39:29.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Subagent feedback 2",
        agent_id="agent1",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Session with subagents",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        # extract_feedback_recursively returns main + subagent feedback
        return [main_1, main_2, sub_1, sub_2]

    pytest_helpers.setup_cli_mocks(monkeypatch, ["claudeutils", "collect"])
    monkeypatch.setattr("claudeutils.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    output = pytest_helpers.assert_json_output(capsys, expected_length=4)
    assert output[0]["content"] == "Main feedback 1"
    assert output[1]["content"] == "Main feedback 2"
    assert output[2]["content"] == "Subagent feedback 1"
    assert output[3]["content"] == "Subagent feedback 2"


def test_collect_skips_malformed_session(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Collect skips malformed sessions and logs warning."""
    valid_feedback = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Valid feedback",
    )

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Valid session",
                timestamp="2025-12-16T08:39:26.932Z",
            ),
            SessionInfo(
                session_id="session2",
                title="Malformed session",
                timestamp="2025-12-16T09:39:26.932Z",
            ),
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        if session_id == "session1":
            return [valid_feedback]
        # Simulate extraction error for malformed session
        raise ValueError("Malformed data")  # noqa: TRY003 - test mock error

    pytest_helpers.setup_cli_mocks(monkeypatch, ["claudeutils", "collect"])
    monkeypatch.setattr("claudeutils.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    # Check both stdout and stderr in one capture
    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert len(output) == 1
    assert output[0]["content"] == "Valid feedback"
    assert "Warning" in captured.err


def test_collect_output_to_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Collect writes JSON to file with --output flag."""
    feedback_item = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="session1",
        feedback_type=FeedbackType.MESSAGE,
        content="Test feedback",
    )
    output_file = tmp_path / "output.json"

    def mock_list(project_dir: str) -> list[SessionInfo]:
        return [
            SessionInfo(
                session_id="session1",
                title="Test session",
                timestamp="2025-12-16T08:39:26.932Z",
            )
        ]

    def mock_extract(session_id: str, project_dir: str) -> list[FeedbackItem]:
        return [feedback_item]

    pytest_helpers.setup_cli_mocks(
        monkeypatch,
        ["claudeutils", "collect", "--output", str(output_file)],
    )
    monkeypatch.setattr("claudeutils.cli.list_top_level_sessions", mock_list)
    monkeypatch.setattr("claudeutils.cli.extract_feedback_recursively", mock_extract)

    cli.main()

    # Verify file was written
    assert output_file.exists()
    output = json.loads(output_file.read_text())
    assert len(output) == 1
    assert output[0]["content"] == "Test feedback"

    # Verify nothing printed to stdout
    captured = capsys.readouterr()
    assert captured.out == ""
