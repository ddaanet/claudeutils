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


def test_execute_rule_mode5_no_slug_derivation_prose() -> None:
    """Mode 5 section does not contain inline slug derivation implementation."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check that inline implementation details are NOT present
    assert "lowercase, hyphens" not in mode5_section, (
        "Mode 5 still contains inline slug derivation prose"
    )


def test_execute_rule_mode5_no_single_task_flow_steps() -> None:
    """Mode 5 section does not contain numbered single-task flow steps."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check that detailed single-task flow is NOT present
    assert (
        "**Single-task flow:**" not in mode5_section
        or "1. Derive slug" not in mode5_section
    ), "Mode 5 still contains detailed single-task flow implementation"


def test_execute_rule_mode5_no_parallel_group_flow_steps() -> None:
    """Mode 5 section does not contain numbered parallel group flow steps."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check that detailed parallel group flow is NOT present
    assert (
        "**Parallel group flow:**" not in mode5_section
        or "Identify the parallel group" not in mode5_section
    ), "Mode 5 still contains detailed parallel group flow implementation"


def test_execute_rule_mode5_no_focused_session_template() -> None:
    """Mode 5 section does not contain focused session.md template."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check that focused session template is NOT present
    assert "**Focused session.md format:**" not in mode5_section, (
        "Mode 5 still contains focused session.md template"
    )


def test_execute_rule_mode5_no_output_format_section() -> None:
    """Mode 5 section does not contain detailed output format section."""
    content = Path("agent-core/fragments/execute-rule.md").read_text()
    mode5_start = content.find("### MODE 5: WORKTREE SETUP")
    assert mode5_start != -1, "MODE 5 section not found"

    next_section = content.find("\n###", mode5_start + 1)
    if next_section == -1:
        mode5_section = content[mode5_start:]
    else:
        mode5_section = content[mode5_start:next_section]

    # Check that output format section is NOT present
    assert "**Output after setup:**" not in mode5_section, (
        "Mode 5 still contains output format section"
    )
