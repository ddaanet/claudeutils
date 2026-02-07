"""Tests for learnings validator."""

import pytest
from pathlib import Path

from claudeutils.validation.learnings import validate


def test_valid_learnings_file_returns_no_errors(tmp_path):
    """Test that valid learnings file returns no errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Institutional knowledge accumulated across sessions.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate.

---
## Learning One
Content here.

## Learning Two
More content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_title_exceeding_max_word_count_returns_error(tmp_path):
    """Test that title exceeding max word count returns error."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble line 2
Preamble line 3
Preamble line 4
Preamble line 5
Preamble line 6
Preamble line 7
Preamble line 8
Preamble line 9
Preamble line 10
## This is a title with way too many words for the validator
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "title has 12 words (max 5)" in errors[0]
    assert "line 12" in errors[0]


def test_duplicate_titles_detected_case_insensitive(tmp_path):
    """Test that duplicate titles are detected (case-insensitive)."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble line 2
Preamble line 3
Preamble line 4
Preamble line 5
Preamble line 6
Preamble line 7
Preamble line 8
Preamble line 9
Preamble line 10
## First Learning Title
Content here.

## First learning title
Different content but same title.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 1
    assert "duplicate title" in errors[0]
    assert "line 15" in errors[0]
    assert "first at line 12" in errors[0]


def test_preamble_first_10_lines_skipped(tmp_path):
    """Test that preamble (first 10 lines) is skipped."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9
Line 10
## First Valid Title
Content here.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_empty_file_returns_no_errors(tmp_path):
    """Test that empty file returns no errors."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("")
    errors = validate(Path("learnings.md"), tmp_path)
    assert errors == []


def test_missing_file_returns_no_errors(tmp_path):
    """Test that missing file returns no errors (graceful degradation)."""
    errors = validate(Path("nonexistent.md"), tmp_path)
    assert errors == []


def test_multiple_errors_reported(tmp_path):
    """Test that multiple errors are all reported."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""# Learnings

Preamble line 2
Preamble line 3
Preamble line 4
Preamble line 5
Preamble line 6
Preamble line 7
Preamble line 8
Preamble line 9
Preamble line 10
## First Title Word Count Too Long Here Now
Content here.

## Second Title Word Count Too Long Here Now
Different content.

## Duplicate Title
Another content.

## duplicate title
Final content.
""")
    errors = validate(Path("learnings.md"), tmp_path)
    assert len(errors) == 3
    assert any("title has 8 words" in e for e in errors)
    assert any("title has 8 words" in e for e in errors)
    assert any("duplicate title" in e for e in errors)
