"""Tests for memory index validator."""

from pathlib import Path

from claudeutils.validation.memory_index import validate


def test_valid_index_with_matching_headers(tmp_path: Path) -> None:
    """Test that valid index with matching headers returns no errors."""
    # Create a decision file with semantic headers
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Decision One
Content here.

## Decision Two
More content.
""")

    # Create memory index with matching entries
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Decision One — First important decision with content here okay
Decision Two — Second important decision with more content great
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_orphan_semantic_header_error(tmp_path: Path) -> None:
    """Test that orphan semantic header (not in index) returns error (FR-5)."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Missing from Index
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "orphan semantic header 'missing from index'" in errors[0]
    assert "has no memory-index.md entry" in errors[0]


def test_orphan_index_entry_error(tmp_path: Path) -> None:
    """Test that orphan index entry (no matching header) returns error."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Existing Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Nonexistent Header — Entry pointing to header that does not exist here
Existing Header — Entry that matches a real semantic header now
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "orphan index entry 'nonexistent header'" in errors[0]
    assert "has no matching semantic header" in errors[0]


def test_duplicate_index_entries_error(tmp_path: Path) -> None:
    """Test that duplicate index entries return error."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Test Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Test Header — First entry matching the semantic header
Test Header — Second entry with the same key appearing again here
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 1
    assert "duplicate index entry" in errors[0]
    assert "test header" in errors[0]


def test_word_count_violation_error(tmp_path: Path) -> None:
    """Test that word count violation (outside 8-15 range) returns error."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Short Entry
Content here.

## Long Title Entry
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Short Entry — Too
Long Title Entry — This is way too many words in entry for validation purposes here
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert len(errors) == 2
    assert any("has 4 words" in e for e in errors)
    assert any("has 16 words" in e for e in errors)


def test_missing_em_dash_separator_error(tmp_path: Path) -> None:
    """Test that missing em-dash separator returns error."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Test Unique Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Test Unique Header just some words without em-dash separator
""")

    errors = validate("agents/memory-index.md", tmp_path)
    # Should report em-dash error AND orphan header (since the whole line becomes key)
    assert any("entry lacks em-dash separator (D-3)" in e for e in errors)


def test_entry_in_wrong_section_autofixed(tmp_path: Path) -> None:
    """Test that entry in wrong section is autofixed (no error if autofix=True)."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## First Header
Content here.
""")

    file2 = decisions_dir / "file-two.md"
    file2.write_text("""# File Two

## Second Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

Second Header — Entry wrongly placed in file one section here
First Header — Entry correctly in file one section here now
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify file was rewritten with correct sections
    content = index_file.read_text()
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content


def test_entries_out_of_order_autofixed(tmp_path: Path) -> None:
    """Test that out-of-order entries are autofixed."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## First Header
Content here.

## Second Header
More content.

## Third Header
Even more.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Third Header — Entry in wrong order but has valid content text here
First Header — Entry that should come first in section order now
Second Header — Entry in middle position with valid content today
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify file was rewritten in correct order
    content = index_file.read_text()
    lines = content.splitlines()
    # Find the lines in the file section
    section_idx = next(
        i for i, l in enumerate(lines) if "agents/decisions/test-decision.md" in l
    )
    entry_lines = [l for l in lines[section_idx:] if l and not l.startswith("##")]
    # Should be ordered by first header, second header, third header
    first_idx = next(
        i for i, l in enumerate(entry_lines) if l.startswith("First Header")
    )
    second_idx = next(
        i for i, l in enumerate(entry_lines) if l.startswith("Second Header")
    )
    third_idx = next(
        i for i, l in enumerate(entry_lines) if l.startswith("Third Header")
    )
    assert first_idx < second_idx < third_idx


def test_structural_header_entries_removed_by_autofix(tmp_path: Path) -> None:
    """Test that structural header entries are removed by autofix."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## .Organizational Section
Structural marker, no entry needed.

## Real Header
Semantic content.

## Another Real Header
More semantic content.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Organizational Section — Entry pointing to structural section should be removed
Real Header — Entry for semantic header with content here today
Another Real Header — Another entry for second semantic header here now
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify structural entry was removed
    content = index_file.read_text()
    assert "Organizational Section" not in content
    assert "Real Header" in content


