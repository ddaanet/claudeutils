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
    EXEMPT_SECTIONS,
    INDEXED_GLOBS,
    autofix_index,
    collect_semantic_headers,
    collect_structural_headers,
    extract_index_structure,
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
            if " — " in stripped:
                key = stripped.split(" — ")[0]
            else:
                # Fallback: whole line is key
                key = stripped

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
    placement_errors = []
    ordering_errors = []
    structural_entries = []  # Entries pointing to structural sections (to remove)

    # Check for duplicate index entries by scanning raw file
    try:
        if isinstance(index_path, str):
            full_path = root / index_path
        else:
            full_path = root / index_path
        lines = full_path.read_text().splitlines()
    except FileNotFoundError:
        lines = []

    seen_entry_keys: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip non-entry lines
        if not stripped or stripped.startswith("#") or stripped.startswith("**") or stripped.startswith("- "):
            continue
        # Extract key
        if " — " in stripped:
            key = stripped.split(" — ")[0].lower()
        else:
            key = stripped.lower()
        # Check for duplicates
        if key in seen_entry_keys:
            errors.append(
                f"  memory-index.md:{i}: duplicate index entry '{key}' "
                f"(first at line {seen_entry_keys[key]})"
            )
        else:
            seen_entry_keys[key] = i

    # Check D-3 format compliance: entries must have em-dash separator
    for key, (lineno, full_entry, section) in entries.items():
        if " — " not in full_entry:
            errors.append(
                f"  memory-index.md:{lineno}: entry lacks em-dash separator (D-3): '{full_entry}'"
            )
        else:
            # Check word count (8-15 word hard limit for key + description total)
            word_count = len(full_entry.split())
            if word_count < 8 or word_count > 15:
                errors.append(
                    f"  memory-index.md:{lineno}: entry has {word_count} words, must be 8-15: '{full_entry}'"
                )

    # Check section placement: entry should be in section matching its source file
    for key, (lineno, full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in headers:
            # Get the file this header is in
            source_file = headers[key][0][0]  # First location's file
            if section != source_file:
                placement_errors.append(
                    f"  memory-index.md:{lineno}: entry '{key}' in section '{section}' "
                    f"but header is in '{source_file}'"
                )

    # Check ordering within sections: entries should match file order
    preamble, sections = extract_index_structure(index_path, root)
    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            continue
        # Check if this section is a file path
        if not FILE_SECTION.match(f"## {section_name}"):
            continue

        # Get entries with their source line numbers
        entry_positions = []
        for entry in entry_lines:
            if " — " in entry:
                key = entry.split(" — ")[0].lower()
            else:
                key = entry.lower()
            if key in headers:
                source_lineno = headers[key][0][1]  # Line number in source file
                entry_positions.append((source_lineno, entry))

        # Check if sorted by source line number
        sorted_positions = sorted(entry_positions, key=lambda x: x[0])
        if entry_positions != sorted_positions:
            ordering_errors.append(
                f"  Section '{section_name}': entries not in file order"
            )

    # Check for orphan semantic headers (headers without index entries)
    # Per design R-4: all semantic headers must have index entries (ERROR blocks commit)
    for title, locations in sorted(headers.items()):
        if title not in entries:
            for filepath, lineno, level in locations:
                errors.append(
                    f"  {filepath}:{lineno}: orphan semantic header '{title}' "
                    f"({level} level) has no memory-index.md entry"
                )

    # Check for orphan index entries (entries without matching headers)
    # Index entries must reference semantic headers in permanent docs (decisions/)
    for key, (lineno, full_entry, section) in entries.items():
        # Skip exempt sections
        if section in EXEMPT_SECTIONS:
            continue
        # Skip entries pointing to structural sections (will be removed by autofix)
        if key in structural:
            continue
        if key not in headers:
            errors.append(
                f"  memory-index.md:{lineno}: orphan index entry '{key}' "
                f"has no matching semantic header in agents/decisions/"
            )

    # Check for entries pointing to structural sections (should be removed)
    for key, (lineno, full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in structural:
            structural_entries.append(
                f"  memory-index.md:{lineno}: entry '{key}' points to structural section"
            )

    # Check for duplicate headers across files
    # Headers should appear in only one file to avoid confusion
    for title, locations in sorted(headers.items()):
        if len(locations) > 1:
            files = set(filepath for filepath, _, _ in locations)
            if len(files) > 1:  # Only error if duplicates are in different files
                errors.append(
                    f"  Duplicate header '{title}' found in multiple files:"
                )
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
            else:
                errors.extend(placement_errors)
                errors.extend(ordering_errors)
                errors.extend(structural_entries)
        else:
            errors.extend(placement_errors)
            errors.extend(ordering_errors)
            errors.extend(structural_entries)

    return errors
