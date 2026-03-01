"""Tests for topic matching and inverted index construction."""

import json
import os
import time
from pathlib import Path

import pytest

from claudeutils.recall.index_parser import IndexEntry, parse_memory_index
from claudeutils.recall.relevance import RelevanceScore
from claudeutils.recall.topic_matcher import (
    ResolvedEntry,
    TopicMatchResult,
    build_inverted_index,
    format_output,
    get_candidates,
    get_or_build_index,
    resolve_entries,
    score_and_rank,
)


def test_build_inverted_index_maps_keywords_to_entries() -> None:
    """build_inverted_index should map each keyword to entries containing it."""
    entry_a = IndexEntry(
        key="test_a",
        description="description_a",
        referenced_file="file_a.md",
        section="Section A",
        keywords=frozenset({"recall", "system", "effectiveness"}),
    )
    entry_b = IndexEntry(
        key="test_b",
        description="description_b",
        referenced_file="file_b.md",
        section="Section B",
        keywords=frozenset({"recall", "hook", "injection"}),
    )
    entry_c = IndexEntry(
        key="test_c",
        description="description_c",
        referenced_file="file_c.md",
        section="Section C",
        keywords=frozenset({"commit", "message", "format"}),
    )

    index = build_inverted_index([entry_a, entry_b, entry_c])

    assert isinstance(index, dict)
    assert "recall" in index
    assert len(index["recall"]) == 2
    assert entry_a in index["recall"]
    assert entry_b in index["recall"]

    assert "hook" in index
    assert len(index["hook"]) == 1
    assert entry_b in index["hook"]

    assert "commit" in index
    assert len(index["commit"]) == 1
    assert entry_c in index["commit"]

    expected_keys = {
        "recall",
        "system",
        "effectiveness",
        "hook",
        "injection",
        "commit",
        "message",
        "format",
    }
    assert set(index.keys()) == expected_keys


def test_match_prompt_returns_candidates_with_overlap() -> None:
    """get_candidates should return entries matching prompt keywords."""
    entry_a = IndexEntry(
        key="test_a",
        description="description_a",
        referenced_file="file_a.md",
        section="Section A",
        keywords=frozenset({"recall", "system", "effectiveness"}),
    )
    entry_b = IndexEntry(
        key="test_b",
        description="description_b",
        referenced_file="file_b.md",
        section="Section B",
        keywords=frozenset({"recall", "hook", "injection"}),
    )
    entry_c = IndexEntry(
        key="test_c",
        description="description_c",
        referenced_file="file_c.md",
        section="Section C",
        keywords=frozenset({"commit", "message", "format"}),
    )

    inverted_index = build_inverted_index([entry_a, entry_b, entry_c])

    candidates = get_candidates("how does the recall system work", inverted_index)

    assert isinstance(candidates, set)
    assert entry_a in candidates
    assert entry_b in candidates
    assert entry_c not in candidates
    assert len(candidates) == 2


@pytest.mark.parametrize(
    ("threshold", "max_entries"),
    [(0.3, None), (0.3, 2)],
)
def test_score_candidates_ranks_by_relevance_and_filters(
    threshold: float, max_entries: int | None
) -> None:
    """score_and_rank should rank by relevance and apply threshold/cap."""
    entry_high = IndexEntry(
        key="high_match",
        description="test entry",
        referenced_file="file_a.md",
        section="Section A",
        keywords=frozenset({"recall", "system", "matching"}),
    )
    entry_mid = IndexEntry(
        key="mid_match",
        description="test entry",
        referenced_file="file_b.md",
        section="Section B",
        keywords=frozenset({"recall", "matching"}),
    )
    entry_low = IndexEntry(
        key="low_match",
        description="test entry",
        referenced_file="file_c.md",
        section="Section C",
        keywords=frozenset(
            {
                "other",
                "unrelated",
                "keywords",
                "none",
                "match",
                "here",
                "at",
                "all",
                "in",
            }
        ),
    )
    entry_cap1 = IndexEntry(
        key="cap1",
        description="test entry",
        referenced_file="file_d.md",
        section="Section D",
        keywords=frozenset({"recall", "test"}),
    )
    entry_cap2 = IndexEntry(
        key="cap2",
        description="test entry",
        referenced_file="file_e.md",
        section="Section E",
        keywords=frozenset({"system"}),
    )

    prompt_keywords = {"recall", "system", "matching"}
    candidates = {entry_high, entry_mid, entry_low, entry_cap1, entry_cap2}

    result = score_and_rank(
        prompt_keywords, candidates, threshold=threshold, max_entries=max_entries
    )

    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
    assert all(isinstance(item[1], RelevanceScore) for item in result)
    assert all(item[1].score >= threshold for item in result)

    if max_entries:
        assert len(result) <= max_entries

    if len(result) > 1:
        scores = [item[1].score for item in result]
        assert scores == sorted(scores, reverse=True)


