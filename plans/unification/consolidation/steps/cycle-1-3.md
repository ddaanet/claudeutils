# Cycle 1.3

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.3: Content Normalization Utilities

**Objective**: Implement normalize_newlines() and format_separator() utilities
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Content normalization (5 tests)

```python
# tests/test_compose.py
from claudeutils.compose import normalize_newlines, format_separator


def test_normalize_newlines_adds_newline():
    """Add newline if missing."""
    assert normalize_newlines("text") == "text\n"


def test_normalize_newlines_preserves_single_newline():
    """Don't add extra newline if already present."""
    assert normalize_newlines("text\n") == "text\n"


def test_format_separator_default_horizontal_rule():
    """Default separator is horizontal rule."""
    assert format_separator("---") == "\n---\n\n"


def test_format_separator_blank():
    """Blank separator is double newline."""
    assert format_separator("blank") == "\n\n"


def test_format_separator_none():
    """None separator is empty string."""
    assert format_separator("none") == ""
```

**Expected failure:**
```
ImportError: cannot import name 'normalize_newlines' from 'claudeutils.compose'
```

**Why it fails**: Functions don't exist yet

**Verify RED**: pytest tests/test_compose.py::test_normalize_newlines_adds_newline -v
- Must fail with ImportError

---

**GREEN Phase:**

**Implementation**: Add normalize_newlines() and format_separator() functions

**Changes:**
- File: src/claudeutils/compose.py
  Action: Add both utility functions

**Behavior**:

**normalize_newlines()**:
- Ensure content ends with exactly one newline
- If content already ends with newline, return unchanged
- If content is empty or None, return unchanged
- Otherwise append single newline
- Must pass: adds newline, preserves existing, handles empty, idempotent

**format_separator()**:
- Return formatted separator string based on style parameter
- Support styles: "---" (default), "blank", "none"
- "---" returns horizontal rule with blank lines
- "blank" returns blank lines only
- "none" returns empty string
- Raise ValueError for unknown styles
- Must pass: all style tests, default, unknown style error

**Hint**: Simple string operations and conditionals. Tests define expected output formats.

**Verify GREEN**: pytest tests/test_compose.py::test_normalize_newlines -v
- All 5 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-1-3-notes.md

---
