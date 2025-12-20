"""Command-line interface for claudeutils."""

# ruff: noqa: T201 - print statements are expected in CLI code
import argparse
import json
import re
import sys
from pathlib import Path

from claudeutils.discovery import list_top_level_sessions
from claudeutils.extraction import extract_feedback_recursively
from claudeutils.filtering import categorize_feedback, filter_feedback
from claudeutils.models import FeedbackItem
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


def handle_list(project: str) -> None:
    """Handle the list subcommand.

    Args:
        project: Project directory path
    """
    sessions = list_top_level_sessions(project)
    if not sessions:
        print("No sessions found")
    else:
        for session in sessions:
            prefix = session.session_id[:8]
            print(f"[{prefix}] {session.title}")


def handle_extract(session_prefix: str, project: str, output: str | None) -> None:
    """Handle the extract subcommand.

    Args:
        session_prefix: Session ID or prefix to extract from
        project: Project directory path
        output: Optional output file path
    """
    try:
        session_id = find_session_by_prefix(session_prefix, project)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    feedback = extract_feedback_recursively(session_id, project)
    json_output = json.dumps([item.model_dump(mode="json") for item in feedback])
    if output:
        Path(output).write_text(json_output)
    else:
        print(json_output)


def handle_collect(project: str, output: str | None) -> None:
    """Handle the collect subcommand.

    Args:
        project: Project directory path
        output: Optional output file path
    """
    sessions = list_top_level_sessions(project)
    all_feedback = []
    for session in sessions:
        try:
            feedback = extract_feedback_recursively(session.session_id, project)
            all_feedback.extend(feedback)
        except (ValueError, OSError, RuntimeError) as e:
            print(
                f"Warning: Failed to extract from {session.session_id}: {e}",
                file=sys.stderr,
            )
            continue

    json_output = json.dumps([item.model_dump(mode="json") for item in all_feedback])
    if output:
        Path(output).write_text(json_output)
    else:
        print(json_output)


def handle_analyze(input_path: str, output_format: str) -> None:
    """Handle the analyze subcommand.

    Args:
        input_path: Input JSON file path (or '-' for stdin)
        output_format: Output format ('text' or 'json')
    """
    # Load feedback from file or stdin
    json_text = sys.stdin.read() if input_path == "-" else Path(input_path).read_text()

    feedback_data = json.loads(json_text)
    items = [FeedbackItem.model_validate(item) for item in feedback_data]

    # Filter and categorize
    filtered_items = filter_feedback(items)
    categories: dict[str, int] = {}
    for item in filtered_items:
        category = categorize_feedback(item)
        categories[category] = categories.get(category, 0) + 1

    # Output results
    if output_format == "json":
        output = {
            "total": len(items),
            "filtered": len(filtered_items),
            "categories": categories,
        }
        print(json.dumps(output))
    else:
        print(f"total: {len(items)}")
        print(f"filtered: {len(filtered_items)}")
        print("categories:")
        for category, count in categories.items():
            print(f"  {category}: {count}")


def handle_rules(input_path: str, min_length: int, output_format: str) -> None:
    """Handle the rules subcommand.

    Args:
        input_path: Input JSON file path (or '-' for stdin)
        min_length: Minimum content length for rule-worthy items
        output_format: Output format ('text' or 'json')
    """
    # Load feedback from file or stdin
    json_text = sys.stdin.read() if input_path == "-" else Path(input_path).read_text()

    feedback_data = json.loads(json_text)
    items = [FeedbackItem.model_validate(item) for item in feedback_data]

    # Filter noise and apply stricter rules
    filtered_items = filter_feedback(items)
    rule_items = [
        item
        for item in filtered_items
        if not (
            # Question check
            (
                item.content.lower().startswith("how ")
                or item.content.lower().startswith("claude code:")
            )
            # Length check (min configurable, max 1000)
            or len(item.content) < min_length
            or len(item.content) > 1000
        )
    ]

    # Sort by timestamp and deduplicate by prefix
    rule_items.sort(key=lambda x: x.timestamp)
    seen_prefixes: set[str] = set()
    deduped_items = []
    for item in rule_items:
        prefix = item.content[:100].lower()
        if prefix not in seen_prefixes:
            seen_prefixes.add(prefix)
            deduped_items.append(item)

    # Output results
    if output_format == "json":
        output = [
            {
                "index": i + 1,
                "timestamp": item.timestamp,
                "session_id": item.session_id,
                "content": item.content,
            }
            for i, item in enumerate(deduped_items)
        ]
        print(json.dumps(output))
    else:
        for i, item in enumerate(deduped_items, 1):
            print(f"{i}. {item.content}")


def main() -> None:
    """Entry point for claudeutils CLI."""
    parser = argparse.ArgumentParser(
        description="Extract feedback from Claude Code sessions",
        epilog=(
            "Pipeline: collect -> analyze -> rules. Use collect to gather all "
            "feedback, analyze to filter and categorize, rules to extract "
            "actionable items."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    collect_parser = subparsers.add_parser(
        "collect",
        help="Batch collect feedback from all sessions",
        description=(
            "Extract feedback from all sessions recursively, including "
            "sub-agents. Outputs JSON array of FeedbackItem objects."
        ),
    )
    collect_parser.add_argument(
        "--project", default=str(Path.cwd()), help="Project directory"
    )
    collect_parser.add_argument("--output", help="Output file path")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze feedback items",
        description="""Filter noise and categorize feedback items.

Categories:
  instructions  - Directives (don't, never, always, must, should)
  corrections   - Fixes (no, wrong, incorrect, fix, error)
  process       - Workflow (plan, next step, before, after)
  code_review   - Quality (review, refactor, improve, clarity)
  preferences   - Other substantive feedback

Noise filtered: command output, bash stdout, system messages, short (<10 chars).""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analyze_parser.add_argument(
        "--input", required=True, help="Input JSON file, or '-' for stdin"
    )
    analyze_parser.add_argument(
        "--format", default="text", choices=["text", "json"], help="Output format"
    )

    rules_parser = subparsers.add_parser(
        "rules",
        help="Extract rule-worthy feedback items",
        description="""Extract actionable, rule-worthy feedback items.

Applies stricter filters than analyze:
  - Removes questions (starting with "How " or "claude code:")
  - Removes long items (>1000 chars)
  - Removes short items (<min-length, default 20 chars)
  - Deduplicates by first 100 characters

Output is sorted chronologically.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    rules_parser.add_argument(
        "--input", required=True, help="Input JSON file, or '-' for stdin"
    )
    rules_parser.add_argument(
        "--min-length",
        type=int,
        default=20,
        help="Minimum length for rule-worthy items (default: 20)",
    )
    rules_parser.add_argument(
        "--format", default="text", choices=["text", "json"], help="Output format"
    )

    args = parser.parse_args()

    if args.command == "list":
        handle_list(args.project)
    elif args.command == "extract":
        handle_extract(args.session_prefix, args.project, args.output)
    elif args.command == "collect":
        handle_collect(args.project, args.output)
    elif args.command == "analyze":
        handle_analyze(args.input, args.format)
    elif args.command == "rules":
        handle_rules(args.input, args.min_length, args.format)
