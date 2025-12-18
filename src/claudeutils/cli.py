"""Command-line interface for claudeutils."""

# ruff: noqa: T201 - print statements are expected in CLI code
import argparse
import json
import re
import sys
from pathlib import Path

from claudeutils.discovery import list_top_level_sessions
from claudeutils.extraction import extract_feedback_recursively
from claudeutils.paths import get_project_history_dir


def find_session_by_prefix(prefix: str, project_dir: str) -> str:
    """Find unique session ID matching prefix.

    Args:
        prefix: Session ID prefix to match
        project_dir: Project directory path

    Returns:
        Full session ID

    Raises:
        ValueError: If 0 or >1 sessions match prefix
    """
    history_dir = get_project_history_dir(project_dir)
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
    )

    matches = []
    if history_dir.exists():
        for file_path in history_dir.glob("*.jsonl"):
            if not uuid_pattern.match(file_path.name):
                continue
            session_id = file_path.name.replace(".jsonl", "")
            if session_id.startswith(prefix):
                matches.append(session_id)

    if len(matches) == 0:
        msg = f"No session found with prefix '{prefix}'"
        raise ValueError(msg)
    if len(matches) > 1:
        msg = f"Multiple sessions match prefix '{prefix}'"
        raise ValueError(msg)

    return matches[0]


def main() -> None:
    """Entry point for claudeutils CLI."""
    parser = argparse.ArgumentParser(
        description="Extract feedback from Claude Code sessions"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List top-level sessions")
    list_parser.add_argument(
        "--project", default=str(Path.cwd()), help="Project directory"
    )

    extract_parser = subparsers.add_parser(
        "extract", help="Extract feedback from session"
    )
    extract_parser.add_argument("session_prefix", help="Session ID or prefix")
    extract_parser.add_argument(
        "--project", default=str(Path.cwd()), help="Project directory"
    )
    extract_parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    if args.command == "list":
        sessions = list_top_level_sessions(args.project)
        if not sessions:
            print("No sessions found")
        else:
            for session in sessions:
                prefix = session.session_id[:8]
                print(f"[{prefix}] {session.title}")
    elif args.command == "extract":
        try:
            session_id = find_session_by_prefix(args.session_prefix, args.project)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)

        feedback = extract_feedback_recursively(session_id, args.project)
        json_output = json.dumps([item.model_dump(mode="json") for item in feedback])
        if args.output:
            Path(args.output).write_text(json_output)
        else:
            print(json_output)
