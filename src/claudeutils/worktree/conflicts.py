"""Session.md conflict resolution during worktree merges."""

import re
import subprocess

from claudeutils.worktree.git_utils import run_git


def _extract_task_block(task_name: str, content: str) -> str | None:
    """Extract task block including indented metadata lines."""
    task_line_pattern = rf"^- \[ \] \*\*{re.escape(task_name)}\*\*.*$"
    match = re.search(task_line_pattern, content, re.MULTILINE)
    if not match:
        return None

    # Extract task line and any indented continuation lines
    start = match.start()
    lines = content[start:].splitlines()
    task_block_lines = [lines[0]]

    # Collect indented continuation lines (metadata)
    for line in lines[1:]:
        if line and (line[0] == " " or line[0] == "\t"):
            task_block_lines.append(line)
        else:
            break

    return "\n".join(task_block_lines)


def _format_new_tasks_text(
    new_task_blocks: dict[str, str],
    *,
    has_next_heading: bool,
    ours_ends_with_newline: bool,
) -> str:
    """Format new tasks with spacing: blank line before next section, newline at EOF."""
    tasks_text = "\n".join(new_task_blocks.values())
    if not tasks_text:
        return ""

    # Ensure proper spacing: newline after tasks, blank line before next section
    if has_next_heading:
        return tasks_text + "\n\n"

    # At EOF - ensure newline before insertion if ours doesn't end with one
    if not ours_ends_with_newline:
        return "\n" + tasks_text + "\n"

    return tasks_text + "\n"


def resolve_session_conflict(ours: str, theirs: str, slug: str | None = None) -> str:
    """Resolve session.md merge: keep ours, append new tasks from theirs.

    If slug provided, extract matching task from theirs' Worktree Tasks section.
    All other sections unchanged from ours.
    """
    # Parse task names from both versions (Pending Tasks only, not Worktree)
    task_pattern = r"^- \[ \] \*\*(.+?)\*\*"
    ours_tasks = set(re.findall(task_pattern, ours, re.MULTILINE))
    theirs_tasks = set(re.findall(task_pattern, theirs, re.MULTILINE))

    # Find new tasks (in theirs but not in ours)
    new_task_names = theirs_tasks - ours_tasks

    # If slug provided, extract task from Worktree Tasks section
    if slug:
        worktree_pattern = rf"^- \[ \] \*\*(.+?)\*\*.*→ wt/{re.escape(slug)}"
        worktree_match = re.search(worktree_pattern, theirs, re.MULTILINE)
        if worktree_match:
            worktree_task_name = worktree_match.group(1)
            # Add to new tasks if not already extracted from Pending Tasks
            if worktree_task_name not in ours_tasks:
                new_task_names.add(worktree_task_name)

    if not new_task_names:
        # No new tasks, return ours as-is
        return ours

    # Extract full task blocks for each new task from theirs
    new_task_blocks = {}
    for task_name in new_task_names:
        block = _extract_task_block(task_name, theirs)
        if block:
            new_task_blocks[task_name] = block

    if not new_task_blocks:
        # All extractions failed, return ours as-is
        return ours

    # Find insertion point in ours: locate Pending Tasks section, find next heading
    pending_tasks_match = re.search(r"^## Pending Tasks\s*$", ours, re.MULTILINE)
    if not pending_tasks_match:
        # No Pending Tasks section found, return ours as-is
        return ours

    # Find the next section heading after Pending Tasks
    search_start = pending_tasks_match.end()
    next_heading_match = re.search(r"^## ", ours[search_start:], re.MULTILINE)

    insertion_point = (
        search_start + next_heading_match.start() if next_heading_match else len(ours)
    )

    # Build the new task block string with proper spacing
    new_tasks_text = _format_new_tasks_text(
        new_task_blocks,
        has_next_heading=bool(next_heading_match),
        ours_ends_with_newline=ours.endswith("\n"),
    )

    # Insert new tasks before the next heading (or at end)
    return ours[:insertion_point] + new_tasks_text + ours[insertion_point:]


