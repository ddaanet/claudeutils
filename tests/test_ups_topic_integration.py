"""Integration tests for topic injection into UserPromptSubmit hook."""

from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from tests.ups_hook_helpers import call_hook


@pytest.fixture
def tmp_memory_index(tmp_path: Path) -> Path:
    """Create memory-index with fixture entries pointing to decision file."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Create decision file with test sections
    decision_file = agents_dir / "test-decisions.md"
    decision_file.write_text("""
# Test Decisions

## When testing hook integration

This is test decision content for hook integration testing. It contains detailed
information about how the hook should work with the topic detector.

## When recall system works

Details about how the recall system works and its components. This section has
specific implementation notes.
""")

    # Create memory-index referencing the decision file
    index_file = agents_dir / "memory-index.md"
    index_file.write_text("""
## agents/test-decisions.md

testing hook integration — decision about hook testing
recall system works — how recall system integrates
""")

    return index_file


def test_hook_topic_injection_produces_additional_context(
    tmp_path: Path, monkeypatch: MonkeyPatch, tmp_memory_index: Path
) -> None:
    """Topic detector hook integration test.

    Adds context and system message when keywords match.
    """
    # Setup
    tmp_dir = tmp_memory_index.parent.parent
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_dir))

    # Create tmp directory for cache
    tmp_cache_dir = tmp_dir / "tmp"
    tmp_cache_dir.mkdir(exist_ok=True)

    # Call hook with prompt containing keywords that match memory-index entries
    prompt = "how does the recall system work"
    result = call_hook(prompt)

    # Assertions
    assert result != {}, "Hook should produce output for matching keywords"
    assert "hookSpecificOutput" in result
    assert "additionalContext" in result["hookSpecificOutput"]

    additional_context = result["hookSpecificOutput"]["additionalContext"]

    # Should contain resolved decision content
    assert "recall system" in additional_context.lower()
    assert "implementation notes" in additional_context.lower()

    # systemMessage should contain topic marker and trigger info
    assert "systemMessage" in result
    system_message = result["systemMessage"]
    assert "topic" in system_message.lower()
    assert "recall" in system_message.lower()


def test_hook_topic_injection_end_to_end(
    tmp_path: Path, monkeypatch: MonkeyPatch, tmp_memory_index: Path
) -> None:
    """End-to-end: prompt with keywords match additionalContext with decision."""
    # Setup
    tmp_dir = tmp_memory_index.parent.parent
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_dir))

    # Create tmp directory for cache
    tmp_cache_dir = tmp_dir / "tmp"
    tmp_cache_dir.mkdir(exist_ok=True)

    # Call hook with prompt containing keywords that match memory-index entries
    prompt = "testing hook integration"
    result = call_hook(prompt)

    # Assertions
    assert result != {}, "Hook should produce output for matching keywords"
    assert "hookSpecificOutput" in result
    assert "additionalContext" in result["hookSpecificOutput"]

    additional_context = result["hookSpecificOutput"]["additionalContext"]

    # Should contain resolved decision content
    assert (
        "test decision content" in additional_context
        or "hook" in additional_context.lower()
    )

    # systemMessage should contain topic marker
    assert "systemMessage" in result
    system_message = result["systemMessage"]
    assert "topic" in system_message.lower()
