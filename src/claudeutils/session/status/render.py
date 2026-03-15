"""Render STATUS output sections from parsed session data."""

from __future__ import annotations

from claudeutils.validation.task_parsing import ParsedTask


def render_next(tasks: list[ParsedTask]) -> str:
    """Render the Next: block for the first eligible pending task.

    Eligible: checkbox ``" "``, no worktree_marker.
    Skips completed (x), blocked (!), failed (†), canceled (-), and
    tasks with worktree markers.

    Returns empty string if no eligible task found.
    """
    for task in tasks:
        if task.checkbox != " ":
            continue
        if task.worktree_marker is not None:
            continue

        model = task.model or "sonnet"
        restart = "yes" if task.restart else "no"
        command = task.command or ""

        return (
            f"Next: {task.name}\n  `{command}`\n  Model: {model} | Restart: {restart}"
        )

    return ""
