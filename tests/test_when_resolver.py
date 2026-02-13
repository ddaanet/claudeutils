"""Tests for resolver module."""

from pathlib import Path

from claudeutils.when.resolver import resolve


def test_mode_detection(tmp_path: Path) -> None:
    """Mode detection routes query to correct resolution mode.

    Section and file modes are tested here; trigger mode is tested in
    test_trigger_mode_resolves.
    """
    # Create minimal test files for section and file mode tests
    index_file = tmp_path / "test_index.md"
    index_file.write_text("## testing\n\n/when test | extra\n")

    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    testing_file = decisions_dir / "testing.md"
    testing_file.write_text("## Test Section\n\nTest content.\n")

    # Section mode detection (returns "section" mode identifier for now)
    # Note: Full section mode implementation is in a later cycle
    # For now, this test just verifies the mode is detected
    section = resolve("section", ".Test Section", str(index_file), str(decisions_dir))
    assert section == "section"

    # File mode detection (returns "file" mode identifier for now)
    # Note: Full file mode implementation is in a later cycle
    file_mode = resolve("file", "..testing.md", str(index_file), str(decisions_dir))
    assert file_mode == "file"


def test_trigger_mode_resolves(tmp_path: Path) -> None:
    """Trigger mode resolves query to heading in decision file via fuzzy match.

    Tests exact and approximate matching against index entries.
    """
    # Create a test index file with section pointing to a file
    index_file = tmp_path / "test_index.md"
    index_file.write_text(
        "## testing\n"
        "\n"
        "/when writing mock tests | mock patch, test doubles\n"
        "/when error handling | exceptions, debugging\n"
    )

    # Create a decisions directory with a decision file
    decisions_dir = tmp_path / "decisions"
    decisions_dir.mkdir()

    decision_file = decisions_dir / "testing.md"
    decision_file.write_text(
        "## When Writing Mock Tests\n"
        "\n"
        "Mock tests prevent side effects...\n"
        "\n"
        "## Error Handling\n"
        "\n"
        "Handle errors gracefully.\n"
    )

    # Query exact match should resolve to heading
    result = resolve(
        "trigger", "writing mock tests", str(index_file), str(decisions_dir)
    )
    assert "## When Writing Mock Tests" in result
    assert "Mock tests prevent side effects" in result

    # Query with approximate match should also resolve
    result = resolve("trigger", "mock test", str(index_file), str(decisions_dir))
    assert "## When Writing Mock Tests" in result
