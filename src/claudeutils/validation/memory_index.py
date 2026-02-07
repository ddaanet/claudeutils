"""Validate memory-index.md entries against semantic headers in indexed files.

Checks:
- All semantic headers (##+ not starting with .) have index entries
- All index entries match at least one semantic header
- No duplicate index entries
- Document intro content (between # and first ##) is exempt
- Entries are in correct file section (autofix by default)
- Entries are in file order within sections (autofix by default)
- Word count 8-15 for entries (preamble lines exempt)
- Entries pointing to structural sections are removed (autofix)
"""

import re
import sys
from pathlib import Path

from .memory_index_helpers import (
    autofix_index,
    check_duplicate_entries,
    check_em_dash_and_word_count,
    check_entry_placement,
    check_entry_sorting,
    check_orphan_entries,
    check_structural_entries,
    collect_semantic_headers,
    collect_structural_headers,
)

# Section header that specifies a file path
FILE_SECTION = re.compile(r"^## (agents/decisions/\S+\.md)$")


def extract_index_entries(
    index_path: Path | str, root: Path
) -> dict[str, tuple[int, str, str]]:
    """Extract index entries from memory-index.md.

    Index entries are bare lines (not headers, not bold, not list markers)
    with em-dash separator: "Key — description"

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.

    Returns:
        Dict: lowercase key → (line_number, full_entry, section_name)
        When duplicates exist, only the last occurrence is stored.
    """
    entries: dict[str, tuple[int, str, str]] = {}

    try:
        if isinstance(index_path, str):
            full_path = root / index_path
        else:
            full_path = root / index_path
        lines = full_path.read_text().splitlines()
    except FileNotFoundError:
        return entries

    current_section: str | None = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Handle headers - track section state
        if stripped.startswith("##") and not stripped.startswith("###"):
            # Extract section name (part after "## ")
            current_section = stripped[3:] if stripped.startswith("## ") else None
            continue

        # Skip H1 headers
        if stripped.startswith("# "):
            continue

        # Skip empty lines without changing section state
        if not stripped:
            continue

        # Skip bold directives (** at start)
        if stripped.startswith("**"):
            continue

        # Skip list markers (old format, shouldn't exist but handle gracefully)
        if stripped.startswith("- "):
            continue

        # In a section, non-header, non-bold, non-empty = index entry
        if current_section:
            # Extract key (part before em-dash)
            key = stripped.split(" — ")[0] if " — " in stripped else stripped

            key_lower = key.lower()
            # Always store (last occurrence wins), duplicates caught separately
            entries[key_lower] = (i, stripped, current_section)

    return entries


def validate(index_path: Path | str, root: Path, autofix: bool = True) -> list[str]:
    """Validate memory index. Returns list of error strings.

    Autofix is enabled by default for section placement, ordering,
    and structural section cleanup.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.
        autofix: Whether to autofix placement/ordering/structural issues.

    Returns:
        List of error messages. Empty list if no errors found.
    """
    headers = collect_semantic_headers(root)
    structural = collect_structural_headers(root)
    entries = extract_index_entries(index_path, root)

    errors = []

    # Check for duplicate index entries
    errors.extend(check_duplicate_entries(index_path, root))

    # Check D-3 format compliance and word count
    errors.extend(check_em_dash_and_word_count(entries))

    # Check section placement, ordering, and structural entries (autofixable)
    placement_errors = check_entry_placement(entries, headers)
    ordering_errors = check_entry_sorting(index_path, root, headers)
    structural_entries = check_structural_entries(entries, structural)

    # Check for orphan semantic headers (headers without index entries)
    for title, locations in sorted(headers.items()):
        if title not in entries:
            for filepath, lineno, level in locations:
                errors.append(
                    f"  {filepath}:{lineno}: orphan semantic header '{title}' "
                    f"({level} level) has no memory-index.md entry"
                )

    # Check for orphan index entries (entries without matching headers)
    errors.extend(check_orphan_entries(entries, headers, structural))

    # Check for duplicate headers across files
    for title, locations in sorted(headers.items()):
        if len(locations) > 1:
            files = {filepath for filepath, _, _ in locations}
            if len(files) > 1:  # Only error if duplicates are in different files
                errors.append(f"  Duplicate header '{title}' found in multiple files:")
                for filepath, lineno, level in locations:
                    errors.append(f"    {filepath}:{lineno} ({level} level)")

    # Handle placement, ordering, and structural entry errors
    if placement_errors or ordering_errors or structural_entries:
        if autofix:
            fixed = autofix_index(index_path, root, headers, structural)
            if fixed:
                parts = []
                if placement_errors:
                    parts.append(f"{len(placement_errors)} placement")
                if ordering_errors:
                    parts.append(f"{len(ordering_errors)} ordering")
                if structural_entries:
                    parts.append(f"{len(structural_entries)} structural")
                print(f"Autofixed {' and '.join(parts)} issues", file=sys.stderr)
                return errors

            # Autofix failed, report as errors
            errors.extend(placement_errors)
            errors.extend(ordering_errors)
            errors.extend(structural_entries)
        else:
            # Autofix disabled, report as errors
            errors.extend(placement_errors)
            errors.extend(ordering_errors)
            errors.extend(structural_entries)

    return errors
