"""Session.md conflict resolution during worktree merges."""

import re


def resolve_session_conflict(ours: str, theirs: str) -> str:
    """Resolve session.md merge conflict by extracting new tasks from theirs.

    Preserves all tasks from ours, adds new tasks found only in theirs.
    All other sections remain unchanged from ours.

    Args:
        ours: The base session.md version (keep as base).
        theirs: The incoming session.md version (extract new tasks from).

    Returns:
        Merged session.md with new tasks appended to Pending Tasks section.
    """
    # Parse task names from both versions
    task_pattern = r"^- \[ \] \*\*(.+?)\*\*"
    ours_tasks = set(re.findall(task_pattern, ours, re.MULTILINE))
    theirs_tasks = set(re.findall(task_pattern, theirs, re.MULTILINE))

    # Find new tasks (in theirs but not in ours)
    new_task_names = theirs_tasks - ours_tasks

    if not new_task_names:
        # No new tasks, return ours as-is
        return ours

    # Extract full task blocks for each new task from theirs
    new_task_blocks = {}
    for task_name in new_task_names:
        # Find the task line
        task_line_pattern = rf"^- \[ \] \*\*{re.escape(task_name)}\*\*.*$"
        match = re.search(task_line_pattern, theirs, re.MULTILINE)
        if not match:
            continue

        # Extract task line and any indented continuation lines
        start = match.start()
        lines = theirs[start:].split("\n")
        task_block_lines = [lines[0]]

        # Collect indented continuation lines (metadata)
        for line in lines[1:]:
            if line and (line[0] == " " or line[0] == "\t"):
                task_block_lines.append(line)
            else:
                break

        new_task_blocks[task_name] = "\n".join(task_block_lines)

    # Find insertion point in ours: locate Pending Tasks section, find next heading
    pending_tasks_match = re.search(r"^## Pending Tasks\s*$", ours, re.MULTILINE)
    if not pending_tasks_match:
        # No Pending Tasks section found, return ours as-is
        return ours

    # Find the next section heading after Pending Tasks
    search_start = pending_tasks_match.end()
    next_heading_match = re.search(r"^## ", ours[search_start:], re.MULTILINE)

    if next_heading_match:
        insertion_point = search_start + next_heading_match.start()
    else:
        # No next heading, insert at end of ours
        insertion_point = len(ours)

    # Build the new task block string
    new_tasks_text = "\n".join(new_task_blocks.values())
    if new_tasks_text:
        new_tasks_text = new_tasks_text + "\n"

    # Insert new tasks before the next heading (or at end)
    return ours[:insertion_point] + new_tasks_text + ours[insertion_point:]
