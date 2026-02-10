"""Tests for session.md conflict resolution."""

from claudeutils.worktree.conflicts import (
    resolve_jobs_conflict,
    resolve_learnings_conflict,
    resolve_session_conflict,
)


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


def test_resolve_session_conflict_extracts_from_worktree_when_slug_matches() -> None:
    """Worktree task extraction when task in both Pending and Worktree sections.

    Scenario matches design (outline.md): main side has task in Pending Tasks,
    worktree side has same task in both Pending Tasks and Worktree Tasks. When
    slug provided, extract from Worktree Tasks section.
    """
    ours = """# Session: Base

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet
- [ ] **Execute plugin migration** — `/plan-adhoc` | sonnet

## Blockers / Gotchas

None.
"""

    theirs = """# Session: Base

## Pending Tasks

- [ ] **Task A** — `/design` | sonnet

## Blockers / Gotchas

None.

## Worktree Tasks

- [ ] **Execute plugin migration** → wt/plugin-migration — `/plan-adhoc` | sonnet
"""

    result = resolve_session_conflict(ours, theirs, slug="plugin-migration")

    # Result should have no Worktree Tasks section (ours-as-base excludes it)
    assert "## Worktree Tasks" not in result

    # Task should be in Pending Tasks
    assert "- [ ] **Execute plugin migration**" in result
    assert "`/plan-adhoc`" in result

    # No reference to wt/plugin-migration marker should remain
    assert "wt/plugin-migration" not in result
    assert "→ wt/" not in result


def test_resolve_learnings_conflict_appends_new_entries() -> None:
    """Append new learning entries from theirs to ours."""
    ours = """# Learnings

Institutional knowledge accumulated.

## Tool batching unsolved

- Documentation doesn't reliably change behavior
- Cost-benefit unclear

## Scan triggers unnecessary tools

- Anti-pattern: "Scan X.md" where X is @-referenced
- Correct pattern: "Check loaded X context"

## Structural header dot syntax

- Anti-pattern: `.## Title`
- Correct pattern: `## .Title`
"""

    theirs = """# Learnings

Institutional knowledge accumulated.

## Tool batching unsolved

- Documentation doesn't reliably change behavior
- Cost-benefit unclear

## Scan triggers unnecessary tools

- Anti-pattern: "Scan X.md" where X is @-referenced
- Correct pattern: "Check loaded X context"

## Structural header dot syntax

- Anti-pattern: `.## Title`
- Correct pattern: `## .Title`

## Vet-fix-agent confabulation from design docs

- Anti-pattern: Give vet-fix-agent full design.md during phase review
- Correct pattern: Precommit-first, explicit scope prevents confabulation
"""

    result = resolve_learnings_conflict(ours, theirs)

    # Result should contain all four learning entries
    assert "## Tool batching unsolved" in result
    assert "## Scan triggers unnecessary tools" in result
    assert "## Structural header dot syntax" in result
    assert "## Vet-fix-agent confabulation from design docs" in result

    # New entry should be appended at end (after "Structural header dot syntax")
    structural_idx = result.find("## Structural header dot syntax")
    confab_idx = result.find("## Vet-fix-agent confabulation from design docs")
    assert structural_idx < confab_idx

    # All entries should preserve exact content (multi-paragraph, code blocks, etc)
    assert "- Documentation doesn't reliably change behavior" in result
    assert "- Cost-benefit unclear" in result
    assert "- Anti-pattern: `.## Title`" in result
    assert "- Correct pattern: `## .Title`" in result
    assert (
        "- Anti-pattern: Give vet-fix-agent full design.md during phase review"
        in result
    )

    # No duplication of shared entries
    assert result.count("## Tool batching unsolved") == 1
    assert result.count("## Scan triggers unnecessary tools") == 1
    assert result.count("## Structural header dot syntax") == 1


def test_resolve_jobs_conflict_advances_status() -> None:
    """Resolve jobs.md conflict by advancing status to higher ordering."""
    ours = """# Jobs

Plan lifecycle tracking.

| Plan | Status | Notes |
|------|--------|-------|
| continuation-prepend | requirements | Problem statement only |
| worktree-skill | designed | In progress |
| plugin-migration | planned | Runbook assembled |
"""

    theirs = """# Jobs

Plan lifecycle tracking.

| Plan | Status | Notes |
|------|--------|-------|
| continuation-prepend | requirements | Problem statement only |
| worktree-skill | planned | Status updated |
| plugin-migration | planned | Runbook assembled |
"""

    result = resolve_jobs_conflict(ours, theirs)

    # worktree-skill should advance from "designed" to "planned"
    assert "| worktree-skill | planned |" in result
    # plugin-migration should remain "planned" (no change)
    assert "| plugin-migration | planned |" in result
    # continuation-prepend should remain "requirements"
    assert "| continuation-prepend | requirements |" in result


def test_resolve_jobs_conflict_outlined_status_ordering() -> None:
    """Verify 'outlined' status falls between 'designed' and 'planned'."""
    ours = """# Jobs

| Plan | Status | Notes |
|------|--------|-------|
| feature-a | designed | Initial design |
"""

    theirs = """# Jobs

| Plan | Status | Notes |
|------|--------|-------|
| feature-a | outlined | Outline complete |
"""

    result = resolve_jobs_conflict(ours, theirs)

    # feature-a should advance from "designed" to "outlined"
    assert "| feature-a | outlined |" in result
