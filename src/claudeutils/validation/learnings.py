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
        with open(full_path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []

    titles = extract_titles(lines)
    errors = []
    seen = {}

    for lineno, title in titles:
        # Word count check
        words = title.split()
        if len(words) > max_words:
            errors.append(
                f"  line {lineno}: title has {len(words)} words (max {max_words}): "
                f"## {title}"
            )

        # Uniqueness check
        key = title.lower()
        if key in seen:
            errors.append(
                f"  line {lineno}: duplicate title (first at line {seen[key]}): "
                f"## {title}"
            )
        else:
            seen[key] = lineno

    return errors
