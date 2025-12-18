"""Claude history path and session discovery utilities."""

import json
import logging
import re
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FeedbackType(StrEnum):
    """Types of user feedback that can be extracted."""

    TOOL_DENIAL = "tool_denial"
    INTERRUPTION = "interruption"
    MESSAGE = "message"


class SessionInfo(BaseModel):
    """Model for session information."""

    session_id: str
    title: str
    timestamp: str


class FeedbackItem(BaseModel):
    """Model for extracted user feedback."""

    timestamp: str
    session_id: str
    feedback_type: FeedbackType
    content: str
    agent_id: str | None = None
    slug: str | None = None
    tool_use_id: str | None = None


def encode_project_path(project_dir: str) -> str:
    """Convert absolute path to Claude history encoding format."""
    if not Path(project_dir).is_absolute():
        msg = "project_dir must be an absolute path"
        raise ValueError(msg)
    # Handle root path specially
    if project_dir == "/":
        return "-"
    return project_dir.rstrip("/").replace("/", "-")


def get_project_history_dir(project_dir: str) -> Path:
    """Return Path to ~/.claude/projects/[ENCODED-PATH]/."""
    return Path.home() / ".claude" / "projects" / encode_project_path(project_dir)


def extract_content_text(content: str | list[dict[str, Any]]) -> str:
    """Extract text from string or array content."""
    if isinstance(content, str):
        return content
    # If it's a list, find first dict with type="text" and extract text field
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if isinstance(text, str):
                    return text
    return ""


def format_title(text: str) -> str:
    """Handle newlines and truncation in titles."""
    # Replace newlines with spaces
    text = text.replace("\n", " ")
    # Truncate to 80 chars if needed
    if len(text) > 80:
        text = text[:77] + "..."
    return text


def is_trivial(text: str) -> bool:
    """Determine whether user feedback should be filtered as trivial.

    Filters out:
    - Empty strings or whitespace only
    - Single characters
    - Short affirmations: y, n, k, g, ok, go, yes, no, continue, proceed,
      sure, okay, resume
    - Slash commands (starting with /)

    Args:
        text: User feedback text to evaluate

    Returns:
        True if text is trivial (should be filtered), False if substantive
    """
    stripped = text.strip()

    # Empty or whitespace only
    if not stripped:
        return True

    # Single character
    if len(stripped) == 1:
        return True

    # Slash command
    if stripped.startswith("/"):
        return True

    # Trivial keywords
    trivial_keywords = {
        "y",
        "n",
        "k",
        "g",
        "ok",
        "go",
        "yes",
        "no",
        "continue",
        "proceed",
        "sure",
        "okay",
        "resume",
    }

    return stripped.lower() in trivial_keywords


def list_top_level_sessions(project_dir: str) -> list[SessionInfo]:
    """List sessions sorted by timestamp with extracted titles."""
    history_dir = get_project_history_dir(project_dir)
    sessions = []

    # UUID regex pattern
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
    )

    # List all .jsonl files in the history directory
    if not history_dir.exists():
        return []

    for file_path in history_dir.glob("*.jsonl"):
        # Filter by UUID pattern
        if not uuid_pattern.match(file_path.name):
            continue

        # Extract session_id from filename
        session_id = file_path.name.replace(".jsonl", "")

        # Read first line and parse JSON
        try:
            with file_path.open() as f:
                first_line = f.readline().strip()
                if not first_line:
                    continue
                data = json.loads(first_line)
        except (json.JSONDecodeError, OSError):
            continue

        # Extract content and format title
        message = data.get("message", {})
        content = message.get("content", "")
        title = extract_content_text(content)
        title = format_title(title)

        # Extract timestamp
        timestamp = data.get("timestamp", "")

        sessions.append(
            SessionInfo(session_id=session_id, title=title, timestamp=timestamp)
        )

    # Sort by timestamp descending (most recent first)
    sessions.sort(key=lambda s: s.timestamp, reverse=True)

    return sessions


def extract_feedback_from_entry(entry: dict[str, Any]) -> FeedbackItem | None:
    """Extract non-trivial user feedback from a conversation entry.

    Args:
        entry: A conversation entry dict from a session JSONL file

    Returns:
        FeedbackItem if feedback is found, None otherwise
    """
    # Only process user messages
    if entry.get("type") != "user":
        return None

    # Extract content from message
    message = entry.get("message", {})
    content = message.get("content", "")

    # Check for tool denial (error in tool_result)
    if isinstance(content, list) and len(content) > 0:
        item = content[0]
        if isinstance(item, dict) and item.get("is_error") is True:
            error_content = item.get("content", "")
            tool_use_id = item.get("tool_use_id")
            return FeedbackItem(
                timestamp=entry.get("timestamp", ""),
                session_id=entry.get("sessionId", ""),
                feedback_type=FeedbackType.TOOL_DENIAL,
                content=error_content,
                agent_id=entry.get("agentId"),
                slug=entry.get("slug"),
                tool_use_id=tool_use_id,
            )

    # Extract text for regular messages
    text = extract_content_text(content)

    # Check for request interruption
    if "[Request interrupted" in text:
        return FeedbackItem(
            timestamp=entry.get("timestamp", ""),
            session_id=entry.get("sessionId", ""),
            feedback_type=FeedbackType.INTERRUPTION,
            content=text,
            agent_id=entry.get("agentId"),
            slug=entry.get("slug"),
        )

    # Filter trivial messages
    if is_trivial(text):
        return None

    # Create FeedbackItem for substantive messages
    return FeedbackItem(
        timestamp=entry.get("timestamp", ""),
        session_id=entry.get("sessionId", ""),
        feedback_type=FeedbackType.MESSAGE,
        content=text,
        agent_id=entry.get("agentId"),
        slug=entry.get("slug"),
    )


def find_sub_agent_ids(session_file: Path) -> list[str]:
    """Extract all sub-agent IDs from a session JSONL file.

    Scans for entries with successful Task tool completions that contain
    an agentId in the toolUseResult field.

    Args:
        session_file: Path to session JSONL file

    Returns:
        List of unique agent IDs (deduplicated, in order of first occurrence)
    """
    agent_ids = []
    seen: set[str] = set()

    with session_file.open() as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Check if entry has toolUseResult as a dict (successful completion)
            tool_result = entry.get("toolUseResult")
            if isinstance(tool_result, dict) and "agentId" in tool_result:
                agent_id = tool_result["agentId"]
                if agent_id not in seen:
                    agent_ids.append(agent_id)
                    seen.add(agent_id)

    return agent_ids


def main() -> None:
    """Entry point for claudeutils CLI."""


if __name__ == "__main__":
    main()
