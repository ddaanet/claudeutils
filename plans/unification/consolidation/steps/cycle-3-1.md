# Cycle 3.1

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.1: Basic Fragment Composition

**Objective**: Implement compose() function with minimal fragment assembly (happy path only)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Implementation Hint**: Minimal compose - no title, no options, hardcoded separator "\n---\n\n"

**Implementation:**

**RED Phase:**

**Test Batch**: Basic composition (4 tests)

```python
# tests/test_compose.py
from claudeutils.compose import compose


def test_compose_single_fragment(tmp_path):
    """Compose single fragment to output."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Header\n\nContent\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output)

    assert output.exists()
    assert output.read_text() == "# Header\n\nContent\n"


def test_compose_multiple_fragments_with_separator(tmp_path):
    """Compose multiple fragments with default separator."""
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("# Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("# Part 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output)

    result = output.read_text()
    assert "# Part 1\n" in result
    assert "\n---\n\n" in result
    assert "# Part 2\n" in result


def test_compose_creates_output_directory(tmp_path):
    """Auto-create output parent directory."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    output = tmp_path / "nested" / "dir" / "output.md"
    compose(fragments=[frag], output=output)

    assert output.exists()
    assert output.parent.exists()


def test_compose_accepts_string_paths(tmp_path):
    """Accept string paths, not just Path objects."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    output = tmp_path / "output.md"
    compose(fragments=[str(frag)], output=str(output))

    assert output.exists()
```

**Expected failure:**
```
ImportError: cannot import name 'compose' from 'claudeutils.compose'
```

**Why it fails**: compose() function doesn't exist yet

**Verify RED**: pytest tests/test_compose.py::test_compose_single_fragment -v
- Must fail with ImportError

---

**GREEN Phase:**

**Implementation**: Add compose() function with minimal composition logic

**Changes:**
- File: src/claudeutils/compose.py
  Action: Add compose() function

**Behavior**:
- Accept fragments as list of Path or str
- Write composed output to output path
- Support single fragment (direct copy with normalization)
- Support multiple fragments (joined with separator)
- Auto-create output parent directories if needed
- Normalize newlines in all fragments
- Add separator between fragments (not after last)
- Must pass all 4 tests: single fragment, multiple fragments, path types, auto-create dirs

**Hint**: Convert strings to Path objects. Use Path.mkdir(parents=True, exist_ok=True) for directories. Hardcode separator "\n---\n\n" for now. Use normalize_newlines() utility.
**Implementation Hint**: Minimal compose - no title, no options, hardcoded separator "\n---\n\n"

**Verify GREEN**: pytest tests/test_compose.py::test_compose -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-1-notes.md

---
