"""Helper functions for memory index validation.

Contains collection and autofix functions extracted from memory_index.py to keep
main module under 350 lines.
"""

import re
from pathlib import Path

# Semantic header: ##+ followed by space and non-dot
SEMANTIC_HEADER = re.compile(r"^(##+) ([^.].+)$")
# Structural header: ##+ followed by space and dot
STRUCTURAL_HEADER = re.compile(r"^(##+) \..+$")
# Document title
DOC_TITLE = re.compile(r"^# .+$")

# Files that contain semantic headers requiring index entries
INDEXED_GLOBS = [
    "agents/decisions/*.md",
]

# Sections that are exempt from file-based validation
EXEMPT_SECTIONS = {
    "Behavioral Rules (fragments — already loaded)",
    "Technical Decisions (mixed — check entry for specific file)",
}


def collect_structural_headers(root: Path) -> set[str]:
    """Scan indexed files for all structural headers (marked with . prefix).

    Args:
        root: Project root directory.

    Returns:
        Set of lowercase titles (without the . prefix).
    """
    structural = set()

    for glob_pattern in INDEXED_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            try:
                lines = filepath.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            for line in lines:
                stripped = line.strip()
                match = STRUCTURAL_HEADER.match(stripped)
                if match:
                    # Get everything after "## ." or "### ."
                    full = stripped.split(" ", 1)[1]  # Remove ##+ prefix
                    title = full[1:]  # Remove leading .
                    structural.add(title.lower())

    return structural


def collect_semantic_headers(root: Path) -> dict[str, list[tuple[str, int, str]]]:
    """Scan indexed files for all semantic headers.

    Args:
        root: Project root directory.

    Returns:
        Dict: lowercase title → list of (file_path, line_number, header_level).
    """
    headers: dict[str, list[tuple[str, int, str]]] = {}

    for glob_pattern in INDEXED_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            rel = str(filepath.relative_to(root))
            try:
                lines = filepath.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            in_doc_intro = False
            seen_first_h2 = False

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # Track document intro exemption (only before first ## header)
                # After first ##, don't re-enter intro (# lines may be code comments)
                if not seen_first_h2 and DOC_TITLE.match(stripped):
                    in_doc_intro = True
                    continue

                # First ## ends document intro permanently
                if in_doc_intro and stripped.startswith("## "):
                    in_doc_intro = False
                    seen_first_h2 = True

                # Skip content in document intro
                if in_doc_intro:
                    continue

                # Match semantic headers
                m = SEMANTIC_HEADER.match(stripped)
                if m:
                    level = m.group(1)
                    title = m.group(2)
                    key = title.lower()
                    headers.setdefault(key, []).append((rel, i, level))

    return headers


def extract_index_structure(
    index_path: Path | str, root: Path
) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Extract full index structure for rewriting.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.

    Returns:
        Tuple of (preamble, sections):
        - preamble: List of lines before first ## section
        - sections: List of (section_name, [entry_lines])
    """
    try:
        if isinstance(index_path, str):
            full_path = root / index_path
        else:
            full_path = root / index_path
        lines = full_path.read_text().splitlines()
    except FileNotFoundError:
        return [], []

    preamble = []
    sections = []
    current_section = None
    current_entries: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Detect section headers
        if stripped.startswith("## ") and not stripped.startswith("### "):
            # Save previous section if exists
            if current_section is not None:
                sections.append((current_section, current_entries))
            current_section = stripped[3:]
            current_entries = []
            continue

        # Before first section = preamble
        if current_section is None:
            preamble.append(line)
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Skip bold directives
        if stripped.startswith("**"):
            continue

        # Entry line
        current_entries.append(stripped)

    # Don't forget last section
    if current_section is not None:
        sections.append((current_section, current_entries))

    return preamble, sections


def autofix_index(
    index_path: Path | str,
    root: Path,
    headers: dict[str, list[tuple[str, int, str]]],
    structural: set[str] | None = None,
) -> bool:
    """Rewrite memory-index.md with entries in correct sections and order.

    Also removes entries pointing to structural sections.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.
        headers: Dictionary of semantic headers (from collect_semantic_headers).
        structural: Set of structural section titles (from collect_structural_headers).

    Returns:
        True if rewrite succeeded, False otherwise.
    """
    if structural is None:
        structural = set()

    preamble, sections = extract_index_structure(index_path, root)

    # Build map: file path → sorted entries
    file_entries: dict[str, list[tuple[int, str]]] = {}
    exempt_entries = {}  # section_name → entries (preserve as-is)

    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            exempt_entries[section_name] = entry_lines
            continue

        for entry in entry_lines:
            key = entry.split(" — ")[0].lower() if " — " in entry else entry.lower()

            # Skip entries pointing to structural sections
            if key in structural:
                continue

            # Find which file this entry belongs to
            if key in headers:
                source_file = headers[key][0][0]
                source_lineno = headers[key][0][1]
                file_entries.setdefault(source_file, []).append((source_lineno, entry))

    # Sort entries within each file by source line number
    for entries_list in file_entries.values():
        entries_list.sort()

    # Rebuild the file
    output = []

    # Preamble
    output.extend(preamble)

    # Exempt sections first (preserve order from original)
    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            output.append(f"\n## {section_name}\n")
            output.extend(entry_lines)

    # File sections in sorted order
    for filepath in sorted(file_entries.keys()):
        output.append(f"\n## {filepath}\n")
        for _, entry in file_entries[filepath]:
            output.append(entry)

    # Write back
    try:
        if isinstance(index_path, str):
            full_path = root / index_path
        else:
            full_path = root / index_path
        content = "\n".join(output) + "\n"
        full_path.write_text(content)
    except OSError:
        return False
    else:
        return True


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
