"""Tests for claudeutils session discovery."""

import json
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from claudeutils.main import (
    FeedbackItem,
    FeedbackType,
    SessionInfo,
    encode_project_path,
    extract_feedback_from_entry,
    find_sub_agent_ids,
    get_project_history_dir,
    is_trivial,
    list_top_level_sessions,
)


@pytest.fixture
def temp_project_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Create temporary project and history directories."""
    project = tmp_path / "myproject"
    project.mkdir()

    history_dir = tmp_path / ".claude" / "projects" / "-tmp-myproject"
    history_dir.mkdir(parents=True)

    def mock_get_history(proj: str) -> Path:
        return history_dir

    monkeypatch.setattr("claudeutils.main.get_project_history_dir", mock_get_history)

    return project, history_dir


# ============= GROUP A: Path Encoding =============


def test_encode_project_path_basic() -> None:
    """Encode standard project paths."""
    assert encode_project_path("/Users/david/code/foo") == "-Users-david-code-foo"
    assert encode_project_path("/home/user/project") == "-home-user-project"


def test_encode_project_path_root() -> None:
    """Handle root path edge case."""
    assert encode_project_path("/") == "-"


def test_encode_project_path_rejects_relative() -> None:
    """Reject relative paths that don't start with /."""
    with pytest.raises(ValueError, match="absolute"):
        encode_project_path("relative/path")


def test_encode_project_path_trailing_slash() -> None:
    """Strip trailing slash from output."""
    assert encode_project_path("/Users/david/code/foo/") == "-Users-david-code-foo"


# ============= GROUP B: History Directory =============


def test_get_project_history_dir_basic() -> None:
    """Construct standard history directory path."""
    result = get_project_history_dir("/Users/david/code/foo")
    expected = Path.home() / ".claude" / "projects" / "-Users-david-code-foo"
    assert result == expected


def test_get_project_history_dir_returns_path() -> None:
    """Return Path object, not string."""
    result = get_project_history_dir("/Users/david/code/foo")
    assert isinstance(result, Path)


def test_get_project_history_dir_uses_encoding() -> None:
    """Use encode_project_path() for encoded portion."""
    project = "/home/user/project"
    result = get_project_history_dir(project)
    encoded = encode_project_path(project)
    assert result.name == encoded


# ============= GROUP C: SessionInfo Model =============


def test_session_info_creation() -> None:
    """Create SessionInfo with required fields and correct types."""
    info = SessionInfo(
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        title="Design a python script",
        timestamp="2025-12-16T08:39:26.932Z",
    )
    assert info.session_id == "e12d203f-ca65-44f0-9976-cb10b74514c1"
    assert info.title == "Design a python script"
    assert info.timestamp == "2025-12-16T08:39:26.932Z"


def test_session_info_validation() -> None:
    """Validate types with Pydantic."""
    with pytest.raises(ValidationError):
        # Intentionally pass wrong types to test Pydantic validation
        SessionInfo(session_id=123, title="foo", timestamp="bar")  # type: ignore[arg-type]


# ============= GROUP D: Session Discovery =============


