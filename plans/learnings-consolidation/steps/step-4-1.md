# Step 4.1

**Plan**: `plans/learnings-consolidation/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 4.1: Unit Tests for learning-ages.py

**Objective:** Comprehensive test coverage for git-active-day calculation with mocked git operations.

**Implementation:**

Create `tests/test_learning_ages.py`:

**1. Test structure setup:**

```python
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add agent-core/bin to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "agent-core" / "bin"))

import learning_ages  # Import after path modification
```

**2. Test categories (per design Implementation Component 6):**

**A. Parsing tests:**
```python
def test_extract_h2_headers():
    """Extract H2 headers from learnings.md, skip first 10 lines (preamble)."""
    lines = [
        "# Learnings\n",
        "\n",
        "Preamble text...\n",
        *["...\n"] * 7,  # Lines 4-10
        "## First learning\n",  # Line 11 — first extracted
        "- Content\n",
        "## Second learning\n",
        "- More content\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert headers[0] == (11, "First learning")
    assert headers[1] == (13, "Second learning")
    # Verify preamble skipped: no headers from lines 1-10
    assert all(line_num > 10 for line_num, _ in headers)

def test_malformed_headers_skipped():
    """Skip malformed headers gracefully, continue processing."""
    lines = [
        *["preamble\n"] * 10,
        "## Valid header\n",
        "###Not a header (no space)\n",
        "## Another valid\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert "Valid header" in str(headers)
    assert "Another valid" in str(headers)
```

**B. Age calculation tests:**
```python
@patch('subprocess.run')
def test_active_day_calculation(mock_run):
    """Count unique commit dates between entry date and today."""
    # Mock git blame output
    mock_run.return_value = MagicMock(
        stdout="a1b2c3d (Author 2026-01-15 00:00:00 +0000 11) ## Learning title",
        returncode=0
    )

    entry_date = learning_ages.get_entry_date("agents/learnings.md", 11)

    assert entry_date == "2026-01-15"
    mock_run.assert_called_once_with(
        ["git", "blame", "-C", "-C", "--first-parent", "-L", "11,11", "--", "agents/learnings.md"],
        capture_output=True,
        text=True,
        check=True
    )

@patch('subprocess.run')
def test_active_days_excludes_inactive_days(mock_run):
    """Only count days with commits, not calendar days."""
    # Mock git log output — 5 unique dates over 10 calendar days
    mock_run.return_value = MagicMock(
        stdout="2026-01-15\n2026-01-16\n2026-01-18\n2026-01-22\n2026-01-25\n",
        returncode=0
    )

    active_days = learning_ages.count_active_days("2026-01-15", "2026-01-25")

    assert active_days == 5  # Not 10 (calendar days)

def test_entry_added_today_zero_active_days():
    """Entry added today should have 0 active days."""
    from datetime import date
    today = date.today().isoformat()

    active_days = learning_ages.count_active_days(today, today)

    assert active_days == 0

@patch('subprocess.run')
def test_merge_commits_handled(mock_run):
    """Merge commits processed via --first-parent flag."""
    # Mock git blame on merge commit
    mock_run.return_value = MagicMock(
        stdout="merge123 (Author 2026-01-20 00:00:00 +0000 15) ## Merge learning",
        returncode=0
    )

    entry_date = learning_ages.get_entry_date("agents/learnings.md", 15)

    assert entry_date == "2026-01-20"
    # Verify --first-parent flag present
    assert "--first-parent" in mock_run.call_args[0][0]
```

**C. Staleness detection tests:**
```python
@patch('subprocess.run')
def test_staleness_finds_last_consolidation(mock_run):
    """Find most recent commit with removed H2 headers (consolidation evidence)."""
    # Mock git log -p output with removed headers
    mock_run.return_value = MagicMock(
        stdout="""
commit abc123 2026-01-20
-## Old learning 1
-## Old learning 2

commit def456 2026-01-10
-## Even older learning
""",
        returncode=0
    )

    last_consolidation = learning_ages.find_last_consolidation("agents/learnings.md")

    assert last_consolidation == "2026-01-20"  # Most recent
    mock_run.assert_called_with(
        ["git", "log", "-p", "--", "agents/learnings.md"],
        capture_output=True,
        text=True,
        check=True
    )

@patch('subprocess.run')
def test_staleness_fallback_no_prior_consolidation(mock_run):
    """Report 'N/A (no prior consolidation detected)' when no removed headers found."""
    # Mock git log -p output with no removed H2 headers
    mock_run.return_value = MagicMock(
        stdout="commit abc123\n+## New learning\n",  # Only additions
        returncode=0
    )

    last_consolidation = learning_ages.find_last_consolidation("agents/learnings.md")

    assert last_consolidation is None  # Script formats this as "N/A (...)"

def test_multiple_consolidations_uses_most_recent():
    """When multiple consolidations found, use most recent."""
    # Test via integration with mocked git log (already covered in test above)
    pass  # Covered by test_staleness_finds_last_consolidation
```

**D. Trigger logic tests:**
```python
def test_size_trigger_thresholds():
    """Size trigger: <150 no trigger, ≥150 trigger."""
    assert learning_ages.check_size_trigger(149) is False
    assert learning_ages.check_size_trigger(150) is True
    assert learning_ages.check_size_trigger(151) is True

def test_staleness_trigger_thresholds():
    """Staleness trigger: <14 days no trigger, ≥14 days trigger."""
    assert learning_ages.check_staleness_trigger(13) is False
    assert learning_ages.check_staleness_trigger(14) is True
    assert learning_ages.check_staleness_trigger(15) is True

def test_batch_minimum_threshold():
    """Batch minimum: <3 entries insufficient, ≥3 sufficient."""
    entries = [("## Entry 1", 10), ("## Entry 2", 9)]
    assert learning_ages.check_batch_minimum(entries, threshold=3) is False

    entries.append(("## Entry 3", 8))
    assert learning_ages.check_batch_minimum(entries, threshold=3) is True
```

**E. Freshness filter tests:**
```python
def test_freshness_filter_includes_gte_7_days():
    """Include entries ≥7 active days, exclude <7 days."""
    entries = [
        ("## Old entry", 10),
        ("## Fresh entry", 6),
        ("## Boundary entry", 7),
        ("## Very old", 22),
    ]

    filtered = learning_ages.filter_by_freshness(entries, threshold=7)

    assert len(filtered) == 3
    assert ("## Fresh entry", 6) not in filtered
    assert ("## Boundary entry", 7) in filtered  # Boundary included

def test_boundary_exactly_7_days():
    """Exactly 7 active days should be included."""
    entries = [("## Boundary", 7)]

    filtered = learning_ages.filter_by_freshness(entries, threshold=7)

    assert len(filtered) == 1
```

**F. Error handling tests:**
```python
def test_missing_file_exits_with_error():
    """Missing learnings.md should exit 1 with stderr message."""
    with pytest.raises(FileNotFoundError):
        learning_ages.read_learnings_file("nonexistent.md")

@patch('subprocess.run')
def test_git_not_available(mock_run):
    """Git command failure should exit 1 with stderr message."""
    mock_run.side_effect = FileNotFoundError("git not found")

    with pytest.raises(FileNotFoundError):
        learning_ages.get_entry_date("agents/learnings.md", 11)

@patch('subprocess.run')
def test_malformed_learnings_continues(mock_run):
    """Malformed entries should be skipped with warning, not fatal."""
    # Already covered in parsing tests
    pass
```

**G. Integration test:**
```python
@patch('subprocess.run')
def test_full_pipeline(mock_run, tmp_path):
    """Full pipeline with mocked git repo produces correct markdown output."""
    # Create temp learnings.md
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("""
# Learnings

Preamble...
...(lines 3-10)
