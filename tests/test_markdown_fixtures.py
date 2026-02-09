"""Test fixture infrastructure for markdown test corpus."""

from pathlib import Path


def test_fixture_directory_exists() -> None:
    """Fixture directory should exist and be empty initially."""
    fixture_dir = Path(__file__).parent / "fixtures" / "markdown"

    # Directory must exist
    assert fixture_dir.exists(), f"Fixture directory {fixture_dir} does not exist"

    # Directory must be a directory, not a file
    assert fixture_dir.is_dir(), f"Path {fixture_dir} exists but is not a directory"

    # Directory must be empty initially
    contents = list(fixture_dir.iterdir())
    assert contents == [], f"Fixture directory should be empty but contains: {contents}"
