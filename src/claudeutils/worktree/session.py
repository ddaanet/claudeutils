"""Session.md parsing and editing utilities."""

import re
from dataclasses import dataclass


@dataclass
class TaskBlock:
    """Task block from session.md."""

    name: str  # Task name extracted from markdown
    lines: list[str]  # All lines (task line + continuation lines)
    section: str  # Section name: "Pending Tasks" or "Worktree Tasks"


def extract_task_blocks(content: str, section: str | None = None) -> list[TaskBlock]:
    """Extract task blocks from session.md content.

    Args:
        content: Session.md file content
        section: Optional section name filter ("Pending Tasks", "Worktree Tasks")

    Returns:
        List of TaskBlock instances
    """
    lines = content.split("\n")
    blocks = []
    current_section = None
    task_pattern = re.compile(r"^- \[[ x>]\] \*\*(.+?)\*\*")

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()
            i += 1
            continue

        # Match task lines
        match = task_pattern.match(line)
        if match:
            task_name = match.group(1)
            task_lines = [line]

            # Collect continuation lines (indented lines following the task)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                # Stop at next task, next section, or blank line
                if (
                    task_pattern.match(next_line)
                    or next_line.startswith("## ")
                    or not next_line.strip()
                ):
                    break
                # Stop at non-indented content line
                if next_line[0].isspace():
                    task_lines.append(next_line)
                    j += 1
                else:
                    break

            # Filter by section if requested
            if section is None or current_section == section:
                blocks.append(
                    TaskBlock(
                        name=task_name,
                        lines=task_lines,
                        section=current_section or "",
                    )
                )

            i = j
            continue

        i += 1

    return blocks


def find_section_bounds(content: str, header: str) -> tuple[int, int] | None:
    """Find line bounds for a section header.

    Args:
        content: Session.md file content
        header: Section header name (without "## " prefix)

    Returns:
        (start_line, end_line) tuple or None if not found
        start_line: Index of "## header" line
        end_line: Index of line before next "## " or EOF
    """
    lines = content.split("\n")
    start_idx = None

    for i, line in enumerate(lines):
        if line == f"## {header}":
            start_idx = i
            break

    if start_idx is None:
        return None

    # Find end: next "## " header or EOF
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end_idx = i
            break

    return (start_idx, end_idx)
