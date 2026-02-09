"""Integration tests for recall analysis pipeline."""

from pathlib import Path

import pytest

from claudeutils.recall.index_parser import parse_memory_index
from claudeutils.recall.recall import calculate_recall
from claudeutils.recall.relevance import find_relevant_entries
from claudeutils.recall.report import generate_json_report, generate_markdown_report
from claudeutils.recall.tool_calls import extract_tool_calls_from_session
from claudeutils.recall.topics import extract_session_topics


@pytest.mark.e2e
def test_recall_pipeline_end_to_end(tmp_path: Path) -> None:
    """Test complete recall analysis pipeline with realistic data."""
    # Create index file
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "# Memory Index\n\n"
        "## agents/decisions/testing.md\n\n"
        "TDD RED Phase — verify behavior with mocking fixtures\n"
        "TDD GREEN Phase — implement feature implementation\n\n"
        "## agents/decisions/workflow.md\n\n"
        "Oneshot workflow — weak orchestrator pattern\n"
    )

    # Create session with relevant work
    session_file = tmp_path / "session.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"I want to implement TDD workflow testing"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"test-session"}\n'
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"grep_1","name":"Grep","input":{"path":"agents/decisions"}},{"type":"tool_use",'
        '"id":"read_1","name":"Read","input":{"file_path":"agents/decisions/testing.md"}}]},'
        '"timestamp":"2025-12-16T10:00:01.000Z","sessionId":"test-session"}\n'
        '{"type":"user","message":{"content":"Now I need to check the workflow"},'
        '"timestamp":"2025-12-16T10:00:02.000Z","sessionId":"test-session"}\n'
        '{"type":"assistant","message":{"content":[{"type":"tool_use",'
        '"id":"read_2","name":"Read","input":{"file_path":"agents/decisions/workflow.md"}}]},'
        '"timestamp":"2025-12-16T10:00:03.000Z","sessionId":"test-session"}\n'
    )

    # Parse index
    entries = parse_memory_index(index_file)
    assert len(entries) >= 3

    # Extract topics from session
    topics = extract_session_topics(session_file)
    assert "testing" in topics
    assert "workflow" in topics

    # Extract tool calls
    tool_calls = extract_tool_calls_from_session(session_file)
    assert len(tool_calls) == 4  # 1 grep, 3 reads
    assert tool_calls[0].tool_name == "Grep"
    assert tool_calls[1].tool_name == "Read"

    # Find relevant entries
    relevant = find_relevant_entries("test-session", topics, entries, threshold=0.3)
    assert len(relevant) > 0

    # Calculate recall
    sessions_data = {"test-session": tool_calls}
    relevant_entries = {"test-session": relevant}

    analysis = calculate_recall(sessions_data, relevant_entries, entries)

    assert analysis.sessions_analyzed == 1
    assert analysis.relevant_pairs_total > 0

    # Test report generation
    markdown_report = generate_markdown_report(analysis)
    assert "# Memory Index Recall Report" in markdown_report
    assert "Summary" in markdown_report
    assert "Per-Entry Analysis" in markdown_report

    json_report = generate_json_report(analysis)
    assert '"sessions_analyzed"' in json_report
    assert '"overall_recall_percent"' in json_report


def test_recall_pipeline_no_matches(tmp_path: Path) -> None:
    """Test pipeline with no matching entries."""
    index_file = tmp_path / "index.md"
    index_file.write_text(
        "## agents/decisions/testing.md\n\nTDD RED Phase — verify behavior\n"
    )

    session_file = tmp_path / "session.jsonl"
    session_file.write_text(
        '{"type":"user","message":{"content":"Fix that bug in the authentication module"},'
        '"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"test-session"}\n'
    )

    entries = parse_memory_index(index_file)
    topics = extract_session_topics(session_file)
    relevant = find_relevant_entries("test-session", topics, entries, threshold=0.3)

    # No relevant entries expected
    assert len(relevant) == 0


def test_recall_report_formatting(tmp_path: Path) -> None:
    """Test report formatting is correct."""
    index_file = tmp_path / "index.md"
    index_file.write_text("## test.md\n\nEntry — Description\n")

    entries = parse_memory_index(index_file)
    tool_calls = [
        __import__("claudeutils.recall.tool_calls", fromlist=["ToolCall"]).ToolCall(
            tool_name="Read",
            tool_id="read_1",
            input={"file_path": "test.md"},
            timestamp="2025-12-16T10:00:00.000Z",
            session_id="session1",
        )
    ]

    relevant_scores = [
        __import__(
            "claudeutils.recall.relevance", fromlist=["RelevanceScore"]
        ).RelevanceScore(
            session_id="session1",
            entry_key="Entry",
            score=0.8,
            is_relevant=True,
            matched_keywords={"entry"},
        )
    ]

    analysis = calculate_recall(
        {"session1": tool_calls},
        {"session1": relevant_scores},
        entries,
    )

    # Markdown report should have valid structure
    markdown = generate_markdown_report(analysis)
    assert "# Memory Index Recall Report" in markdown
    assert "## Summary" in markdown
    assert "## Per-Entry Analysis" in markdown
    assert "## Recommendations" in markdown
    assert "|" in markdown  # Table format

    # JSON should be valid
    json_text = generate_json_report(analysis)
    import json

    data = json.loads(json_text)
    assert data["sessions_analyzed"] == 1
    assert data["overall_recall_percent"] == 100.0
