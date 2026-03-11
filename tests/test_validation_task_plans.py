"""Tests for task plan reference validation."""

from pathlib import Path

from claudeutils.validation.task_plans import validate


def test_valid_plan_passes_invalid_fails(tmp_path: Path) -> None:
    """Valid plan references pass; missing plan references fail."""
    # Setup: Create session.md at agents/session.md under tmp_path
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    # Create a valid plan directory with requirements.md
    valid_plan_dir = tmp_path / "plans" / "valid-plan"
    valid_plan_dir.mkdir(parents=True)
    (valid_plan_dir / "requirements.md").write_text("# Valid Plan\n")

    # Create session.md with two tasks: one with valid plan ref, one without
    session_content = """# Session Handoff: 2026-03-11

## In-tree Tasks

- [ ] **Good task** — `\x60/design plans/valid-plan/requirements.md\x60 | sonnet
- [ ] **Bad task** — `\x60/design\x60 | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    # Call validate
    errors = validate("agents/session.md", tmp_path)

    # Should have exactly 1 error mentioning "Bad task"
    assert len(errors) == 1
    assert "Bad task" in errors[0]


def test_terminal_tasks_exempt(tmp_path: Path) -> None:
    """Terminal tasks are exempt from plan reference validation."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    session_content = """# Session Handoff: 2026-03-11

## In-tree Tasks

- [x] **Done task** — `\x60/design\x60 | sonnet
- [-] **Canceled task** — `\x60/design\x60 | sonnet
- [†] **Failed task** — `\x60/design\x60 | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    errors = validate("agents/session.md", tmp_path)

    assert errors == []


def test_slug_only_command(tmp_path: Path) -> None:
    """Slug-only commands like /orchestrate my-plan are extracted/validated."""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir(parents=True)

    # Create a valid plan directory with requirements.md
    plan_dir = tmp_path / "plans" / "my-plan"
    plan_dir.mkdir(parents=True)
    (plan_dir / "requirements.md").write_text("# My Plan\n")

    session_content = """# Session Handoff: 2026-03-11

## Worktree Tasks

- [ ] **Slug task** — `\x60/orchestrate my-plan\x60 | sonnet
"""
    (agents_dir / "session.md").write_text(session_content)

    errors = validate("agents/session.md", tmp_path)

    assert errors == []
