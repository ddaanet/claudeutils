"""CLI command for memory index recall analysis."""

import sys
from pathlib import Path

import click

from claudeutils.discovery import list_top_level_sessions
from claudeutils.paths import get_project_history_dir
from claudeutils.recall.index_parser import parse_memory_index
from claudeutils.recall.recall import calculate_recall
from claudeutils.recall.relevance import find_relevant_entries
from claudeutils.recall.report import generate_json_report, generate_markdown_report
from claudeutils.recall.tool_calls import extract_tool_calls_from_session
from claudeutils.recall.topics import extract_session_topics


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
    "--baseline-before",
    default=None,
    type=str,
    help="ISO date cutoff for baseline sessions (format: YYYY-MM-DD)",
)
@click.option(
    "--threshold",
    default=0.3,
    type=float,
    help="Relevance threshold (default: 0.3)",
)
@click.option(
    "--format",
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
    baseline_before: str | None,
    threshold: float,
    format: str,
    output: str | None,
) -> None:
    """Analyze memory index recall effectiveness.

    Runs recall analysis on local session history to measure whether agents
    consult relevant memory index entries when working on related topics.
    """
    try:
        # Convert index path
        index_path = Path(index)
        if not index_path.exists():
            click.echo(f"Error: Index file not found: {index}", err=True)
            sys.exit(1)

        # Parse memory index
        index_entries = parse_memory_index(index_path)
        if not index_entries:
            click.echo("Error: No index entries parsed from index file", err=True)
            sys.exit(1)

        click.echo(f"Parsed {len(index_entries)} index entries")

        # Get project directory (assume current directory is project root)
        project_dir = str(Path.cwd())

        # List sessions
        all_sessions = list_top_level_sessions(project_dir)
        if not all_sessions:
            click.echo("Error: No sessions found in project history", err=True)
            sys.exit(1)

        click.echo(f"Found {len(all_sessions)} sessions")

        # Limit to requested number
        analyzed_sessions = all_sessions[:sessions]
        click.echo(f"Analyzing {len(analyzed_sessions)} sessions")

        # Get history directory
        history_dir = get_project_history_dir(project_dir)

        # Extract tool calls and topics per session
        sessions_data = {}
        relevant_entries = {}

        for session_info in analyzed_sessions:
            session_file = history_dir / f"{session_info.session_id}.jsonl"
            if not session_file.exists():
                continue

            # Extract tool calls
            tool_calls = extract_tool_calls_from_session(session_file)
            sessions_data[session_info.session_id] = tool_calls

            # Extract topics
            topics = extract_session_topics(session_file)
            if topics:
                # Find relevant entries
                relevant = find_relevant_entries(
                    session_info.session_id, topics, index_entries, threshold
                )
                if relevant:
                    relevant_entries[session_info.session_id] = relevant

        if not relevant_entries:
            click.echo("Warning: No relevant entries found in sessions", err=True)

        # Calculate recall metrics
        analysis = calculate_recall(sessions_data, relevant_entries, index_entries)

        # Generate report
        if format == "json":
            report_content = generate_json_report(analysis)
        else:
            report_content = generate_markdown_report(analysis)

        # Output report
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_content)
            click.echo(f"Report written to {output}")
        else:
            click.echo(report_content)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
