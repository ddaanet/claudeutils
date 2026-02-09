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


def extract_tool_calls_from_session(session_file: Path) -> list[ToolCall]:
    """Extract all tool calls from a session JSONL file.

    Processes each line, looking for assistant entries with tool_use content blocks.
    Skips malformed entries and logs warnings for graceful degradation.

    Args:
        session_file: Path to session JSONL file

    Returns:
        List of ToolCall objects sorted by timestamp
    """
    tool_calls: list[ToolCall] = []

    try:
        with session_file.open() as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Malformed JSON in {session_file.name} line {line_num}: {e}"
                    )
                    continue

                # Only process assistant entries
                if entry.get("type") != "assistant":
                    continue

                # Extract timestamp and session_id
                timestamp = entry.get("timestamp", "")
                session_id = entry.get("sessionId", "")

                # Process content array looking for tool_use blocks
                message = entry.get("message", {})
                content = message.get("content", [])
                if not isinstance(content, list):
                    continue

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
                            f"Incomplete tool_use block in {session_file.name} "
                            f"line {line_num}"
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
                    except Exception as e:
                        logger.warning(
                            f"Failed to create ToolCall in {session_file.name} "
                            f"line {line_num}: {e}"
                        )
                        continue

    except OSError as e:
        logger.warning(f"Failed to read {session_file}: {e}")
        return []

    # Sort by timestamp
    tool_calls.sort(key=lambda tc: tc.timestamp)

    return tool_calls
