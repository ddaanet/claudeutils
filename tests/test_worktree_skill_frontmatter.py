"""Tests for worktree skill YAML frontmatter validation."""

from pathlib import Path

import yaml


def _get_frontmatter() -> str:
    """Get YAML frontmatter from worktree skill file."""
    content = Path("agent-core/skills/worktree/SKILL.md").read_text()
    return content.split("---")[1]


def _parse_frontmatter() -> dict[str, object]:
    """Parse YAML frontmatter from worktree skill file."""
    frontmatter = _get_frontmatter()
    data = yaml.safe_load(frontmatter)
    assert isinstance(data, dict)
    return data


def test_worktree_skill_basic_schema() -> None:
    """YAML frontmatter includes required fields with correct types."""
    data = _parse_frontmatter()

    # Check name field
    assert data.get("name") == "worktree"

    # Check description field
    assert "description" in data
    assert isinstance(data["description"], str)
    assert len(data["description"]) > 0

    # Check allowed-tools field
    assert "allowed-tools" in data
    assert isinstance(data["allowed-tools"], list)

    # Check user-invocable field
    assert "user-invocable" in data
    assert data["user-invocable"] is True

    # Check continuation field
    assert "continuation" in data
    assert isinstance(data["continuation"], dict)


def test_worktree_skill_content_validation() -> None:
    """Description and allowed-tools include required content."""
    data = _parse_frontmatter()

    # Check description mentions invocation triggers
    description = data.get("description")
    assert isinstance(description, str)
    required_triggers = [
        "create a worktree",
        "set up parallel work",
        "merge a worktree",
        "branch off a task",
        "wt",
    ]
    for trigger in required_triggers:
        assert trigger in description, f"Description missing trigger: {trigger}"

    # Check allowed-tools includes required tools
    tools = data.get("allowed-tools")
    assert isinstance(tools, list)
    tools_str = " ".join(str(t) for t in tools)
    required_patterns = [
        "Read",
        "Write",
        "Edit",
        "claudeutils _worktree:*",
        "just precommit",
        "git status:*",
        "git worktree:*",
        "Skill",
    ]
    for pattern in required_patterns:
        assert pattern in tools_str, f"allowed-tools missing: {pattern}"


def test_worktree_skill_continuation_structure() -> None:
    """Continuation dict includes cooperative mode and default-exit."""
    data = _parse_frontmatter()
    continuation = data.get("continuation")
    assert isinstance(continuation, dict)

    # Check cooperative field
    assert "cooperative" in continuation
    assert continuation["cooperative"] is True

    # Check default-exit field
    assert "default-exit" in continuation
    assert isinstance(continuation["default-exit"], list)
    assert len(continuation["default-exit"]) == 0
