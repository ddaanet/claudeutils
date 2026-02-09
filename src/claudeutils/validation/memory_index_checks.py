"""Check functions for memory index validation.

Contains validation check functions extracted from memory_index_helpers.py.
"""

import re
from pathlib import Path

from .memory_index_helpers import EXEMPT_SECTIONS, extract_index_structure


def check_duplicate_entries(index_path: Path | str, root: Path) -> list[str]:
    """Check for duplicate index entries.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.

    Returns:
        List of error messages for duplicate entries.
    """
    errors: list[str] = []
    try:
        if isinstance(index_path, str):
            full_path = root / index_path
        else:
            full_path = root / index_path
        lines = full_path.read_text().splitlines()
    except FileNotFoundError:
        return errors

    seen_entry_keys: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip non-entry lines
        if not stripped or stripped.startswith(("#", "**", "- ")):
            continue
        # Extract key
        key = (
            stripped.split(" — ")[0].lower() if " — " in stripped else stripped.lower()
        )
        # Check for duplicates
        if key in seen_entry_keys:
            errors.append(
                f"  memory-index.md:{i}: duplicate index entry '{key}' "
                f"(first at line {seen_entry_keys[key]})"
            )
        else:
            seen_entry_keys[key] = i

    return errors


def check_em_dash_and_word_count(entries: dict[str, tuple[int, str, str]]) -> list[str]:
    """Check entries for em-dash separator and word count.

    Args:
        entries: Dictionary of entries from extract_index_entries.

    Returns:
        List of error messages.
    """
    errors = []
    for lineno, full_entry, _section in entries.values():
        if " — " not in full_entry:
            errors.append(
                f"  memory-index.md:{lineno}: entry lacks em-dash separator "
                f"(D-3): '{full_entry}'"
            )
        else:
            # Check word count (8-15 word hard limit for key + description total)
            word_count = len(full_entry.split())
            if word_count < 8 or word_count > 15:
                errors.append(
                    f"  memory-index.md:{lineno}: entry has {word_count} words, "
                    f"must be 8-15: '{full_entry}'"
                )
    return errors


def check_entry_placement(
    entries: dict[str, tuple[int, str, str]],
    headers: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    """Check that entries are in correct file sections.

    Args:
        entries: Dictionary of entries from extract_index_entries.
        headers: Dictionary of semantic headers from collect_semantic_headers.

    Returns:
        List of error messages for misplaced entries.
    """
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in headers:
            # Get the file this header is in
            source_file = headers[key][0][0]  # First location's file
            if section != source_file:
                errors.append(
                    f"  memory-index.md:{lineno}: entry '{key}' in section "
                    f"'{section}' but header is in '{source_file}'"
                )
    return errors


def check_entry_sorting(
    index_path: Path | str,
    root: Path,
    headers: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    """Check that entries within sections match file order.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.
        headers: Dictionary of semantic headers from collect_semantic_headers.

    Returns:
        List of error messages for out-of-order entries.
    """
    # Section header that specifies a file path
    file_section = re.compile(r"^## (agents/decisions/\S+\.md)$")

    errors = []
    _preamble, sections = extract_index_structure(index_path, root)
    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            continue
        # Check if this section is a file path
        if not file_section.match(f"## {section_name}"):
            continue

        # Get entries with their source line numbers
        entry_positions = []
        for entry in entry_lines:
            key = entry.split(" — ")[0].lower() if " — " in entry else entry.lower()
            if key in headers:
                source_lineno = headers[key][0][1]  # Line number in source file
                entry_positions.append((source_lineno, entry))

        # Check if sorted by source line number
        sorted_positions = sorted(entry_positions)
        if entry_positions != sorted_positions:
            errors.append(f"  Section '{section_name}': entries not in file order")

    return errors


def check_orphan_entries(
    entries: dict[str, tuple[int, str, str]],
    headers: dict[str, list[tuple[str, int, str]]],
    structural: set[str],
) -> list[str]:
    """Check for orphan index entries (no matching headers).

    Args:
        entries: Dictionary of entries from extract_index_entries.
        headers: Dictionary of semantic headers from collect_semantic_headers.
        structural: Set of structural header titles.

    Returns:
        List of error messages for orphan entries.
    """
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
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
    return errors


def check_structural_entries(
    entries: dict[str, tuple[int, str, str]], structural: set[str]
) -> list[str]:
    """Check for entries pointing to structural sections.

    Args:
        entries: Dictionary of entries from extract_index_entries.
        structural: Set of structural header titles.

    Returns:
        List of error messages for structural entries.
    """
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in structural:
            errors.append(
                f"  memory-index.md:{lineno}: entry '{key}' points to "
                f"structural section"
            )
    return errors
