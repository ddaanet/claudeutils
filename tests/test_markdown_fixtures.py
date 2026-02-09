"""Test fixture infrastructure for markdown test corpus."""

from pathlib import Path

import pytest


def load_fixture_pair(
    name: str, fixtures_dir: Path | None = None
) -> tuple[list[str], list[str]]:
    """Load a fixture pair from .input.md and .expected.md files.

    Args:
        name: Base fixture name (without extension)
        fixtures_dir: Directory containing fixtures. Defaults to tests/fixtures/markdown

    Returns:
        Tuple of (input_lines, expected_lines) with newlines preserved

    Raises:
        FileNotFoundError: If either fixture file is missing
    """
    if fixtures_dir is None:
        fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"

    input_file = fixtures_dir / f"{name}.input.md"
    expected_file = fixtures_dir / f"{name}.expected.md"

    if not input_file.exists():
        raise FileNotFoundError(f"Input fixture not found: {input_file}")
    if not expected_file.exists():
        raise FileNotFoundError(f"Expected fixture not found: {expected_file}")

    input_lines = input_file.read_text().splitlines(keepends=True)
    expected_lines = expected_file.read_text().splitlines(keepends=True)

    return input_lines, expected_lines


def test_load_fixture_pair() -> None:
    """Helper function should load fixture pairs correctly."""
    # Create temporary test fixtures
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"
    test_name = "01-example"

    # Write test fixture files
    input_file = fixtures_dir / f"{test_name}.input.md"
    expected_file = fixtures_dir / f"{test_name}.expected.md"

    input_content = "# Test\nLine 1\n"
    expected_content = "# Test\nProcessed\n"

    input_file.write_text(input_content)
    expected_file.write_text(expected_content)

    try:
        # Test: load_fixture_pair returns correct tuple
        input_lines, expected_lines = load_fixture_pair(test_name, fixtures_dir)

        # Verify types
        assert isinstance(input_lines, list), "input_lines should be list"
        assert isinstance(expected_lines, list), "expected_lines should be list"
        assert all(isinstance(line, str) for line in input_lines)
        assert all(isinstance(line, str) for line in expected_lines)

        # Verify content with newlines preserved
        assert input_lines == ["# Test\n", "Line 1\n"]
        assert expected_lines == ["# Test\n", "Processed\n"]

    finally:
        # Cleanup test fixtures
        if input_file.exists():
            input_file.unlink()
        if expected_file.exists():
            expected_file.unlink()


def test_load_fixture_pair_missing_input() -> None:
    """Should raise FileNotFoundError if input file missing."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"

    with pytest.raises(FileNotFoundError, match="Input fixture not found"):
        load_fixture_pair("nonexistent", fixtures_dir)


def test_load_fixture_pair_missing_expected() -> None:
    """Should raise FileNotFoundError if expected file missing."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"
    test_name = "02-partial"

    # Create only input file
    input_file = fixtures_dir / f"{test_name}.input.md"
    input_file.write_text("test\n")

    try:
        with pytest.raises(FileNotFoundError, match="Expected fixture not found"):
            load_fixture_pair(test_name, fixtures_dir)
    finally:
        if input_file.exists():
            input_file.unlink()


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
