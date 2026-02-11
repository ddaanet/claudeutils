"""Tests for execute-rule.md Mode 5 refactoring to reference worktree skill."""

from pathlib import Path


def test_execute_rule_mode5_section_exists() -> None:
    """execute-rule.md contains Mode 5 section header."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    assert "### MODE 5: WORKTREE SETUP" in content


def test_execute_rule_mode5_documents_triggers() -> None:
    """Mode 5 section documents wt command triggers."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    # Find the next section (MODE with number) or end of document
    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check for trigger documentation
    assert "wt" in mode5_section, "Mode 5 section missing wt trigger"
    assert "Triggers:" in mode5_section, "Mode 5 section missing Triggers label"


def test_execute_rule_mode5_references_skill() -> None:
    """Mode 5 section references /worktree skill for implementation details."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    # Find the next section
    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check for skill reference
    assert "/worktree" in mode5_section or "SKILL.md" in mode5_section, (
        "Mode 5 section does not reference /worktree skill"
    )
