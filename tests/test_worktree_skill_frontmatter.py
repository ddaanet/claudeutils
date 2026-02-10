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


def test_worktree_skill_frontmatter_has_name() -> None:
    """YAML frontmatter includes 'name: worktree' field."""
    data = _parse_frontmatter()
    assert data.get("name") == "worktree"


def test_worktree_skill_frontmatter_has_description() -> None:
    """YAML frontmatter includes 'description' field as multi-line string."""
    data = _parse_frontmatter()
    assert "description" in data
    assert isinstance(data["description"], str)
    assert len(data["description"]) > 0


def test_worktree_skill_description_mentions_invocation_triggers() -> None:
    """Description mentions all required invocation triggers."""
    data = _parse_frontmatter()
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


def test_worktree_skill_frontmatter_has_allowed_tools() -> None:
    """YAML frontmatter includes 'allowed-tools' field as list."""
    data = _parse_frontmatter()
    assert "allowed-tools" in data
    assert isinstance(data["allowed-tools"], list)


def test_worktree_skill_allowed_tools_includes_required_tools() -> None:
    """Allowed-tools includes all required tools."""
    data = _parse_frontmatter()
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


def test_worktree_skill_frontmatter_has_user_invocable() -> None:
    """YAML frontmatter includes 'user-invocable: true' field."""
    data = _parse_frontmatter()
    assert "user-invocable" in data
    assert data["user-invocable"] is True


def test_worktree_skill_frontmatter_has_continuation() -> None:
    """YAML frontmatter includes 'continuation' field as dict."""
    data = _parse_frontmatter()
    assert "continuation" in data
    assert isinstance(data["continuation"], dict)


def test_worktree_skill_continuation_has_cooperative_mode() -> None:
    """Continuation dict includes 'cooperative: true' field."""
    data = _parse_frontmatter()
    continuation = data.get("continuation")
    assert isinstance(continuation, dict)
    assert "cooperative" in continuation
    assert continuation["cooperative"] is True


def test_worktree_skill_continuation_has_default_exit() -> None:
    """Continuation dict includes 'default-exit: []' (empty array)."""
    data = _parse_frontmatter()
    continuation = data.get("continuation")
    assert isinstance(continuation, dict)
    assert "default-exit" in continuation
    assert isinstance(continuation["default-exit"], list)
    assert len(continuation["default-exit"]) == 0
