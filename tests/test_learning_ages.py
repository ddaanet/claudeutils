"""Unit tests for learning-ages.py script.

Test coverage:
- Parsing: H2 extraction, preamble skip, malformed headers
- Age calculation: active days, git blame, merge commits
- Staleness detection: last consolidation via removed headers
- Trigger logic: size, staleness, batch minimum thresholds
- Freshness filter: 7-day threshold
- Error handling: missing files, git failures
- Integration: full pipeline with mocked git
"""

import pytest
import subprocess
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import importlib.util

# Import module with hyphens in name
script_path = Path(__file__).parent.parent / "agent-core" / "bin" / "learning-ages.py"
spec = importlib.util.spec_from_file_location("learning_ages", script_path)
learning_ages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(learning_ages)


# ==============================================================================
# A. Parsing tests
# ==============================================================================

def test_extract_titles_skips_preamble():
    """Extract H2 headers from learnings.md, skip first 10 lines (preamble)."""
    lines = [
        "# Learnings\n",
        "\n",
        "Preamble text...\n",
        "Line 4\n",
        "Line 5\n",
        "Line 6\n",
        "Line 7\n",
        "Line 8\n",
        "Line 9\n",
        "Line 10\n",
        "## First learning\n",  # Line 11 — first extracted
        "- Content\n",
        "## Second learning\n",  # Line 13
        "- More content\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert headers[0] == (11, "First learning")
    assert headers[1] == (13, "Second learning")
    # Verify preamble skipped: no headers from lines 1-10
    assert all(line_num > 10 for line_num, _ in headers)


def test_extract_titles_malformed_headers_skipped():
    """Skip malformed headers gracefully, continue processing."""
    lines = [
        *["preamble\n"] * 10,
        "## Valid header\n",
        "###Not a header (no space)\n",
        "## Another valid\n",
        "# Wrong level\n",
        "##Also no space\n",
    ]

    headers = learning_ages.extract_titles(lines)

    assert len(headers) == 2
    assert headers[0] == (11, "Valid header")
    assert headers[1] == (13, "Another valid")


def test_extract_titles_empty_file():
    """Empty file or only preamble should return empty list."""
    lines = ["# Learnings\n"] + ["preamble\n"] * 9

    headers = learning_ages.extract_titles(lines)

    assert headers == []


# ==============================================================================
# B. Age calculation tests
# ==============================================================================

@patch('subprocess.run')
def test_get_commit_date_for_line_parses_porcelain(mock_run):
    """Parse git blame porcelain output to extract commit date."""
    # Mock git blame --line-porcelain output
    mock_run.return_value = MagicMock(
        stdout=(
            "abc123def456 11 11 1\n"
            "author Author Name\n"
            "author-time 1705276800\n"
            "committer Committer Name\n"
            "committer-time 1705276800\n"  # 2024-01-15 00:00:00 UTC
            "summary Add learning entry\n"
            "\t## Learning title\n"
        ),
        returncode=0
    )

    commit_date = learning_ages.get_commit_date_for_line("agents/learnings.md", 11)

    assert commit_date == "2024-01-15"
    mock_run.assert_called_once_with(
        ["git", "blame", "-C", "-C", "--first-parent",
         "--line-porcelain", "-L11,11", "--", "agents/learnings.md"],
        capture_output=True,
        text=True,
        check=True
    )


@patch('subprocess.run')
def test_get_active_days_since_counts_unique_dates(mock_run):
    """Count unique commit dates, not calendar days."""
    # Mock git log output — 5 unique dates over 10 calendar days
    mock_run.return_value = MagicMock(
        stdout=(
            "2024-01-15\n"
            "2024-01-16\n"
            "2024-01-16\n"  # Duplicate
            "2024-01-18\n"
            "2024-01-22\n"
            "2024-01-25\n"
        ),
        returncode=0
    )

    active_days = learning_ages.get_active_days_since("2024-01-15")

    assert active_days == 5  # Not 6 (duplicate removed), not 10 (calendar days)


@patch('subprocess.run')
def test_get_active_days_since_entry_added_today(mock_run):
    """Entry added today should have non-zero active days if commits exist."""
    today = date.today().isoformat()
    # Mock git log --since=<today> includes today's commits
    mock_run.return_value = MagicMock(
        stdout=f"{today}\n",
        returncode=0
    )

    active_days = learning_ages.get_active_days_since(today)

    # If today has commits, count is 1 (today)
    assert active_days == 1


@patch('subprocess.run')
def test_get_commit_date_for_line_first_parent_flag(mock_run):
    """Verify --first-parent flag used for merge commit handling."""
    mock_run.return_value = MagicMock(
        stdout="committer-time 1705276800\n",
        returncode=0
    )

    learning_ages.get_commit_date_for_line("agents/learnings.md", 15)

    # Verify --first-parent flag present
    call_args = mock_run.call_args[0][0]
    assert "--first-parent" in call_args


@patch('subprocess.run')
def test_get_commit_date_for_line_git_error_returns_none(mock_run):
    """Git blame error should return None and print to stderr."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "git blame")

    commit_date = learning_ages.get_commit_date_for_line("agents/learnings.md", 11)

    assert commit_date is None


# ==============================================================================
# C. Staleness detection tests
# ==============================================================================

@patch('subprocess.run')
def test_get_last_consolidation_date_finds_recent(mock_run):
    """Find most recent commit with removed H2 headers (consolidation evidence)."""
    # Mock git log -p output with removed headers
    mock_run.return_value = MagicMock(
        stdout=(
            "commit abc123\n"
            "Date:   Mon Jan 20 10:00:00 2025 -0800\n"
            "\n"
            "-## Old learning 1\n"
            "-## Old learning 2\n"
            "\n"
            "commit def456\n"
            "Date:   Wed Jan 10 09:00:00 2025 -0800\n"
            "\n"
            "-## Even older learning\n"
        ),
        returncode=0
    )

    # Patch get_active_days_since to avoid nested git call
    with patch.object(learning_ages, 'get_active_days_since', return_value=15):
        last_date, staleness = learning_ages.get_last_consolidation_date("agents/learnings.md")

    assert last_date == "2025-01-20"  # Most recent
    assert staleness == 15


@patch('subprocess.run')
def test_get_last_consolidation_date_no_prior_consolidation(mock_run):
    """Return (None, None) when no removed headers found."""
    # Mock git log -p output with only additions
    mock_run.return_value = MagicMock(
        stdout=(
            "commit abc123\n"
            "Date:   Mon Jan 20 10:00:00 2025 -0800\n"
            "\n"
            "+## New learning\n"
        ),
        returncode=0
    )

    last_date, staleness = learning_ages.get_last_consolidation_date("agents/learnings.md")

    assert last_date is None
    assert staleness is None


@patch('subprocess.run')
def test_get_last_consolidation_date_removed_header_pattern(mock_run):
    """Only match lines starting with '-## ' (removed H2 headers)."""
    # Mock git log -p with various diff patterns
    mock_run.return_value = MagicMock(
        stdout=(
            "commit abc123\n"
            "Date:   Mon Jan 20 10:00:00 2025 -0800\n"
            "\n"
            "- This is a bullet, not a header\n"
            "-### H3 header removed\n"
            "-## H2 header removed\n"  # This should match
        ),
        returncode=0
    )

    with patch.object(learning_ages, 'get_active_days_since', return_value=10):
        last_date, staleness = learning_ages.get_last_consolidation_date("agents/learnings.md")

    assert last_date == "2025-01-20"
    assert staleness == 10


# ==============================================================================
# D. Error handling tests
# ==============================================================================

def test_main_missing_file_exits_with_error(tmp_path, capsys):
    """Missing learnings.md should exit 1 with stderr message."""
    nonexistent = tmp_path / "nonexistent.md"

    with pytest.raises(SystemExit) as exc_info:
        sys.argv = ["learning-ages.py", str(nonexistent)]
        learning_ages.main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err


def test_main_no_entries_exits_with_error(tmp_path, capsys):
    """File with no learning entries should exit 1."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text("# Learnings\n\n" + "Preamble\n" * 10)

    with pytest.raises(SystemExit) as exc_info:
        sys.argv = ["learning-ages.py", str(learnings_file)]
        learning_ages.main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "No learning entries found" in captured.err


@patch('subprocess.run')
def test_get_active_days_since_git_error_returns_zero(mock_run):
    """Git command failure should return 0 and print to stderr."""
    mock_run.side_effect = subprocess.CalledProcessError(1, "git log")

    active_days = learning_ages.get_active_days_since("2024-01-15")

    assert active_days == 0


# ==============================================================================
# E. Integration test
# ==============================================================================

@patch('subprocess.run')
def test_main_full_pipeline(mock_run, tmp_path, capsys):
    """Full pipeline with mocked git repo produces correct markdown output."""
    # Create temp learnings.md
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text(
        "# Learnings\n"
        "\n"
        "Preamble line 3\n"
        "Preamble line 4\n"
        "Preamble line 5\n"
        "Preamble line 6\n"
        "Preamble line 7\n"
        "Preamble line 8\n"
        "Preamble line 9\n"
        "Preamble line 10\n"
        "## Old learning\n"  # Line 11
        "- Content\n"
        "## Recent learning\n"  # Line 13
        "- More content\n"
    )

    # Mock git calls
    def mock_git_command(cmd, **kwargs):
        if "blame" in cmd:
            # Return porcelain format for line blame
            # Find -L argument which is in format "-L11,11"
            line_arg = [arg for arg in cmd if arg.startswith("-L")][0]
            line_num = int(line_arg[2:].split(",")[0])  # Extract from -L<num>,<num>
            if line_num == 11:
                timestamp = 1704067200  # 2024-01-01
            else:  # line 13
                timestamp = 1706659200  # 2024-01-31
            return MagicMock(
                stdout=f"committer-time {timestamp}\n",
                returncode=0
            )
        elif "log" in cmd and "-p" in cmd:
            # Mock git log -p for consolidation detection
            return MagicMock(
                stdout=(
                    "commit xyz789\n"
                    "Date:   Mon Jan 15 10:00:00 2024 -0800\n"
                    "\n"
                    "-## Consolidated learning\n"
                ),
                returncode=0
            )
        elif "log" in cmd:
            # Mock git log for active days calculation
            since_date = cmd[4].split("=")[1]  # Extract from --since=<date>
            if since_date == "2024-01-01":
                # 15 unique commit dates
                dates = [f"2024-01-{d:02d}" for d in range(1, 16)]
                return MagicMock(stdout="\n".join(dates) + "\n", returncode=0)
            elif since_date == "2024-01-31":
                # 5 unique commit dates
                dates = [f"2024-01-{d:02d}" for d in range(31, 36)]
                return MagicMock(stdout="\n".join(dates) + "\n", returncode=0)
            elif since_date == "2024-01-15":
                # 10 unique commit dates (for consolidation staleness)
                dates = [f"2024-01-{d:02d}" for d in range(15, 25)]
                return MagicMock(stdout="\n".join(dates) + "\n", returncode=0)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_git_command

    # Run main
    sys.argv = ["learning-ages.py", str(learnings_file)]
    learning_ages.main()

    # Verify output
    captured = capsys.readouterr()
    output = captured.out

    # Check report structure
    assert "# Learning Ages Report" in output
    assert "**File lines:** 14" in output
    assert "**Last consolidation:** 10 active days ago" in output
    assert "**Total entries:** 2" in output
    assert "**Entries ≥7 active days:** 1" in output  # Only "Old learning" with 15 days is ≥7
    assert "## Entries by Age" in output

    # Check entries sorted by age (descending)
    lines = output.splitlines()
    entry_lines = [l for l in lines if l.startswith("- **")]
    assert len(entry_lines) == 2
    # Older entry should be first (more active days)
    assert "Old learning" in entry_lines[0]
    assert "Recent learning" in entry_lines[1]
    assert "15 days" in entry_lines[0]
    assert "5 days" in entry_lines[1]


@patch('subprocess.run')
def test_main_no_consolidation_message(mock_run, tmp_path, capsys):
    """Display 'N/A' message when no prior consolidation detected."""
    learnings_file = tmp_path / "learnings.md"
    learnings_file.write_text(
        "# Learnings\n" + "\n" * 9 + "## First learning\n"
    )

    def mock_git_command(cmd, **kwargs):
        if "blame" in cmd:
            return MagicMock(stdout="committer-time 1704067200\n", returncode=0)
        elif "log" in cmd and "-p" in cmd:
            # No removed headers
            return MagicMock(stdout="commit abc\nDate: Mon Jan 1 10:00:00 2024 -0800\n+## New\n", returncode=0)
        elif "log" in cmd:
            return MagicMock(stdout="2024-01-01\n", returncode=0)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_git_command

    sys.argv = ["learning-ages.py", str(learnings_file)]
    learning_ages.main()

    captured = capsys.readouterr()
    assert "**Last consolidation:** N/A (no prior consolidation detected)" in captured.out
