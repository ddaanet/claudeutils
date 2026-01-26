# Cycle 3.4

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.4: Validation Modes

**Objective**: Validate strict vs warn mode behavior for missing fragments
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Validation modes (4 tests)

```python
# tests/test_compose.py


def test_compose_strict_mode_raises_on_missing_fragment(tmp_path):
    """Raise FileNotFoundError in strict mode for missing fragment."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Content\n")
    frag2 = tmp_path / "missing.md"  # Does not exist

    output = tmp_path / "output.md"

    with pytest.raises(FileNotFoundError, match="Fragment not found"):
        compose(fragments=[frag1, frag2], output=output, validate_mode="strict")


def test_compose_strict_mode_is_default(tmp_path):
    """Strict mode is default validation mode."""
    missing = tmp_path / "missing.md"
    output = tmp_path / "output.md"

    with pytest.raises(FileNotFoundError):
        compose(fragments=[missing], output=output)


def test_compose_warn_mode_skips_missing_fragment(tmp_path, capsys):
    """Skip missing fragments in warn mode with warning."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Content 1\n")
    frag2 = tmp_path / "missing.md"  # Does not exist
    frag3 = tmp_path / "exists2.md"
    frag3.write_text("Content 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2, frag3], output=output, validate_mode="warn")

    # Output should contain only existing fragments
    result = output.read_text()
    assert "Content 1\n" in result
    assert "Content 2\n" in result

    # Warning should be printed to stderr
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "missing.md" in captured.err


def test_compose_warn_mode_creates_partial_output(tmp_path):
    """Create output with available fragments in warn mode."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Available content\n")
    frag2 = tmp_path / "missing.md"  # Does not exist

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output, validate_mode="warn")

    assert output.exists()
    assert "Available content\n" in output.read_text()
```

**Expected failure:**
```
May pass - implementation supports this
```

**Verify RED**: pytest tests/test_compose.py::test_compose_strict_mode -v
- Tests should pass (feature implemented)

---

**GREEN Phase:**

**Implementation**: Already implemented in Cycle 3.1

**Verify GREEN**: pytest tests/test_compose.py::test_compose_warn_mode -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-4-notes.md

---
