"""Tests for execute-rule.md Mode 5 refactoring to reference worktree skill."""

from pathlib import Path


def _get_mode5_section() -> str:
    """Extract Mode 5 section from execute-rule.md.

    Returns the content between "### MODE 5: WORKTREE SETUP" and the next
    section header (or end of file).
    """
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    if mode5_start == -1:
        return ""

    # Find the next section (another ### header) or end of document
    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        return content[mode5_start:]
    return content[mode5_start:next_section]


def test_execute_rule_mode5_section_exists() -> None:
    """execute-rule.md contains Mode 5 section header."""
    section = _get_mode5_section()
    assert section, "MODE 5 section not found"
    assert "### MODE 5: WORKTREE SETUP" in section


def test_execute_rule_mode5_documents_triggers() -> None:
    """Mode 5 section documents wt command triggers."""
    section = _get_mode5_section()
    assert section, "MODE 5 section not found"

    # Check for trigger documentation
    assert "wt" in section, "Mode 5 section missing wt trigger"
    assert "Triggers:" in section, "Mode 5 section missing Triggers label"


def test_execute_rule_mode5_references_skill() -> None:
    """Mode 5 section references /worktree skill for implementation details."""
    section = _get_mode5_section()
    assert section, "MODE 5 section not found"

    # Check for skill reference
    assert "/worktree" in section or "SKILL.md" in section, (
        "Mode 5 section does not reference /worktree skill"
    )
