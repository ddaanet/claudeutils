"""Parse memory-index.md into structured entries."""

import logging
import re
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Common stopwords to exclude from keywords
STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "can",
    "for",
    "from",
    "to",
    "at",
    "in",
    "by",
    "on",
    "with",
    "as",
    "if",
    "and",
    "or",
    "not",
    "this",
    "that",
    "it",
    "its",
    "my",
    "your",
    "our",
    "their",
    "of",
}


class IndexEntry(BaseModel):
    """Parsed entry from memory-index.md."""

    key: str  # Text before em-dash
    description: str  # Text after em-dash
    referenced_file: str  # From parent H2 heading (file path)
    section: str  # Parent H2 heading text
    keywords: set[str]  # Extracted from key + description


def _extract_keywords(text: str) -> set[str]:
    """Extract keywords from text.

    Tokenizes on whitespace and punctuation, lowercases, removes stopwords.

    Args:
        text: Text to tokenize

    Returns:
        Set of keywords
    """
    # Split on whitespace and punctuation
    tokens = re.split(r"[\s\-_.,;:()[\]{}\"'`]+", text.lower())

    # Remove empty strings and stopwords
    return {token for token in tokens if token and token not in STOPWORDS}


def parse_memory_index(index_file: Path) -> list[IndexEntry]:
    """Parse memory-index.md into structured entries.

    Extracts H2 sections (file paths) and entries (key — description format).
    Skips special sections that don't map to clear Read targets:
    - "Behavioral Rules (fragments — already loaded)"
    - "Technical Decisions (mixed — check entry for specific file)"

    Args:
        index_file: Path to memory-index.md

    Returns:
        List of IndexEntry objects
    """
    entries: list[IndexEntry] = []

    try:
        content = index_file.read_text()
    except OSError as e:
        logger.warning(f"Failed to read {index_file}: {e}")
        return []

    lines = content.split("\n")
    current_section = ""
    current_file = ""
    skip_section = False

    for line in lines:
        # Check for H2 headings (##)
        if line.startswith("## "):
            current_section = line[3:].strip()

            # Determine if this is a file path or special section
            if current_section.startswith(("Behavioral Rules", "Technical Decisions")):
                skip_section = True
                current_file = ""
            else:
                skip_section = False
                current_file = current_section

            continue

        # Skip entries in special sections
        if skip_section:
            continue

        # Skip empty lines and non-entry lines
        if not line.strip() or not current_file:
            continue

        # Skip lines that don't match entry format (key — description)
        if " — " not in line:
            continue

        # Parse entry: key — description
        parts = line.split(" — ", 1)
        if len(parts) != 2:
            continue

        key = parts[0].strip()
        description = parts[1].strip()

        if not key or not description:
            continue

        # Extract keywords from both key and description
        keywords = _extract_keywords(key + " " + description)

        entry = IndexEntry(
            key=key,
            description=description,
            referenced_file=current_file,
            section=current_section,
            keywords=keywords,
        )
        entries.append(entry)

    return entries
