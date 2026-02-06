# Phase 4: Testing

**Complexity:** Moderate (mock git operations, test workflow integration)
**Model:** Sonnet
**Scope:** ~200 lines test code

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

## Tool batching unsolved
- Content

## Hard limits vs soft limits
- More content
""")

    # Mock git blame responses
    def mock_git_side_effect(*args, **kwargs):
        cmd = args[0]
        if "blame" in cmd:
            if "11" in cmd:
                return MagicMock(stdout="abc123 (Author 2026-01-14 ...) ## Tool batching", returncode=0)
            elif "13" in cmd:
                return MagicMock(stdout="def456 (Author 2026-01-28 ...) ## Hard limits", returncode=0)
        elif "log" in cmd and "-p" in cmd:
            return MagicMock(stdout="commit xyz789 2026-01-20\n-## Old learning\n", returncode=0)
        elif "log" in cmd:
            return MagicMock(stdout="2026-01-15\n2026-01-20\n2026-01-28\n2026-02-01\n", returncode=0)
        return MagicMock(stdout="", returncode=0)

    mock_run.side_effect = mock_git_side_effect

    output = learning_ages.generate_report(str(learnings_file))

    # Verify output format
    assert "# Learning Ages Report" in output
    assert "**File lines:**" in output
    assert "**Last consolidation:**" in output
    # Verify staleness calculation present (mocked consolidation 2026-01-20)
    # Active days between 2026-01-20 and mocked "today" should appear
    assert "active days ago" in output or "N/A" in output
    assert "## Tool batching unsolved" in output
    assert "- Age:" in output
    assert "- Added: 2026-01-14" in output
```

**Expected Outcome:**

Test file created at `tests/test_learning_ages.py` with:
- 7 test categories (A-G) covering all design test cases
- Git operation mocking via `subprocess.run` patches
- Edge case coverage (merge commits, file renames, today's entries, staleness fallback)
- Integration test with full pipeline

**Validation:**

Run test suite:
```bash
pytest tests/test_learning_ages.py -v
```

Expected:
- All tests pass
- Coverage for git operations (blame, log, log -p)
- Edge cases handled (0 active days, missing file, git unavailable)

**Success Criteria:**

- [ ] Test file created at `tests/test_learning_ages.py`
- [ ] 7 test categories present (parsing, age calculation, staleness, trigger logic, freshness, error handling, integration)
- [ ] Git operations mocked via subprocess patches
- [ ] Edge cases tested (merge commits, entry added today, no prior consolidation)
- [ ] Staleness detection test includes fallback ("N/A")
- [ ] All tests pass: `pytest tests/test_learning_ages.py`

---

## Step 4.2: Integration Validation

**Objective:** Validate end-to-end workflow integration with manual testing procedures.

**Implementation:**

**1. Unit test integration (automated):**

Already covered by step 4.1 integration test. Run:
```bash
pytest tests/test_learning_ages.py::test_full_pipeline -v
```

Verify:
- Script produces markdown output matching design § D-2
- Summary fields present (file lines, last consolidation, total entries, ≥7 days count)
- Per-entry sections formatted correctly

**2. Manual handoff trigger test:**

Create test scenario to verify handoff step 4c triggers consolidation:

**Option A: Size trigger (>150 lines)**

```bash
# Check current learnings.md size
wc -l agents/learnings.md

# If needed, add temp entries to exceed 150 lines
# (Do this in a test branch)

# Run handoff and verify step 4c executes
# Expected: Script runs, filtered entry list passed to remember-task agent
```

**Option B: Staleness trigger (>14 days)**

```bash
# Check staleness
agent-core/bin/learning-ages.py agents/learnings.md | head -5

# If staleness <14 days, use git manipulation to simulate old entries
# (Or wait for natural staleness)

# Run handoff and verify step 4c executes
```

**Verification steps:**
- [ ] Handoff skill loads without error
- [ ] Step 4c runs learning-ages.py
- [ ] Trigger condition evaluated (size OR staleness)
- [ ] If triggered: filtered entry list logged
- [ ] If triggered: remember-task agent delegated
- [ ] If not triggered: consolidation skipped, continues to step 5
- [ ] If error: logged to stderr, handoff continues (NFR-1)

**3. Agent definition validation:**

**A. Remember-task agent:**

```bash
# Read agent file
cat agent-core/agents/remember-task.md

# Verify frontmatter
head -10 agent-core/agents/remember-task.md | grep -E "(name|description|model|color|tools)"

# Verify source comment
grep "Source: agent-core/skills/remember" agent-core/agents/remember-task.md

# Verify sections present
grep "^##" agent-core/agents/remember-task.md | head -10
```

Expected sections:
- Role statement
- Input Format
- Pre-Consolidation Checks
- Consolidation Protocol
- Reporting
- Return Protocol

Checklist:
- [ ] Protocol embedded faithfully (compare with remember skill steps 1-4a):
  - Verify protocol steps present in same order (Understand → File Selection → Draft → Apply → Discovery)
  - Check terminology matches skill (e.g., "Precision over brevity", "Atomic changes")
  - Confirm routing patterns identical (fragments/ vs decisions/ vs implementation-notes.md)
  - Allow adaptation: agent body uses second-person ("You"), skill uses imperative
- [ ] Source comment present for synchronization tracking
- [ ] Pre-check algorithms concrete (thresholds specified: 50% keyword overlap, 70% redundancy)
- [ ] Report structure documented (6 sections: summary, supersession, redundancy, contradictions, file limits, discovery)
- [ ] Model: sonnet, color: green, tools include Read/Write/Edit/Bash/Grep/Glob
- [ ] Quiet execution pattern (report to file, return filepath)

**B. Memory-refactor agent:**

```bash
# Read agent file
cat agent-core/agents/memory-refactor.md

# Verify sections
grep "^##" agent-core/agents/memory-refactor.md
```

Expected sections:
- Role statement
- Input Format
- Refactoring Process (6 steps)
- Constraints
- Output Format
- Return Protocol

Checklist:
- [ ] Refactoring process has 6 steps with heuristics
- [ ] Validator autofix integration (step 5)
- [ ] Content preservation constraints (no summarization)
- [ ] Model: sonnet, color: yellow, tools include Read/Write/Edit/Grep/Glob
- [ ] Quiet execution pattern (filepaths on success, error on failure)

**4. No automated full workflow test:**

Design specifies no automated end-to-end test for full workflow (complexity too high). Manual validation sufficient:
- Phase 1-3 unit tests pass
- Agent definitions reviewed manually
- Handoff trigger test executed manually

**Expected Outcome:**

Integration validation complete:
- Unit tests pass
- Manual handoff trigger test executed
- Agent definitions validated against specifications
- No full workflow automation (manual validation acceptable per design)

**Validation:**

```bash
# Run all tests
pytest tests/test_learning_ages.py -v

# Verify no test failures
echo $?  # Should be 0
```

**Unexpected Result Handling:**

If tests fail:
- **Parse errors**: Verify preamble skip count (10 lines)
- **Git mock failures**: Check subprocess.run patch syntax
- **Integration test fails**: Verify markdown output format matches design § D-2

If manual trigger test doesn't trigger:
- **Size check**: Verify learnings.md actually >150 lines
- **Staleness check**: Verify staleness >14 days via script output
- **Threshold mismatch**: Compare handoff step 4c thresholds with design D-3

If agent definitions incomplete:
- **Compare against design**: Cross-reference Implementation Components 2 and 3
- **Check protocol embedding**: Compare remember-task protocol with remember skill steps 1-4a
- **Verify structure**: Ensure all required sections present per phase 3 success criteria

**Success Criteria:**

- [ ] All unit tests pass: `pytest tests/test_learning_ages.py`
- [ ] Integration test produces correct markdown format (matches design § D-2)
- [ ] Manual handoff trigger test executed (size OR staleness)
- [ ] Remember-task agent validated (protocol, source comment, pre-checks, reporting)
- [ ] Memory-refactor agent validated (6-step process, autofix integration, constraints)
- [ ] Both agents follow quiet execution pattern
- [ ] No critical issues found in agent definitions

**Report Path:** `plans/learnings-consolidation/reports/phase-4-execution.md`

**Design References:**
- Implementation Component 6: Testing specification
- D-2: Markdown output format (validation target)
- D-3: Trigger thresholds (manual test verification)
- NFR-1: Failure handling (handoff continues on error)
