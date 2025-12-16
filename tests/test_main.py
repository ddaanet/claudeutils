"""Tests for claudeutils session discovery."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from claudeutils.main import (
    SessionInfo,
    encode_project_path,
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