def test_exempt_sections_preserved_as_is(tmp_path: Path) -> None:
    """Test that exempt sections are preserved as-is."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test Decision

## Test Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## Behavioral Rules (fragments — already loaded)

Some custom rule — description that shows em-dash format here
Another rule — another entry with proper em-dash separator today

## Technical Decisions (mixed — check entry for specific file)

Technical note — entry with em-dash in technical section here
Another item — another entry with proper format today now

## agents/decisions/test-decision.md

Test Header — Entry for semantic header with content here
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify exempt sections preserved
    content = index_file.read_text()
    assert "Some custom rule — description that shows em-dash format here" in content
    assert "Another rule — another entry with proper em-dash separator today" in content
    assert "Technical note — entry with em-dash in technical section here" in content


def test_autofix_false_reports_all_issues(tmp_path: Path) -> None:
    """Test that autofix=False reports all issues as errors."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## First Header
Content here.

## Second Header
More content.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

Second Header — Entry in wrong order here today ok
First Header — Entry that should come first now
""")

    # With autofix=False, should report errors
    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert len(errors) > 0
    assert any("entries not in file order" in e for e in errors)


def test_duplicate_headers_across_files_error(tmp_path: Path) -> None:
    """Test that duplicate headers across files return error."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## Duplicate Name
Content here.
""")

    file2 = decisions_dir / "file-two.md"
    file2.write_text("""# File Two

## Duplicate Name
Different content.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

Duplicate Name — Entry for duplicate header found multiple places now

## agents/decisions/file-two.md

Duplicate Name — Another entry for same duplicate header here too
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=False)
    assert len(errors) > 0
    assert any("Duplicate header 'duplicate name'" in e for e in errors)


def test_multiple_autofix_issues_resolved_in_single_pass(tmp_path: Path) -> None:
    """Test that multiple autofix issues resolved in single pass."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    file1 = decisions_dir / "file-one.md"
    file1.write_text("""# File One

## First Header
Content here.

## Second Header
More content.
""")

    file2 = decisions_dir / "file-two.md"
    file2.write_text("""# File Two

## Third Header
Content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/file-one.md

Second Header — Entry in wrong section and wrong order fix this now
Third Header — Entry in wrong section entirely different place today
First Header — Entry in wrong order here too needs reordering now

## agents/decisions/file-two.md
""")

    errors = validate("agents/memory-index.md", tmp_path, autofix=True)
    assert errors == []

    # Verify both issues were fixed
    content = index_file.read_text()
    assert "## agents/decisions/file-one.md" in content
    assert "## agents/decisions/file-two.md" in content

    # Verify Third Header moved to correct section
    lines = content.splitlines()
    file1_section_idx = next(
        i for i, l in enumerate(lines) if "agents/decisions/file-one.md" in l
    )
    file2_section_idx = next(
        i for i, l in enumerate(lines) if "agents/decisions/file-two.md" in l
    )
    # Third Header should be between file1 section header and file2 section header
    for i in range(file2_section_idx, len(lines)):
        if "Third Header" in lines[i]:
            assert i > file2_section_idx


def test_missing_index_file_returns_no_errors(tmp_path: Path) -> None:
    """Test graceful degradation when index file missing."""
    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_missing_decision_files_returns_no_errors(tmp_path: Path) -> None:
    """Test graceful degradation when decision files missing."""
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.parent.mkdir(parents=True)
    index_file.write_text("""# Memory Index

## agents/decisions/nonexistent.md
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_document_intro_exemption(tmp_path: Path) -> None:
    """Test that document intro content is exempt from validation."""
    decisions_dir = tmp_path / "agents" / "decisions"
    decisions_dir.mkdir(parents=True)

    decision_file = decisions_dir / "test-decision.md"
    decision_file.write_text("""# Test File

Intro content with ## that looks like header syntax
But this content should be skipped before first real header

## Real Header
Actual content here.
""")

    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.write_text("""# Memory Index

## agents/decisions/test-decision.md

Real Header — Semantic header after intro content here
""")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []


def test_empty_index_file_no_errors(tmp_path: Path) -> None:
    """Test empty index file (graceful degradation)."""
    index_file = tmp_path / "agents" / "memory-index.md"
    index_file.parent.mkdir(parents=True)
    index_file.write_text("")

    errors = validate("agents/memory-index.md", tmp_path)
    assert errors == []