def test_resolve_entries_extracts_section_content(tmp_path: Path) -> None:
    """resolve_entries returns content when file and section exist."""
    decision_file = tmp_path / "agents" / "decisions" / "test.md"
    decision_file.parent.mkdir(parents=True, exist_ok=True)
    decision_file.write_text(
        "# Test Decisions\n\n"
        "## When Evaluating Recall System Effectiveness\n\n"
        "Anti-pattern: Measuring without proper baseline\n\n"
        "## Other Section\n\n"
        "Other content here\n"
    )

    entry = IndexEntry(
        key="evaluating recall system effectiveness",
        description="test entry",
        referenced_file="agents/decisions/test.md",
        section="Test",
        keywords=frozenset({"recall", "effectiveness"}),
    )
    score = RelevanceScore(
        session_id="hook",
        entry_key=entry.key,
        score=0.8,
        is_relevant=True,
        matched_keywords={"recall", "effectiveness"},
    )

    result = resolve_entries([(entry, score)], tmp_path)

    assert len(result) == 1
    assert "Evaluating Recall System Effectiveness" in result[0].content
    assert "Anti-pattern" in result[0].content
    assert str(decision_file) == str(result[0].source_file)


def test_resolve_entries_skips_missing_file(tmp_path: Path) -> None:
    """resolve_entries silently skips entries whose file does not exist."""
    entry = IndexEntry(
        key="nonexistent",
        description="test entry",
        referenced_file="agents/decisions/nonexistent.md",
        section="Test",
        keywords=frozenset({"test"}),
    )
    score = RelevanceScore(
        session_id="hook",
        entry_key=entry.key,
        score=0.5,
        is_relevant=True,
        matched_keywords={"test"},
    )

    result = resolve_entries([(entry, score)], tmp_path)

    assert len(result) == 0


def test_resolve_entries_skips_missing_section(tmp_path: Path) -> None:
    """resolve_entries skips entries with no matching section heading."""
    decision_file = tmp_path / "agents" / "decisions" / "test.md"
    decision_file.parent.mkdir(parents=True, exist_ok=True)
    decision_file.write_text(
        "# Test Decisions\n\n## Some Other Section\n\nContent here\n"
    )

    entry = IndexEntry(
        key="nonexistent section",
        description="test entry",
        referenced_file="agents/decisions/test.md",
        section="Test",
        keywords=frozenset({"test"}),
    )
    score = RelevanceScore(
        session_id="hook",
        entry_key=entry.key,
        score=0.5,
        is_relevant=True,
        matched_keywords={"test"},
    )

    result = resolve_entries([(entry, score)], tmp_path)

    assert len(result) == 0


