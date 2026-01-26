# Cycle 3.2

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.2: Title and Separator Options

**Objective**: Add title and separator parameters to compose()
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Implementation Hint**: Add title and separator parameters with defaults

**Implementation:**

**RED Phase:**

**Test Batch**: Title and separators (4 tests)

```python
# tests/test_compose.py


def test_compose_with_title(tmp_path):
    """Prepend title as h1 header."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output, title="My Document")

    result = output.read_text()
    assert result.startswith("# My Document\n\n")
    assert "Content\n" in result


def test_compose_separator_blank(tmp_path):
    """Use blank line separator."""
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("Part 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output, separator="blank")

    result = output.read_text()
    assert result == "Part 1\n\n\nPart 2\n"


def test_compose_separator_none(tmp_path):
    """Use no separator."""
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("Part 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output, separator="none")

    result = output.read_text()
    assert result == "Part 1\nPart 2\n"


def test_compose_no_title_by_default(tmp_path):
    """Don't add title if not provided."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Existing Header\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output)

    result = output.read_text()
    assert result.startswith("# Existing Header\n")
```

**Expected failure:**
```
AssertionError - tests fail because separator handling may need refinement
```

**Why it fails**: Implementation needs verification, tests validate behavior

**Verify RED**: pytest tests/test_compose.py::test_compose_with_title -v
- Should pass (implementation already supports this)

---

**GREEN Phase:**

**Implementation**: Add title and separator parameters

**Changes:**
- File: src/claudeutils/compose.py
  Action: Update compose() function signature and add title/separator handling

```python
def compose(
    fragments: list[Path] | list[str],
    output: Path | str,
    title: str | None = None,
    separator: str = "---",
) -> None:
    """
    Compose multiple markdown fragments into a single output file.

    Args:
        fragments: List of fragment file paths.
        output: Path to output file.
        title: Optional markdown header to prepend.
        separator: Fragment separator style ("---", "blank", "none").
    """
    output_path = Path(output) if isinstance(output, str) else output
    fragment_paths = [Path(f) if isinstance(f, str) else f for f in fragments]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as out:
        # Write title if provided
        if title:
            out.write(f"# {title}\n\n")

        for i, frag_path in enumerate(fragment_paths):
            content = frag_path.read_text(encoding='utf-8')
            content = normalize_newlines(content)
            out.write(content)

            if i < len(fragment_paths) - 1:
                sep = format_separator(separator)
                out.write(sep)
```

**Verify GREEN**: pytest tests/test_compose.py::test_compose_separator -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-2-notes.md

---
