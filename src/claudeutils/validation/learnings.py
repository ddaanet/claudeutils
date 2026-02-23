"""Validate learnings.md identifier syntax and uniqueness.

Checks:
- Title format: ## Title (markdown header)
- Max word count per title (default: 5)
- No duplicate titles
- No empty titles
"""

import re
from pathlib import Path

MAX_WORDS = 5
TITLE_PATTERN = re.compile(r"^## (.+)$")


def extract_titles(lines: list[str]) -> list[tuple[int, str]]:
    """Extract (line_number, title_text) pairs from learning titles.

    Args:
        lines: List of file lines.

    Returns:
        List of (line_number, title_text) tuples, skipping preamble (first 10 lines).
    """
    titles = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip first 10 lines (preamble/header)
        if i <= 10:
            continue
        # Match ## Title headers
        m = TITLE_PATTERN.match(stripped)
        if m:
            titles.append((i, m.group(1)))
    return titles


def parse_segments(content: str) -> dict[str, list[str]]:
    """Parse learnings.md into segments keyed by heading text.

    Args:
        content: Raw file content as string.

    Returns:
        Ordered dict mapping heading text (or empty string for preamble) to list of
        body lines. The heading line itself is not included in body lines.
    """
    lines = content.splitlines()
    segments: dict[str, list[str]] = {}
    current_heading = ""
    current_body: list[str] = []

    for line in lines:
        m = TITLE_PATTERN.match(line)
        if m:
            if current_heading or current_body:
                segments[current_heading] = current_body
            current_heading = m.group(1)
            current_body = []
        else:
            current_body.append(line)

    if current_heading or current_body:
        segments[current_heading] = current_body

    return segments


def _detect_orphaned_content(lines: list[str]) -> list[str]:
    """Find non-blank lines after preamble but before first ## heading."""
    errors: list[str] = []
    first_heading_line = None
    for i, line in enumerate(lines, 1):
        if i <= 10:
            continue
        if TITLE_PATTERN.match(line.strip()):
            first_heading_line = i
            break

    if first_heading_line is None:
        return errors

    for i in range(11, first_heading_line):
        stripped = lines[i - 1].strip()
        if stripped:
            errors.append(
                f"  line {i}: orphaned content (not under a ## heading): {stripped}"
            )
    return errors


def validate(path: Path, root: Path, max_words: int = MAX_WORDS) -> list[str]:
    """Validate learnings file. Returns list of error strings.

    Args:
        path: Path to learnings file (relative to root).
        root: Project root directory.
        max_words: Maximum allowed words in a title (default: 5).

    Returns:
        List of error messages. Empty list if no errors found.
    """
    full_path = root / path
    try:
        with full_path.open() as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    titles = extract_titles(lines)
    errors = []
    seen: dict[str, int] = {}

    for lineno, title in titles:
        words = title.split()
        if len(words) > max_words:
            errors.append(
                f"  line {lineno}: title has {len(words)} words (max {max_words}): "
                f"## {title}"
            )

        key = title.lower()
        if key in seen:
            errors.append(
                f"  line {lineno}: duplicate title (first at line {seen[key]}): "
                f"## {title}"
            )
        else:
            seen[key] = lineno

    errors.extend(_detect_orphaned_content(lines))
    return errors
