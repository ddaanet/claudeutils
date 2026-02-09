"""Test fixtures for markdown tests."""

from pathlib import Path

# Create fixture directories on module import
MARKDOWN_FIXTURES_DIR = Path(__file__).parent / "markdown"
MARKDOWN_FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
