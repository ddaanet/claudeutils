# Cycle 3.3

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.3: Header Adjustment Integration

**Objective**: Add adjust_headers parameter to compose()
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Implementation Hint**: Add adjust_headers parameter, apply increase_header_levels when enabled

**Implementation:**

**RED Phase:**

**Test Batch**: Header adjustment (3 tests)

```python
# tests/test_compose.py


def test_compose_adjust_headers_increases_levels(tmp_path):
    """Increase all header levels when adjust_headers=True."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Title\n## Section\n### Subsection\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output, adjust_headers=True)

    result = output.read_text()
    assert "## Title\n" in result
    assert "### Section\n" in result
    assert "#### Subsection\n" in result


def test_compose_adjust_headers_disabled_by_default(tmp_path):
    """Don't adjust headers by default."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Title\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output)

    result = output.read_text()
    assert "# Title\n" in result


def test_compose_adjust_headers_with_title(tmp_path):
    """Adjust headers with title creates proper hierarchy."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Purpose\n## Details\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output, title="Document", adjust_headers=True)

    result = output.read_text()
    assert result.startswith("# Document\n\n")
    assert "## Purpose\n" in result
    assert "### Details\n" in result
```

**Expected failure:**
```
May pass - implementation already supports this
```

**Verify RED**: pytest tests/test_compose.py::test_compose_adjust_headers -v
- Tests should pass (feature implemented in 3.1)

---

**GREEN Phase:**

**Implementation**: Add adjust_headers parameter

**Changes:**
- File: src/claudeutils/compose.py
  Action: Update compose() to add adjust_headers parameter

```python
def compose(
    fragments: list[Path] | list[str],
    output: Path | str,
    title: str | None = None,
    adjust_headers: bool = False,
    separator: str = "---",
) -> None:
    """
    Compose multiple markdown fragments into a single output file.

    Args:
        fragments: List of fragment file paths.
        output: Path to output file.
        title: Optional markdown header to prepend.
        adjust_headers: If True, increase all fragment headers by 1 level.
        separator: Fragment separator style ("---", "blank", "none").
    """
    output_path = Path(output) if isinstance(output, str) else output
    fragment_paths = [Path(f) if isinstance(f, str) else f for f in fragments]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as out:
        if title:
            out.write(f"# {title}\n\n")

        for i, frag_path in enumerate(fragment_paths):
            content = frag_path.read_text(encoding='utf-8')

            # Apply header adjustment if enabled
            if adjust_headers:
                content = increase_header_levels(content, 1)

            content = normalize_newlines(content)
            out.write(content)

            if i < len(fragment_paths) - 1:
                sep = format_separator(separator)
                out.write(sep)
```

**Verify GREEN**: pytest tests/test_compose.py::test_compose_adjust_headers -v
- All 3 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-3-notes.md

---
