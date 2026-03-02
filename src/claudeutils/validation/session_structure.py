"""Validate session.md structural conventions.

Checks:
- No task appears in both In-tree Tasks and Worktree Tasks
- Reference Files entries point to existing versioned files
"""

import re
from pathlib import Path

TASK_PATTERN = re.compile(r"^- \[.\] \*\*(.+?)\*\*")
SECTION_PATTERN = re.compile(r"^## (.+)$")
REF_FILE_PATTERN = re.compile(r"^- `([^`]+)`")

ALLOWED_SECTIONS = [
    "Completed This Session",
    "In-tree Tasks",
    "Pending Tasks",
    "Worktree Tasks",
    "Blockers / Gotchas",
    "Reference Files",
    "Next Steps",
]

SECTION_ORDER = [
    "Completed This Session",
    "In-tree Tasks",
    "Pending Tasks",
    "Worktree Tasks",
    "Blockers / Gotchas",
    "Reference Files",
    "Next Steps",
]


def parse_sections(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    """Parse session.md into named sections.

    Args:
        lines: File content as list of lines.

    Returns:
        Dict mapping section name to list of (line_number, line_text) pairs.
    """
    sections: dict[str, list[tuple[int, str]]] = {}
    current_section = ""
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m = SECTION_PATTERN.match(stripped)
        if m:
            current_section = m.group(1)
            sections.setdefault(current_section, [])
            continue
        if current_section:
            sections.setdefault(current_section, []).append((i, stripped))
    return sections


def extract_section_tasks(
    section_lines: list[tuple[int, str]],
) -> list[tuple[int, str]]:
    """Extract task names from section lines.

    Args:
        section_lines: List of (line_number, line_text) pairs from a section.

    Returns:
        List of (line_number, task_name) pairs.
    """
    tasks = []
    for lineno, line in section_lines:
        m = TASK_PATTERN.match(line)
        if m:
            tasks.append((lineno, m.group(1)))
    return tasks


def check_cross_section_uniqueness(
    pending_tasks: list[tuple[int, str]],
    worktree_tasks: list[tuple[int, str]],
) -> list[str]:
    """Check no task appears in both In-tree and Worktree sections.

    Args:
        pending_tasks: Tasks from In-tree Tasks section.
        worktree_tasks: Tasks from Worktree Tasks section.

    Returns:
        List of error strings.
    """
    errors = []
    pending_names = {name.lower(): (lineno, name) for lineno, name in pending_tasks}
    for lineno, name in worktree_tasks:
        key = name.lower()
        if key in pending_names:
            p_lineno, _ = pending_names[key]
            errors.append(
                f"  line {lineno}: task in both In-tree (line {p_lineno}) "
                f"and Worktree: **{name}**"
            )
    return errors


def check_reference_files(
    section_lines: list[tuple[int, str]], root: Path
) -> list[str]:
    """Verify Reference Files entries point to existing files.

    Args:
        section_lines: Lines from Reference Files section.
        root: Project root directory.

    Returns:
        List of error strings.
    """
    errors = []
    for lineno, line in section_lines:
        m = REF_FILE_PATTERN.match(line)
        if m:
            ref_path = m.group(1)
            if not (root / ref_path).exists():
                errors.append(f"  line {lineno}: reference file not found: {ref_path}")
    return errors


def check_section_schema(lines: list[str]) -> list[str]:
    """Validate that session.md contains only allowed sections in correct order.

    Args:
        lines: File content as list of lines.

    Returns:
        List of error strings.
    """
    errors = []
    seen_sections = []
    seen_names = set()

    for i, line in enumerate(lines, 1):
        stripped = line.rstrip()
        m = SECTION_PATTERN.match(stripped)
        if not m:
            continue

        section_name = m.group(1)

        if section_name not in ALLOWED_SECTIONS:
            errors.append(f"  line {i}: unrecognized section: {section_name}")
            continue

        if section_name in seen_names:
            errors.append(f"  line {i}: duplicate section: {section_name}")
            continue

        seen_names.add(section_name)
        seen_sections.append((i, section_name))

    for i, (lineno, name) in enumerate(seen_sections):
        if i == 0:
            continue

        prev_name = seen_sections[i - 1][1]
        prev_order = SECTION_ORDER.index(prev_name)
        curr_order = SECTION_ORDER.index(name)

        if curr_order < prev_order:
            errors.append(
                f"  line {lineno}: section out of order: {name} "
                f"appears before {prev_name}"
            )

    return errors


def validate(session_path: str, root: Path) -> list[str]:
    """Validate session.md structure.

    Args:
        session_path: Path to session file (relative to root).
        root: Project root directory.

    Returns:
        List of error strings. Empty if no errors.
    """
    full_path = root / session_path
    if not full_path.exists():
        return []

    with full_path.open() as f:
        lines = f.readlines()

    errors = []

    # Section schema validation
    errors.extend(check_section_schema(lines))

    sections = parse_sections(lines)

    # Cross-section uniqueness
    pending = extract_section_tasks(sections.get("In-tree Tasks", []))
    worktree = extract_section_tasks(sections.get("Worktree Tasks", []))
    errors.extend(check_cross_section_uniqueness(pending, worktree))

    # Reference Files existence
    if "Reference Files" in sections:
        errors.extend(check_reference_files(sections["Reference Files"], root))

    return errors
