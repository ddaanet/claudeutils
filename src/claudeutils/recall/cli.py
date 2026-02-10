"""CLI command for memory index recall analysis."""

import sys
from pathlib import Path
from typing import Any

import click

from claudeutils.discovery import list_top_level_sessions
from claudeutils.paths import get_project_history_dir
from claudeutils.recall.index_parser import parse_memory_index
from claudeutils.recall.recall import calculate_recall
from claudeutils.recall.relevance import find_relevant_entries
from claudeutils.recall.report import generate_json_report, generate_markdown_report
from claudeutils.recall.tool_calls import extract_tool_calls_from_session
from claudeutils.recall.topics import extract_session_topics


def _load_and_validate_index(index: str) -> list[Any]:
    """Load and validate memory index entries."""
    index_path = Path(index)
    if not index_path.exists():
        click.echo(f"Error: Index file not found: {index}", err=True)
        sys.exit(1)

    index_entries = parse_memory_index(index_path)
    if not index_entries:
        click.echo("Error: No index entries parsed from index file", err=True)
        sys.exit(1)

    click.echo(f"Parsed {len(index_entries)} index entries")
    return index_entries


def _get_analyzed_sessions(project_dir: str, sessions: int) -> tuple[list[Any], Path]:
    """Get list of sessions to analyze and history directory."""
    all_sessions = list_top_level_sessions(project_dir)
    if not all_sessions:
        click.echo("Error: No sessions found in project history", err=True)
        sys.exit(1)

    click.echo(f"Found {len(all_sessions)} sessions")
    analyzed_sessions = all_sessions[:sessions]
    click.echo(f"Analyzing {len(analyzed_sessions)} sessions")

    history_dir = get_project_history_dir(project_dir)
    return analyzed_sessions, history_dir


def _process_sessions(
    analyzed_sessions: list[Any],
    history_dir: Path,
    index_entries: list[Any],
    threshold: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract tool calls and find relevant entries for each session."""
    sessions_data = {}
    relevant_entries = {}

    for session_info in analyzed_sessions:
        session_file = history_dir / f"{session_info.session_id}.jsonl"
        if not session_file.exists():
            continue

        tool_calls = extract_tool_calls_from_session(session_file)
        sessions_data[session_info.session_id] = tool_calls

        topics = extract_session_topics(session_file)
        if topics:
            relevant = find_relevant_entries(
                session_info.session_id, topics, index_entries, threshold
            )
            if relevant:
                relevant_entries[session_info.session_id] = relevant

    if not relevant_entries:
        click.echo("Warning: No relevant entries found in sessions", err=True)

    return sessions_data, relevant_entries


def _write_report(report_content: str, output: str | None) -> None:
    """Write report to file or stdout."""
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content)
        click.echo(f"Report written to {output}")
    else:
        click.echo(report_content)


@click.command()
@click.option(
    "--index",
    required=True,
    type=click.Path(exists=True),
    help="Path to memory-index.md",
)
@click.option(
    "--sessions",
    default=30,
    type=int,
    help="Number of recent sessions to analyze (default: 30)",
)
@click.option(
    "--threshold",
    default=0.3,
    type=float,
    help="Relevance threshold (default: 0.3)",
)
@click.option(
    "--format",
    "output_format",
    default="markdown",
    type=click.Choice(["markdown", "json"]),
    help="Output format (default: markdown)",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Write report to file (default: stdout)",
)
def recall(
    index: str,
    sessions: int,
    threshold: float,
    output_format: str,
    output: str | None,
) -> None:
    """Analyze memory index recall effectiveness."""
    try:
        index_entries = _load_and_validate_index(index)
        project_dir = str(Path.cwd())
        analyzed_sessions, history_dir = _get_analyzed_sessions(project_dir, sessions)

        sessions_data, relevant_entries = _process_sessions(
            analyzed_sessions, history_dir, index_entries, threshold
        )

        analysis = calculate_recall(sessions_data, relevant_entries, index_entries)

        if output_format == "json":
            report_content = generate_json_report(analysis)
        else:
            report_content = generate_markdown_report(analysis)

        _write_report(report_content, output)

    except (OSError, ValueError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
