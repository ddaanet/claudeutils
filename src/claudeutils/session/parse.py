"""Session.md parser — shared by handoff and status subcommands (Phase 2).

Composes existing functions from worktree/session.py and
validation/task_parsing.py rather than reimplementing parsing logic.
"""

from __future__ import annotations

import re

from claudeutils.validation.task_parsing import ParsedTask, parse_task_line
from claudeutils.worktree.session import (
    _extract_plan_from_block,
    extract_task_blocks,
    find_section_bounds,
)

__all__ = ["ParsedTask", "parse_completed_section", "parse_status_line", "parse_tasks"]


def parse_status_line(content: str) -> str | None:
    """Extract status text between ``# Session Handoff:`` and first ``## ``.

    Returns None if no ``# Session Handoff:`` heading found.
    """
    lines = content.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if line.startswith("# Session Handoff:"):
            start_idx = i + 1
            break
    if start_idx is None:
        return None

    collected: list[str] = []
    for line in lines[start_idx:]:
        if line.startswith("## "):
            break
        collected.append(line)

    text = "\n".join(collected).strip()
    return text if text else None


def parse_completed_section(content: str) -> list[str]:
    """Extract lines under ``## Completed This Session``.

    Returns list of non-empty lines. Empty list if section missing or empty.
    """
    bounds = find_section_bounds(content, "Completed This Session")
    if bounds is None:
        return []

    lines = content.split("\n")
    section_lines = lines[bounds[0] + 1 : bounds[1]]
    return [line for line in section_lines if line.strip()]


def parse_tasks(content: str, section: str = "In-tree Tasks") -> list[ParsedTask]:
    """Parse task items from a named section of session.md.

    Composes ``extract_task_blocks`` → ``parse_task_line`` → extend with ``plan_dir``.
    Section name parameter makes in-tree and worktree parsing identical.

    Returns list of ParsedTask with ``plan_dir`` populated from continuation lines.
    """
    blocks = extract_task_blocks(content, section=section)
    tasks: list[ParsedTask] = []

    for block in blocks:
        parsed = parse_task_line(block.lines[0])
        if parsed is None:
            continue

        # Extend with plan_dir from continuation lines
        plan_dir = _extract_plan_from_block(block)
        # Strip status suffix from plan_dir (e.g., "parser" not "parser |")
        if plan_dir:
            plan_dir = re.sub(r"\s*\|.*$", "", plan_dir)
        parsed.plan_dir = plan_dir

        tasks.append(parsed)

    return tasks
