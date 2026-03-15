"""Tests for session status rendering (Phase 3)."""

from __future__ import annotations

from claudeutils.session.status.render import render_next
from claudeutils.validation.task_parsing import ParsedTask


def _task(name: str, **kwargs: object) -> ParsedTask:
    """Build a ParsedTask for testing with sensible defaults."""
    defaults: dict[str, object] = {
        "checkbox": " ",
        "command": "/runbook plans/test/r.md",
        "model": "sonnet",
        "worktree_marker": None,
        "restart": False,
    }
    defaults.update(kwargs)
    return ParsedTask(
        name=name,
        checkbox=str(defaults["checkbox"]),
        full_line=f"- [{defaults['checkbox']}] **{name}**",
        command=defaults.get("command"),  # type: ignore[arg-type]
        model=defaults.get("model"),  # type: ignore[arg-type]
        worktree_marker=defaults.get("worktree_marker"),  # type: ignore[arg-type]
        restart=bool(defaults["restart"]),
    )


# --- Cycle 3.1: render_next ---


def test_render_next_task() -> None:
    """First pending task without worktree marker renders as Next block."""
    tasks = [
        _task("Build parser", command="/runbook plans/parser/design.md"),
    ]
    result = render_next(tasks)
    assert "Next: Build parser" in result
    assert "`/runbook plans/parser/design.md`" in result
    assert "Model: sonnet" in result
    assert "Restart: no" in result


def test_render_next_skips_worktree_markers() -> None:
    """Tasks with worktree markers are skipped; first plain pending wins."""
    tasks = [
        _task("Slugged", worktree_marker="my-slug"),
        _task("WT marked", worktree_marker="wt"),
        _task("Plain pending", command="/design plans/p/b.md"),
    ]
    result = render_next(tasks)
    assert "Next: Plain pending" in result
    assert "Slugged" not in result
    assert "WT marked" not in result


def test_render_next_no_pending() -> None:
    """Empty task list returns empty string."""
    assert render_next([]) == ""


def test_render_next_skips_completed() -> None:
    """Tasks with checkbox x are skipped."""
    tasks = [_task("Done", checkbox="x")]
    assert render_next(tasks) == ""


def test_render_next_skips_blocked() -> None:
    """Tasks with blocked checkbox are skipped."""
    tasks = [_task("Blocked", checkbox="!")]
    assert render_next(tasks) == ""


def test_render_next_skips_failed() -> None:
    """Tasks with checkbox † are skipped."""
    tasks = [_task("Failed", checkbox="†")]
    assert render_next(tasks) == ""


def test_render_next_skips_canceled() -> None:
    """Tasks with checkbox - are skipped."""
    tasks = [_task("Canceled", checkbox="-")]
    assert render_next(tasks) == ""


def test_render_next_restart_yes() -> None:
    """Restart flag renders as 'yes'."""
    tasks = [_task("Heavy", restart=True, model="opus")]
    result = render_next(tasks)
    assert "Restart: yes" in result
    assert "Model: opus" in result


def test_render_next_model_defaults() -> None:
    """None model defaults to 'sonnet' in output."""
    tasks = [_task("No model", model=None)]
    result = render_next(tasks)
    assert "Model: sonnet" in result
