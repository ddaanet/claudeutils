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

    # New task should include full metadata with proper indentation
    assert "  - Plan: feature-z" in result
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


def test_resolve_session_conflict_no_new_tasks_returns_ours_unchanged() -> None:
    """When theirs has no new tasks, return ours unchanged."""
    ours = """# Session: Base

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Task B** — `/plan-adhoc` | opus

## Blockers / Gotchas

None.
"""

    theirs = """# Session: Base

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Task B** — `/plan-adhoc` | opus

## Blockers / Gotchas

Updated blockers.
"""

    result = resolve_session_conflict(ours, theirs)

    # Should return ours exactly (no task extraction needed)
    assert result == ours


def test_resolve_session_conflict_handles_empty_pending_tasks() -> None:
    """Extract new tasks when ours has empty Pending Tasks section."""
    ours = """# Session: Base

## Pending Tasks

## Blockers / Gotchas

None.
"""

    theirs = """# Session: Base

## Pending Tasks

- [ ] **New task** — `/design` | sonnet

## Blockers / Gotchas

None.
"""

    result = resolve_session_conflict(ours, theirs)

    # New task should be inserted
    assert "**New task**" in result
    assert "`/design`" in result


def test_resolve_session_conflict_ignores_duplicate_task_names_outside_pending() -> (
    None
):
    """Task name appearing in other sections shouldn't affect extraction."""
    ours = """# Session: Base

## Pending Tasks

- [ ] **Fix bug X** — `/design` | sonnet

## Blockers / Gotchas

Need to fix **Implement feature Y** before proceeding.
"""

    theirs = """# Session: Base

## Pending Tasks

- [ ] **Fix bug X** — `/design` | sonnet
- [ ] **Implement feature Y** — `/plan-adhoc` | sonnet
  - Plan: feature-y

## Blockers / Gotchas

Need to fix **Implement feature Y** before proceeding.
"""

    result = resolve_session_conflict(ours, theirs)

    # Should extract the Pending Tasks version, not the Blockers mention
    assert "- [ ] **Implement feature Y**" in result
    assert "  - Plan: feature-y" in result
    # Blockers section unchanged from ours
    assert result.count("**Implement feature Y**") == 2  # One in tasks, one in blockers
