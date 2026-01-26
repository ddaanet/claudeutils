# Cycle 1.1

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 1.1: Header Level Detection

**Objective**: Implement get_header_level() to detect markdown header levels
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Header level detection (4 tests)

```python
# tests/test_compose.py
from claudeutils.compose import get_header_level


def test_get_header_level_detects_h1():
    """Detect h1 header."""
    assert get_header_level("# Title") == 1


def test_get_header_level_detects_h3():
    """Detect h3 header."""
    assert get_header_level("### Subsection") == 3


def test_get_header_level_detects_h6():
    """Detect h6 header."""
    assert get_header_level("###### Deep") == 6


def test_get_header_level_returns_none_for_non_header():
    """Return None for non-header lines."""
    assert get_header_level("Not a header") is None
    assert get_header_level(" # Space before hash") is None
```

**Expected failure:**
```
ImportError: cannot import name 'get_header_level' from 'claudeutils.compose'
```

**Why it fails**: Module and function don't exist yet

**Verify RED**: Run pytest tests/test_compose.py::test_get_header_level_detects_h1
- Must fail with ImportError
- If passes, STOP - feature may exist

---

**GREEN Phase:**

**Implementation**: Create src/claudeutils/compose.py with minimal get_header_level()

**Changes:**
- File: src/claudeutils/compose.py
  Action: Create file with imports and get_header_level() function

**Behavior**:
- Parse line to detect hash marks at start
- Count consecutive hashes (1-6)
- Return count if valid header pattern, None otherwise
- Must handle space after hashes (e.g., "# Title" → 1, "### Section" → 3)
- Must return None for non-header lines

**Hint**: Use regex to match start-of-line hash pattern. Consider re.match() with pattern group extraction to count hashes.

**Verify GREEN**: pytest tests/test_compose.py::test_get_header_level -v
- All 4 tests must pass

**Verify no regression**: pytest
- All existing tests pass

---

**STOP IMMEDIATELY if:**
- Test passes on first run (expected RED failure)
- Test failure message doesn't match expected ImportError
- Any existing test breaks (regression failure)

**Actions when stopped:**
1. Document in plans/unification/consolidation/reports/cycle-1-1-notes.md
2. If test passes unexpectedly: Investigate, check if feature exists
3. If regression: STOP execution, report broken tests
4. If scope unclear: STOP, document ambiguity, request clarification

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/unification/consolidation/reports/cycle-1-1-notes.md

---