def test_format_output_produces_context_and_system_parts() -> None:
    """format_output should produce dual-channel output with attribution."""
    entry_1 = IndexEntry(
        key="evaluating recall system effectiveness",
        description="test",
        referenced_file="agents/decisions/operational-practices.md",
        section="Test",
        keywords=frozenset({"recall", "effectiveness"}),
    )
    resolved_1 = ResolvedEntry(
        content="## When Evaluating Recall System Effectiveness\n\n"
        "Anti-pattern: Measuring without baseline",
        source_file=Path("agents/decisions/operational-practices.md"),
        entry=entry_1,
    )

    entry_2 = IndexEntry(
        key="too many rules in context",
        description="test",
        referenced_file="agents/decisions/prompt-structure-research.md",
        section="Test",
        keywords=frozenset({"rules", "context"}),
    )
    resolved_2 = ResolvedEntry(
        content="## When Too Many Rules In Context\n\n"
        "LLM adherence degrades with rule count",
        source_file=Path("agents/decisions/prompt-structure-research.md"),
        entry=entry_2,
    )

    result = format_output([resolved_1, resolved_2])

    assert isinstance(result, TopicMatchResult)
    assert "When Evaluating Recall System Effectiveness" in result.context
    assert "When Too Many Rules In Context" in result.context
    assert "Source: agents/decisions/operational-practices.md" in result.context
    assert result.system_message.startswith("topic")
    assert "evaluating recall system effectiveness" in result.system_message
    assert "too many rules in context" in result.system_message

    empty_result = format_output([])
    assert empty_result.context == ""
    assert empty_result.system_message == ""


def test_cache_stores_index_to_project_tmp(tmp_path: Path) -> None:
    """get_or_build_index should build and cache index to project tmp."""
    memory_index = tmp_path / "memory-index.md"
    memory_index.write_text(
        "# Memory Index\n\n"
        "## agents/decisions/operational-practices.md\n\n"
        "evaluating recall system effectiveness — 4.1% voluntary activation\n"
    )

    tmp_subdir = tmp_path / "tmp"
    tmp_subdir.mkdir(parents=True, exist_ok=True)

    entries, inverted_index = get_or_build_index(memory_index, tmp_path)

    assert isinstance(entries, list)
    assert len(entries) > 0
    assert all(isinstance(entry, IndexEntry) for entry in entries)

    assert isinstance(inverted_index, dict)
    assert all(isinstance(k, str) for k in inverted_index)

    cache_files = list(tmp_path.glob("tmp/topic-index-*.json"))
    assert len(cache_files) == 1

    cache_data = json.loads(cache_files[0].read_text())
    assert "entries" in cache_data
    assert "inverted_index" in cache_data
    assert "timestamp" in cache_data
    assert isinstance(cache_data["entries"], list)
    assert isinstance(cache_data["inverted_index"], dict)
    assert isinstance(cache_data["timestamp"], (int, float))


@pytest.mark.parametrize("case", ["cache_hit", "cache_invalidation"])
def test_cache_behavior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    """Cache hit avoids reparsing; mtime change invalidates cache."""
    memory_index = tmp_path / "memory-index.md"
    memory_index.write_text(
        "# Memory Index\n\n"
        "evaluating recall system effectiveness — 4.1% voluntary activation\n"
        "  agents/decisions/operational-practices.md\n"
    )

    tmp_subdir = tmp_path / "tmp"
    tmp_subdir.mkdir(parents=True, exist_ok=True)

    parse_call_count: list[int] = [0]

    def mock_parse_memory_index(path: Path) -> list[IndexEntry]:
        parse_call_count[0] += 1
        return parse_memory_index(path)

    monkeypatch.setattr(
        "claudeutils.recall.topic_matcher.parse_memory_index", mock_parse_memory_index
    )

    if case == "cache_hit":
        get_or_build_index(memory_index, tmp_path)
        assert parse_call_count[0] == 1

        get_or_build_index(memory_index, tmp_path)
        assert parse_call_count[0] == 1

    elif case == "cache_invalidation":
        get_or_build_index(memory_index, tmp_path)
        assert parse_call_count[0] == 1

        time.sleep(0.01)
        memory_index.write_text(
            "# Memory Index\n\n"
            "evaluating recall system effectiveness — 4.1% voluntary activation\n"
            "  agents/decisions/operational-practices.md\n"
            "\n"
        )
        os.utime(memory_index, None)

        get_or_build_index(memory_index, tmp_path)
        assert parse_call_count[0] == 2