def test_list_sessions_basic_discovery(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Discover all UUID-named session files."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"First"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "a1b2c3d4-1234-5678-9abc-def012345678.jsonl").write_text(
        '{"type":"user","message":{"content":"Second"},"timestamp":"2025-12-16T11:00:00.000Z","sessionId":"a1b2c3d4-1234-5678-9abc-def012345678"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions) == 2


def test_list_sessions_filters_agents(temp_project_dir: tuple[Path, Path]) -> None:
    """Exclude agent-*.jsonl files."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Main"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "agent-a6755ed.jsonl").write_text(
        '{"type":"user","message":{"content":"Agent"},"timestamp":"2025-12-16T10:05:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions) == 1
    assert sessions[0].session_id == "e12d203f-ca65-44f0-9976-cb10b74514c1"


def test_list_sessions_sorted_by_timestamp(temp_project_dir: tuple[Path, Path]) -> None:
    """Show most recent session first."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Middle"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )
    (history_dir / "a1b2c3d4-1234-5678-9abc-def012345678.jsonl").write_text(
        '{"type":"user","message":{"content":"Latest"},"timestamp":"2025-12-16T12:00:00.000Z","sessionId":"a1b2c3d4-1234-5678-9abc-def012345678"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Latest"
    assert sessions[1].title == "Middle"


def test_list_sessions_extracts_title_from_string_content(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Handle content as string."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Design a python script"},'
        '"timestamp":"2025-12-16T10:00:00.000Z",'
        '"sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Design a python script"


def test_list_sessions_extracts_title_from_array_content(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Handle content as array with text blocks."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":[{"type":"text",'
        '"text":"Help me with this"}]},"timestamp":"2025-12-16T10:00:00.000Z",'
        '"sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Help me with this"


def test_list_sessions_truncates_long_titles(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Truncate titles longer than 80 chars with ..."""
    project, history_dir = temp_project_dir

    long_text = "A" * 100
    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        f'{{"type":"user","message":{{"content":"{long_text}"}},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert len(sessions[0].title) == 80
    assert sessions[0].title == ("A" * 77 + "...")


def test_list_sessions_handles_newlines_in_title(
    temp_project_dir: tuple[Path, Path],
) -> None:
    """Replace newlines with spaces in multi-line messages."""
    project, history_dir = temp_project_dir

    (history_dir / "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl").write_text(
        '{"type":"user","message":{"content":"Line one\\nLine two"},'
        '"timestamp":"2025-12-16T10:00:00.000Z",'
        '"sessionId":"e12d203f-ca65-44f0-9976-cb10b74514c1"}\n'
    )

    sessions = list_top_level_sessions(str(project))
    assert sessions[0].title == "Line one Line two"


# ============= GROUP E: Trivial Feedback Filter =============


def test_is_trivial_empty_string() -> None:
    """Empty string is trivial."""
    assert is_trivial("") is True


def test_is_trivial_whitespace_only() -> None:
    """Whitespace-only strings are trivial."""
    assert is_trivial(" ") is True
    assert is_trivial("   ") is True
    assert is_trivial("\t") is True
    assert is_trivial("\n") is True
    assert is_trivial(" \t\n ") is True


def test_is_trivial_single_character() -> None:
    """Any single character is trivial."""
    assert is_trivial("a") is True
    assert is_trivial("z") is True
    assert is_trivial("1") is True
    assert is_trivial("!") is True
    assert is_trivial(" x ") is True  # Single char with whitespace


def test_is_trivial_yes_no_variants() -> None:
    """Yes/no variations are trivial (case-insensitive)."""
    assert is_trivial("y") is True
    assert is_trivial("Y") is True
    assert is_trivial("n") is True
    assert is_trivial("N") is True
    assert is_trivial("yes") is True
    assert is_trivial("YES") is True
    assert is_trivial("no") is True
    assert is_trivial("No") is True


def test_is_trivial_keywords_with_whitespace() -> None:
    """Trivial keywords with leading/trailing whitespace."""
    for text in [" continue ", "\tok\t", "  yes  ", "\nresume\n"]:
        assert is_trivial(text) is True


def test_is_trivial_slash_commands() -> None:
    """Slash commands are trivial."""
    for text in ["/model", "/clear", "/help", "/commit", " /model "]:
        assert is_trivial(text) is True


def test_is_trivial_substantive_messages() -> None:
    """Substantive messages are NOT trivial."""
    for text in [
        "Design a python script",
        "Help me with this bug",
        "yesterday",  # Contains 'y' but not exact match
        "yes I think that works",  # Contains keyword with other text
    ]:
        assert is_trivial(text) is False


def test_is_trivial_exact_match_only() -> None:
    """Case insensitivity applies only to exact keyword matches."""
    # Exact matches are trivial
    for text in ["YeS", "OK", "ContinUE"]:
        assert is_trivial(text) is True

    # Keywords + extra text are NOT trivial
    for text in ["Yes please", "OK done", "continue with this"]:
        assert is_trivial(text) is False


# ============= GROUP F: Message Parsing =============


def test_extract_feedback_non_user_message() -> None:
    """Non-user messages (type=assistant) return None."""
    entry = {
        "type": "assistant",
        "message": {"role": "assistant", "content": "Some response"},
        "timestamp": "2025-12-16T08:39:26.932Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    assert extract_feedback_from_entry(entry) is None


def test_extract_feedback_trivial_message() -> None:
    """Trivial user messages return None."""
    entry = {
        "type": "user",
        "message": {"role": "user", "content": "resume"},
        "timestamp": "2025-12-16T08:43:52.198Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    assert extract_feedback_from_entry(entry) is None


def test_extract_feedback_substantive_message() -> None:
    """Substantive user messages return FeedbackItem."""
    content = "Design a python script to extract user feedback"
    entry = {
        "type": "user",
        "message": {"role": "user", "content": content},
        "timestamp": "2025-12-16T08:39:26.932Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    expected = FeedbackItem(
        timestamp="2025-12-16T08:39:26.932Z",
        session_id="e12d203f-ca65-44f0-9976-cb10b74514c1",
        feedback_type=FeedbackType.MESSAGE,
        content=content,
    )
    assert extract_feedback_from_entry(entry) == expected


def test_extract_feedback_tool_denial_main_session() -> None:
    """Tool denial in main session returns FeedbackItem."""
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "is_error": True,
                    "content": "[Request interrupted by user for tool use]",
                    "tool_use_id": "toolu_01Q9nwwXaokrfKdLpUDCLHt7",
                }
            ],
        },
        "timestamp": "2025-12-16T08:43:43.872Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.feedback_type == FeedbackType.TOOL_DENIAL
    assert result.tool_use_id == "toolu_01Q9nwwXaokrfKdLpUDCLHt7"
    assert result.content == "[Request interrupted by user for tool use]"
    assert result.agent_id is None


def test_extract_feedback_tool_denial_subagent() -> None:
    """Tool denial in sub-agent includes agentId and slug."""
    denial_msg = (
        "The user doesn't want to proceed with this tool use. "
        "The tool use was rejected (eg. if it was a file edit, the "
        "new_string was NOT written to the file). STOP what you are "
        "doing and wait for the user to tell you how to proceed."
    )
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "content": denial_msg,
                    "is_error": True,
                    "tool_use_id": "toolu_0165cVNnbPXQCt22gTrTXnQq",
                }
            ],
        },
        "timestamp": "2025-12-16T08:43:43.789Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
        "agentId": "a6755ed",
        "slug": "fluffy-cuddling-forest",
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.feedback_type == FeedbackType.TOOL_DENIAL
    assert result.agent_id == "a6755ed"
    assert result.slug == "fluffy-cuddling-forest"
    assert result.content == denial_msg


def test_extract_feedback_request_interruption() -> None:
    """Request interruption returns FeedbackItem with INTERRUPTION type."""
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {"type": "text", "text": "[Request interrupted by user for tool use]"}
            ],
        },
        "timestamp": "2025-12-16T08:43:43.872Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.feedback_type == FeedbackType.INTERRUPTION
    assert "[Request interrupted" in result.content


def test_extract_feedback_missing_session_id() -> None:
    """Missing sessionId field returns FeedbackItem with empty string."""
    entry = {
        "type": "user",
        "message": {"role": "user", "content": "Design a python script"},
        "timestamp": "2025-12-16T08:39:26.932Z",
    }
    result = extract_feedback_from_entry(entry)
    assert result is not None
    assert result.session_id == ""


def test_extract_feedback_malformed_content_empty_list() -> None:
    """Tool result with empty content list returns None."""
    entry = {
        "type": "user",
        "message": {
            "role": "user",
            "content": [],
        },
        "timestamp": "2025-12-16T08:39:26.932Z",
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    assert extract_feedback_from_entry(entry) is None


def test_extract_feedback_pydantic_validation_error() -> None:
    """Invalid timestamp format raises ValidationError."""
    entry = {
        "type": "user",
        "message": {"role": "user", "content": "Design a script"},
        "timestamp": 12345,  # Invalid: should be string
        "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    }
    with pytest.raises(ValidationError):
        extract_feedback_from_entry(entry)


# ============= GROUP G: Recursive Sub-Agent Processing =============


def test_find_sub_agent_ids_successful_tasks() -> None:
    """Extract agent IDs from successful Task tool completions."""
    entries = [
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ae9906a",
                "content": [],
                "totalDurationMs": 5000,
            },
            "timestamp": "2025-12-16T08:47:19.855Z",
            "sessionId": "main-session-id",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": "Agent completed",
                        "tool_use_id": "toolu_abc123",
                    }
                ],
            },
        },
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ad67fd8",
                "content": [],
                "totalDurationMs": 3000,
            },
            "timestamp": "2025-12-16T08:48:00.000Z",
            "sessionId": "main-session-id",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": "Agent completed",
                        "tool_use_id": "toolu_xyz789",
                    }
                ],
            },
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == ["ae9906a", "ad67fd8"]


def test_find_sub_agent_ids_no_tasks() -> None:
    """Session with no Task calls returns empty list."""
    entries = [
        {
            "type": "user",
            "message": {"role": "user", "content": "Design a script"},
            "timestamp": "2025-12-16T08:39:26.932Z",
            "sessionId": "main-session-id",
        },
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": "I'll help you design a script",
            },
            "timestamp": "2025-12-16T08:39:27.000Z",
            "sessionId": "main-session-id",
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == []


def test_find_sub_agent_ids_duplicates_deduplicated() -> None:
    """Duplicate agent IDs are deduplicated."""
    entries = [
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ae9906a",
                "content": [],
                "totalDurationMs": 5000,
            },
            "timestamp": "2025-12-16T08:47:19.855Z",
            "sessionId": "main-session-id",
            "message": {"role": "user", "content": []},
        },
        {
            "type": "user",
            "toolUseResult": {
                "status": "completed",
                "agentId": "ae9906a",
                "content": [],
                "totalDurationMs": 3000,
            },
            "timestamp": "2025-12-16T08:48:00.000Z",
            "sessionId": "main-session-id",
            "message": {"role": "user", "content": []},
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == ["ae9906a"]


def test_find_sub_agent_ids_interrupted_task_ignored() -> None:
    """Interrupted Task (string toolUseResult) is ignored."""
    entries = [
        {
            "type": "user",
            "toolUseResult": "Error: [Request interrupted by user for tool use]",
            "timestamp": "2025-12-16T08:43:43.872Z",
            "sessionId": "main-session-id",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "content": "[Request interrupted by user for tool use]",
                        "is_error": True,
                        "tool_use_id": "toolu_xyz789",
                    }
                ],
            },
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        session_path = Path(tmpdir) / "test_session.jsonl"
        with session_path.open("w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        result = find_sub_agent_ids(session_path)
        assert result == []
