"""Command-line interface for claudeutils."""

# ruff: noqa: T201 - print statements are expected in CLI code
import json
import logging
import re
import sys
from pathlib import Path

import click

from claudeutils.discovery import list_top_level_sessions
from claudeutils.extraction import extract_feedback_recursively
from claudeutils.filtering import categorize_feedback, filter_feedback
from claudeutils.markdown import process_file
from claudeutils.models import FeedbackItem
from claudeutils.paths import get_project_history_dir
from claudeutils.tokens_cli import handle_tokens


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


@click.group(
    help="Extract feedback from Claude Code sessions",
    epilog=(
        "Pipeline: collect -> analyze -> rules. Use collect to gather all "
        "feedback, analyze to filter and categorize, rules to extract "
        "actionable items."
    ),
)
def cli() -> None:
    """Entry point for claudeutils CLI."""
    # Configure logging to show warnings on terminal
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )


@cli.command("list", help="List top-level sessions")
@click.option("--project", default=None, help="Project directory")
def list_sessions(project: str | None) -> None:
    """Handle the list subcommand."""
    if project is None:
        project = str(Path.cwd())
    sessions = list_top_level_sessions(project)
    if not sessions:
        print("No sessions found")
    else:
        for session in sessions:
            prefix = session.session_id[:8]
            print(f"[{prefix}] {session.title}")


@cli.command(help="Extract feedback from session")
@click.argument("session_prefix")
@click.option("--project", default=None, help="Project directory")
@click.option("--output", help="Output file path")
def extract(session_prefix: str, project: str | None, output: str | None) -> None:
    """Handle the extract subcommand."""
    if project is None:
        project = str(Path.cwd())
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


@cli.command(
    help="Batch collect feedback from all sessions",
    epilog=(
        "Extract feedback from all sessions recursively, including "
        "sub-agents. Outputs JSON array of FeedbackItem objects."
    ),
)
@click.option("--project", default=None, help="Project directory")
@click.option("--output", help="Output file path")
def collect(project: str | None, output: str | None) -> None:
    """Handle the collect subcommand."""
    if project is None:
        project = str(Path.cwd())
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


@cli.command(
    help="Analyze feedback items",
    epilog="""Categories:
  instructions  - Directives (don't, never, always, must, should)
  corrections   - Fixes (no, wrong, incorrect, fix, error)
  process       - Workflow (plan, next step, before, after)
  code_review   - Quality (review, refactor, improve, clarity)
  preferences   - Other substantive feedback

Noise filtered: command output, bash stdout, system messages, short (<10 chars).""",
)
@click.option(
    "--input", "input_path", required=True, help="Input JSON file, or '-' for stdin"
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def analyze(input_path: str, output_format: str) -> None:
    """Handle the analyze subcommand."""
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


@cli.command(
    help="Extract rule-worthy feedback items",
    epilog="""Applies stricter filters than analyze:
  - Removes questions (starting with "How " or "claude code:")
  - Removes long items (>1000 chars)
  - Removes short items (<min-length, default 20 chars)
  - Deduplicates by first 100 characters

Output is sorted chronologically.""",
)
@click.option(
    "--input", "input_path", required=True, help="Input JSON file, or '-' for stdin"
)
@click.option(
    "--min-length",
    type=int,
    default=20,
    help="Minimum length for rule-worthy items (default: 20)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def rules(input_path: str, min_length: int, output_format: str) -> None:
    """Handle the rules subcommand."""
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


@cli.command(
    help=(
        "Count tokens in files using Anthropic API. "
        "Requires ANTHROPIC_API_KEY environment variable."
    ),
    epilog=(
        "Examples:\n"
        "  uv run claudeutils tokens sonnet prompt.md\n"
        "  uv run claudeutils tokens opus file1.md file2.md --json\n"
        "  uv run claudeutils tokens claude-sonnet-4-5-20250929 prompt.md"
    ),
)
@click.argument("model", metavar="{haiku,sonnet,opus}")
@click.argument("files", nargs=-1, required=True, metavar="FILE")
@click.option(
    "--json", "json_output", is_flag=True, help="Output JSON format instead of text"
)
def tokens(model: str, files: tuple[str, ...], *, json_output: bool) -> None:
    """Handle the tokens subcommand."""
    handle_tokens(model, list(files), json_output=json_output)


@cli.command(help="Process markdown files")
def markdown() -> None:
    """Handle the markdown subcommand.

    Reads file paths from stdin, processes markdown structure fixes, and prints
    modified file paths to stdout.
    """
    files = [line.strip() for line in sys.stdin if line.strip()]

    # Validate all files first
    errors: list[str] = []
    valid_files: list[Path] = []
    for filepath_str in files:
        filepath = Path(filepath_str)
        if filepath.suffix != ".md":
            errors.append(f"Error: {filepath_str} is not a markdown file")
        elif not filepath.exists():
            errors.append(f"Error: {filepath_str} does not exist")
        else:
            valid_files.append(filepath)

    # Process valid files
    for filepath in valid_files:
        if process_file(filepath):
            print(str(filepath))

    # Report all errors and exit with error code
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point for claudeutils CLI."""
    cli()