def resolve_jobs_conflict(ours: str, theirs: str) -> str:
    """Resolve jobs.md merge: advance plan statuses to higher ordering.

    Status ordering: requirements → designed → outlined → planned → complete
    """
    status_ordering = ("requirements", "designed", "outlined", "planned", "complete")

    # Parse plan rows from both versions
    table_pattern = r"^\| ([^\|]+) \| ([^\|]+) \|"

    ours_matches = re.findall(table_pattern, ours, re.MULTILINE)
    theirs_matches = re.findall(table_pattern, theirs, re.MULTILINE)

    # Build plan -> status maps (strip whitespace)
    ours_status_map = {plan.strip(): status.strip() for plan, status in ours_matches}
    theirs_status_map = {
        plan.strip(): status.strip() for plan, status in theirs_matches
    }

    # Build updated status map by comparing ordering
    status_updates = {}
    for plan, theirs_status in theirs_status_map.items():
        if plan in ours_status_map:
            ours_status = ours_status_map[plan]

            # Get status indices
            if ours_status in status_ordering and theirs_status in status_ordering:
                ours_idx = status_ordering.index(ours_status)
                theirs_idx = status_ordering.index(theirs_status)

                # If theirs status is higher, mark for update
                if theirs_idx > ours_idx:
                    status_updates[plan] = theirs_status

    # If no updates needed, return ours unchanged
    if not status_updates:
        return ours

    # Reconstruct ours with updated statuses
    result = ours
    for plan, new_status in status_updates.items():
        # Find the table row for this plan and replace its status
        old_pattern = rf"^\| {re.escape(plan)} \| [^\|]+ \|"
        replacement = f"| {plan} | {new_status} |"
        result = re.sub(old_pattern, replacement, result, flags=re.MULTILINE)

    return result


def resolve_learnings_conflict(ours: str, theirs: str) -> str:
    """Resolve learnings.md merge: keep ours, append new entries from theirs.

    Entries identified by heading text.
    """
    # Split both versions on heading delimiter (^## ) with MULTILINE
    ours_split = re.split(r"^## ", ours, flags=re.MULTILINE)
    theirs_split = re.split(r"^## ", theirs, flags=re.MULTILINE)

    # First element is preamble (before first heading)
    ours_preamble = ours_split[0]
    ours_entries = ours_split[1:]

    theirs_entries = theirs_split[1:]

    # Extract heading text from each entry (first line of each section)
    def extract_heading(entry: str) -> str | None:
        """Extract first line as heading, None if empty."""
        if not entry:
            return None
        first_line = entry.split("\n", 1)[0]
        return first_line.strip() if first_line.strip() else None

    # Build set of ours headings for comparison
    ours_headings = set()
    for entry in ours_entries:
        heading = extract_heading(entry)
        if heading:
            ours_headings.add(heading)

    # Identify new entries in theirs (headings present in theirs but not ours)
    new_entries = []
    for entry in theirs_entries:
        heading = extract_heading(entry)
        if heading and heading not in ours_headings:
            new_entries.append(f"## {entry}")

    # Reconstruct result: preamble + ours entries + new entries
    result = ours_preamble
    for entry in ours_entries:
        result += f"## {entry}"

    for entry in new_entries:
        result += entry

    return result


def resolve_source_conflicts(
    conflict_files: list[str],
    *,
    exclude_patterns: list[str] | None = None,
    cwd: str | None = None,
) -> list[str]:
    """Resolve source code conflicts using take-ours strategy.

    Takes conflicted source files and applies `git checkout --ours`, then stages.
    Filters against exclude patterns (session context files). Returns list of
    successfully resolved files.

    Args:
        conflict_files: List of file paths with merge conflicts.
        exclude_patterns: File patterns to exclude from resolution (e.g.,
            ["agents/session.md", "agents/jobs.md"]).
        cwd: Working directory for git commands. Defaults to current directory.

    Returns:
        List of file paths that were successfully resolved.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    resolved = []

    for file_path in conflict_files:
        # Skip files matching exclude patterns
        if any(file_path == pattern for pattern in exclude_patterns):
            continue

        # Apply take-ours resolution
        try:
            if cwd:
                run_git(["-C", cwd, "checkout", "--ours", file_path], check=True)
                run_git(["-C", cwd, "add", file_path], check=True)
            else:
                run_git(["checkout", "--ours", file_path], check=True)
                run_git(["add", file_path], check=True)
            resolved.append(file_path)
        except subprocess.CalledProcessError as e:
            msg = f"Failed to resolve conflict in {file_path}"
            raise RuntimeError(msg) from e

    return resolved
