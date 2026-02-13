"""Compress key functionality for heading corpus loading."""

import re
from pathlib import Path


def load_heading_corpus(decisions_dir: Path) -> list[str]:
    """Load heading corpus from decision files.

    Args:
        decisions_dir: Path to the decisions directory.

    Returns:
        List of heading text strings from H2 and H3 headings, excluding
        structural headings (those starting with a dot).
    """
    headings = []

    # Scan all .md files in the directory
    for file_path in sorted(decisions_dir.glob("*.md")):
        content = file_path.read_text()

        # Extract H2+ headings: ^#{2,}\s+(.+)$
        for match in re.finditer(r"^#{2,}\s+(.+)$", content, re.MULTILINE):
            heading_text = match.group(1)

            # Filter out structural headings (starting with dot)
            if not heading_text.startswith("."):
                headings.append(heading_text)

    return headings
