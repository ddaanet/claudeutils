# Cycle 1.2

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.2: Header Level Increase

**Objective**: Implement increase_header_levels() to adjust markdown headers
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Header level increase (4 tests)

```python
# tests/test_compose.py
from claudeutils.compose import increase_header_levels


def test_increase_header_levels_by_one():
    """Increase all headers by 1 level."""
    content = "# Title\n## Section\n### Subsection"
    result = increase_header_levels(content, 1)
    assert result == "## Title\n### Section\n#### Subsection"


def test_increase_header_levels_by_two():
    """Increase all headers by 2 levels."""
    content = "# Title\n## Section"
    result = increase_header_levels(content, 2)
    assert result == "### Title\n#### Section"


def test_increase_header_levels_preserves_non_headers():
    """Don't modify non-header lines."""
    content = "# Header\nNormal text\n## Section"
    result = increase_header_levels(content, 1)
    assert result == "## Header\nNormal text\n### Section"


def test_increase_header_levels_default_is_one():
    """Default levels parameter is 1."""
    content = "# Title"
    result = increase_header_levels(content)
    assert result == "## Title"
```

**Expected failure:**
```
ImportError: cannot import name 'increase_header_levels' from 'claudeutils.compose'
```

**Why it fails**: Function doesn't exist yet

**Verify RED**: pytest tests/test_compose.py::test_increase_header_levels_by_one -v
- Must fail with ImportError
- If passes, STOP

---

**GREEN Phase:**

**Implementation**: Add increase_header_levels() function to compose.py

**Changes:**
- File: src/claudeutils/compose.py
  Action: Add increase_header_levels() function

**Behavior**:
- Process multi-line markdown content
- Find all header lines (lines starting with #)
- Add specified number of hash marks to each header
- Preserve non-header lines unchanged
- Default levels=1
- Must pass tests: increase by 1, increase by 2, no headers, custom levels

**Hint**: Use regex with MULTILINE flag to process multiple lines. Consider re.sub() for replacement. Pattern should match start-of-line hashes.

**Verify GREEN**: pytest tests/test_compose.py::test_increase_header_levels -v
- All 4 tests must pass

**Verify no regression**: pytest
- All existing tests pass

---

**STOP IMMEDIATELY if:**
- Test passes on first run
- Test failure doesn't match expected
- Regression failure

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-1-2-notes.md

---
