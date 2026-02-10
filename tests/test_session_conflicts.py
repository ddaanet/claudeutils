"""Tests for session.md conflict resolution."""

from claudeutils.worktree.conflicts import resolve_session_conflict


def test_resolve_session_conflict_extracts_new_tasks() -> None:
    """Extract new tasks from theirs side before keep-ours resolution."""
    ours = """# Session: Base

**Status:** Test session.

## Pending Tasks

- [ ] **Implement feature X** — `/design` | sonnet
  - Plan: feature-x
- [ ] **Design feature Y** — `/plan-adhoc` | opus

## Blockers / Gotchas

None.

## Reference Files

- test.md
"""

    theirs = """# Session: Base

**Status:** Test session.

## Pending Tasks

- [ ] **Implement feature X** — `/design` | sonnet
  - Plan: feature-x
- [ ] **Design feature Y** — `/plan-adhoc` | opus
- [ ] **Plan feature Z TDD runbook** — `/plan-tdd` | sonnet
  - Plan: feature-z

## Blockers / Gotchas

None.

## Reference Files

- test.md
"""

    result = resolve_session_conflict(ours, theirs)

    # All three tasks should be present
    assert "**Implement feature X**" in result
    assert "**Design feature Y**" in result
    assert "**Plan feature Z TDD runbook**" in result

    # New task should include full metadata
    assert "Plan: feature-z" in result
    assert "`/plan-tdd`" in result

    # Order: ours tasks first, then new theirs tasks
    x_idx = result.find("**Implement feature X**")
    y_idx = result.find("**Design feature Y**")
    z_idx = result.find("**Plan feature Z TDD runbook**")
    assert x_idx < y_idx < z_idx

    # Other sections unchanged
    assert "## Blockers / Gotchas" in result
    assert "## Reference Files" in result
    assert "- test.md" in result
