"""Claude history path and session discovery utilities."""

import json
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class SessionInfo(BaseModel):
    """Model for session information."""

    session_id: str
    title: str
    timestamp: str


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


def list_top_level_sessions(project_dir: str) -> list[SessionInfo]:
    """Discovers UUID-named session files, extracts titles, sorts by timestamp."""
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


def main() -> None:
    """Entry point for claudeutils CLI."""


if __name__ == "__main__":
    main()
