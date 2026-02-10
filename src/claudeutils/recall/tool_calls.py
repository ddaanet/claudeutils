"""Extract tool calls from session JSONL files."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolCall(BaseModel):
    """Tool call extracted from assistant JSONL entry."""

    tool_name: str  # "Read", "Grep", "Glob", "Bash", "Write", etc.
    tool_id: str  # tool_use id for correlation
    input: dict[str, Any]  # tool-specific arguments
    timestamp: str  # ISO 8601
    session_id: str


def _parse_json_line(
    raw_line: str, line_num: int, session_file: Path
) -> dict[str, Any] | None:
    """Parse JSON line with error handling."""
    json_line = raw_line.strip()
    if not json_line:
        return None

    try:
        entry: dict[str, Any] = json.loads(json_line)
    except json.JSONDecodeError as e:
        logger.warning(
            "Malformed JSON in %s line %s: %s",
            session_file.name,
            line_num,
            e,
        )
        return None
    else:
        return entry


def _extract_tool_calls_from_content(
    content: list[Any],
    timestamp: str,
    session_id: str,
    line_num: int,
    session_file: Path,
) -> list[ToolCall]:
    """Extract tool calls from content blocks."""
    tool_calls: list[ToolCall] = []

    for content_block in content:
        if not isinstance(content_block, dict):
            continue

        if content_block.get("type") != "tool_use":
            continue

        tool_name = content_block.get("name")
        tool_id = content_block.get("id")
        input_data = content_block.get("input", {})

        if not tool_name or not tool_id:
            logger.warning(
                "Incomplete tool_use block in %s line %s",
                session_file.name,
                line_num,
            )
            continue

        try:
            tool_call = ToolCall(
                tool_name=tool_name,
                tool_id=tool_id,
                input=input_data,
                timestamp=timestamp,
                session_id=session_id,
            )
            tool_calls.append(tool_call)
        except (TypeError, ValueError) as e:
            logger.warning(
                "Failed to create ToolCall in %s line %s: %s",
                session_file.name,
                line_num,
                e,
            )

    return tool_calls


def extract_tool_calls_from_session(session_file: Path) -> list[ToolCall]:
    """Extract tool calls from session JSONL file."""
    tool_calls: list[ToolCall] = []

    try:
        with session_file.open() as f:
            for line_num, raw_line in enumerate(f, 1):
                entry = _parse_json_line(raw_line, line_num, session_file)
                if not entry:
                    continue

                if entry.get("type") != "assistant":
                    continue

                timestamp = entry.get("timestamp", "")
                session_id = entry.get("sessionId", "")

                message = entry.get("message", {})
                content = message.get("content", [])
                if not isinstance(content, list):
                    continue

                calls = _extract_tool_calls_from_content(
                    content, timestamp, session_id, line_num, session_file
                )
                tool_calls.extend(calls)

    except OSError as e:
        logger.warning("Failed to read %s: %s", session_file, e)
        return []

    tool_calls.sort(key=lambda tc: tc.timestamp)
    return tool_calls
