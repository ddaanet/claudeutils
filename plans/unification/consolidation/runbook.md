---
name: composition-api
type: tdd
model: haiku
---

# Composition API TDD Runbook

**Context**: Unified markdown composition engine supporting CLAUDE.md generation and role file assembly via YAML config and CLI interface
**Design**: plans/unification/consolidation/design/compose-api.md
**Status**: Draft
**Created**: 2026-01-24

## Weak Orchestrator Metadata

**Total Steps**: 11
**Execution Model**: All cycles: Haiku (TDD execution)
**Step Dependencies**: Sequential
**Error Escalation**: Haiku → User on stop conditions/regression
**Report Locations**: plans/unification/consolidation/reports/
**Success Criteria**: All cycles GREEN, no regressions
**Prerequisites**: PyYAML>=6.0, click>=8.0.0 dependencies added to pyproject.toml

## Common Context

**Key Design Decisions:**

1. **Click framework for CLI** - Declarative commands, built-in help, exit code handling
2. **Config file first** - YAML as primary interface (reusable, version-controllable, explicit)
3. **YAML over JSON** - Human-readable, comments, YAML anchors for path deduplication
4. **UTF-8 encoding only** - Standard for markdown, simplifies implementation
5. **Strict and warn modes** - Fail-fast vs graceful handling of missing fragments
6. **Header adjustment** - Conditional feature for hierarchical composition

**TDD Protocol:**

Strict RED-GREEN-REFACTOR:
1. RED: Write failing test
2. Verify RED (test must fail with expected message)
3. GREEN: Minimal implementation
4. Verify GREEN (test passes)
5. Verify Regression (all existing tests pass)
6. REFACTOR (optional, maintain GREEN)

**Batching Strategy:**

Tests grouped in batches of 3-5 related assertions to maintain RED/GREEN discipline while avoiding excessive granularity. Each batch tests a coherent feature area.

**Project Paths:**

- Source: `src/claudeutils/compose.py` (new file)
- CLI: `src/claudeutils/cli.py` (modify existing - add compose command)
- Tests: `tests/test_compose.py` (new file), `tests/test_cli_compose.py` (new file)
- Config: `pyproject.toml` (add PyYAML, click dependencies)

**Conventions:**

- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Write notes to plans/unification/consolidation/reports/cycle-{X}-{Y}-notes.md
- Mock patching: patch where object is used, not defined
- Exit codes: 1=config error, 2=fragment error, 3=output error, 4=arg error

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

```python
import re
from pathlib import Path


def get_header_level(line: str) -> int | None:
    """
    Detect markdown header level from a line.

    Args:
        line: Single line of text.

    Returns:
        Header level (1-6) if line is header, None otherwise.
    """
    match = re.match(r'^(#+)\s', line)
    return len(match.group(1)) if match else None
```

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

```python
def increase_header_levels(content: str, levels: int = 1) -> str:
    """
    Increase markdown header levels by specified amount.

    Args:
        content: Markdown content string.
        levels: Number of header levels to increase (default 1).

    Returns:
        Content with adjusted headers.
    """
    pattern = r'^(#{1,})\s'
    replacement = r'\1' + '#' * levels + ' '
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)
```

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

```python
def normalize_newlines(content: str) -> str:
    """
    Ensure content ends with single newline.

    Args:
        content: String content.

    Returns:
        Content with single trailing newline.
    """
    if not content or content.endswith('\n'):
        return content
    return content + '\n'


def format_separator(style: str = "---") -> str:
    """
    Format fragment separator based on style.

    Args:
        style: Separator style ("---", "blank", "none").

    Returns:
        Separator string ready for output.
    """
    if style == "---":
        return "\n---\n\n"
    elif style == "blank":
        return "\n\n"
    elif style == "none":
        return ""
    else:
        raise ValueError(f"Unknown separator style: {style}")
```

**Verify GREEN**: pytest tests/test_compose.py::test_normalize_newlines -v
- All 5 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-1-3-notes.md

---

## Cycle 2.1: Basic YAML Configuration Loading

**Objective**: Implement load_config() with basic YAML parsing and validation
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Basic config loading (4 tests)

```python
# tests/test_compose.py
from pathlib import Path
from claudeutils.compose import load_config


def test_load_config_basic(tmp_path):
    """Load valid YAML configuration."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
fragments:
  - file1.md
  - file2.md
output: result.md
""")

    config = load_config(config_file)
    assert config['fragments'] == ['file1.md', 'file2.md']
    assert config['output'] == 'result.md'


def test_load_config_with_optional_fields(tmp_path):
    """Load config with optional fields."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
fragments:
  - file1.md
output: result.md
title: "My Document"
adjust_headers: true
separator: "blank"
validate_mode: "warn"
""")

    config = load_config(config_file)
    assert config['title'] == 'My Document'
    assert config['adjust_headers'] is True
    assert config['separator'] == 'blank'
    assert config['validate_mode'] == 'warn'


def test_load_config_applies_defaults(tmp_path):
    """Apply defaults for missing optional fields."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
fragments:
  - file1.md
output: result.md
""")

    config = load_config(config_file)
    assert config.get('title') is None
    assert config.get('adjust_headers', False) is False
    assert config.get('separator', '---') == '---'
    assert config.get('validate_mode', 'strict') == 'strict'


def test_load_config_with_sources_anchors(tmp_path):
    """Support YAML anchors for path deduplication."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
sources:
  core: &core agent-core/fragments

fragments:
  - *core/file1.md
  - *core/file2.md
output: result.md
""")

    config = load_config(config_file)
    # YAML should expand anchors automatically
    assert 'agent-core/fragments/file1.md' in config['fragments'][0]
```

**Expected failure:**
```
ImportError: cannot import name 'load_config' from 'claudeutils.compose'
```

**Why it fails**: Function doesn't exist yet

**Verify RED**: pytest tests/test_compose.py::test_load_config_basic -v
- Must fail with ImportError

---

**GREEN Phase:**

**Implementation**: Add load_config() function with YAML parsing

**Changes:**
- File: src/claudeutils/compose.py
  Action: Add imports and load_config() function

```python
import yaml


def load_config(config_path: Path) -> dict:
    """
    Load and parse YAML composition configuration file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Parsed configuration dict.

    Raises:
        FileNotFoundError: If config file does not exist
        yaml.YAMLError: If config is malformed YAML
        ValueError: If config missing required fields
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML: {e}")

    # Validate required fields
    if not config:
        raise ValueError("Empty configuration file")
    if 'fragments' not in config:
        raise ValueError("Missing required field: fragments")
    if 'output' not in config:
        raise ValueError("Missing required field: output")
    if not config['fragments']:
        raise ValueError("fragments list cannot be empty")

    return config
```

**Verify GREEN**: pytest tests/test_compose.py::test_load_config -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-2-1-notes.md

---

## Cycle 2.2: Configuration Error Handling

**Objective**: Validate error cases for load_config()
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Configuration validation errors (4 tests)

```python
# tests/test_compose.py
import pytest
import yaml


def test_load_config_missing_file():
    """Raise FileNotFoundError for missing config file."""
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_config(Path("nonexistent.yaml"))


def test_load_config_invalid_yaml(tmp_path):
    """Raise YAMLError for malformed YAML."""
    config_file = tmp_path / "bad.yaml"
    config_file.write_text("invalid: yaml: : syntax")

    with pytest.raises(yaml.YAMLError):
        load_config(config_file)


def test_load_config_missing_fragments_field(tmp_path):
    """Raise ValueError for missing fragments field."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("output: result.md")

    with pytest.raises(ValueError, match="Missing required field: fragments"):
        load_config(config_file)


def test_load_config_missing_output_field(tmp_path):
    """Raise ValueError for missing output field."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("fragments:\n  - file1.md")

    with pytest.raises(ValueError, match="Missing required field: output"):
        load_config(config_file)
```

**Expected failure:**
```
FAILED - assert not raised
```

**Why it fails**: Error handling not implemented yet (tests expect exceptions)

**Verify RED**: pytest tests/test_compose.py::test_load_config_missing_file -v
- Must fail (exception not raised)

---

**GREEN Phase:**

**Implementation**: Error handling already added in Cycle 2.1, tests should pass

**Verify GREEN**: pytest tests/test_compose.py::test_load_config_missing -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-2-2-notes.md

---

## Cycle 3.1: Basic Fragment Composition

**Objective**: Implement compose() function with basic fragment assembly
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

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

**Implementation**: Add compose() function with basic composition logic

**Changes:**
- File: src/claudeutils/compose.py
  Action: Add compose() function

```python
def compose(
    fragments: list[Path] | list[str],
    output: Path | str,
    title: str | None = None,
    adjust_headers: bool = False,
    separator: str = "---",
    validate_mode: str = "strict",
) -> None:
    """
    Compose multiple markdown fragments into a single output file.

    Args:
        fragments: List of fragment file paths.
        output: Path to output file.
        title: Optional markdown header to prepend.
        adjust_headers: If True, increase all fragment headers by 1 level.
        separator: Fragment separator style ("---", "blank", "none").
        validate_mode: Error handling strategy ("strict", "warn").

    Raises:
        FileNotFoundError: If validate_mode="strict" and fragment missing
        PermissionError: If output directory cannot be created
        IOError: If output file cannot be written
    """
    # Convert to Path objects
    output_path = Path(output) if isinstance(output, str) else output
    fragment_paths = [Path(f) if isinstance(f, str) else f for f in fragments]

    # Validate fragments in strict mode
    if validate_mode == "strict":
        missing = [p for p in fragment_paths if not p.exists()]
        if missing:
            raise FileNotFoundError(f"Fragment not found: {missing[0]}")

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Compose fragments
    with open(output_path, 'w', encoding='utf-8') as out:
        # Write title if provided
        if title:
            out.write(f"# {title}\n\n")

        # Process each fragment
        for i, frag_path in enumerate(fragment_paths):
            # Skip if missing in warn mode
            if not frag_path.exists():
                if validate_mode == "warn":
                    import sys
                    print(f"WARNING: Skipping missing fragment: {frag_path}", file=sys.stderr)
                    continue

            # Read fragment
            content = frag_path.read_text(encoding='utf-8')

            # Apply transformations
            if adjust_headers:
                content = increase_header_levels(content, 1)

            content = normalize_newlines(content)

            # Write content
            out.write(content)

            # Write separator (except after last fragment)
            if i < len(fragment_paths) - 1:
                sep = format_separator(separator)
                out.write(sep)
```

**Verify GREEN**: pytest tests/test_compose.py::test_compose -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-1-notes.md

---

## Cycle 3.2: Title and Separator Options

**Objective**: Validate title injection and separator style options
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

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

**Implementation**: Implementation from Cycle 3.1 should already support these features

**Verify GREEN**: pytest tests/test_compose.py::test_compose_separator -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-2-notes.md

---

## Cycle 3.3: Header Adjustment Integration

**Objective**: Validate adjust_headers parameter integration
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

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

**Implementation**: Already implemented in Cycle 3.1

**Verify GREEN**: pytest tests/test_compose.py::test_compose_adjust_headers -v
- All 3 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-3-3-notes.md

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

## Cycle 4.1: CLI Basic Command

**Objective**: Implement compose CLI command with basic functionality
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: Basic CLI command (3 tests)

```python
# tests/test_cli_compose.py
from click.testing import CliRunner
from pathlib import Path
from claudeutils.cli import main


def test_cli_compose_basic(tmp_path):
    """Compose from config file via CLI."""
    # Create fragments
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("# Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("# Part 2\n")

    # Create config
    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag1}
  - {frag2}
output: {tmp_path / 'output.md'}
""")

    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config)])

    assert result.exit_code == 0
    assert (tmp_path / 'output.md').exists()


def test_cli_compose_shows_help():
    """Show help message for compose command."""
    runner = CliRunner()
    result = runner.invoke(main, ['compose', '--help'])

    assert result.exit_code == 0
    assert 'Compose markdown from YAML configuration' in result.output


def test_cli_compose_missing_config_file():
    """Exit with code 4 for missing config file."""
    runner = CliRunner()
    result = runner.invoke(main, ['compose', 'nonexistent.yaml'])

    assert result.exit_code == 4
    assert 'Error' in result.output
```

**Expected failure:**
```
AttributeError: 'Group' object has no attribute 'compose'
```

**Why it fails**: compose command not added to CLI yet

**Verify RED**: pytest tests/test_cli_compose.py::test_cli_compose_basic -v
- Must fail

---

**GREEN Phase:**

**Implementation**: Add compose command to CLI

**Changes:**
- File: src/claudeutils/cli.py
  Action: Add compose subcommand to main CLI group

```python
import click
from pathlib import Path
from claudeutils.compose import compose, load_config


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Override output path from config')
@click.option('--validate', '-v', type=click.Choice(['strict', 'warn']),
              default='strict', help='Validation mode')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show plan without writing')
def compose_cmd(config_file, output, validate, verbose, dry_run):
    """Compose markdown from YAML configuration."""
    try:
        config_path = Path(config_file)
        config = load_config(config_path)

        if verbose:
            click.echo(f"Loading config: {config_file}")

        if dry_run:
            click.echo(f"Dry-run: Would compose to {config.get('output')}")
            return

        output_path = Path(output) if output else Path(config['output'])
        fragments = [Path(f) for f in config['fragments']]

        compose(
            fragments=fragments,
            output=output_path,
            title=config.get('title'),
            adjust_headers=config.get('adjust_headers', False),
            separator=config.get('separator', '---'),
            validate_mode=validate,
        )

        if verbose:
            click.echo(f"Composed {len(fragments)} fragments to {output_path}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(4)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(3)
```

**Verify GREEN**: pytest tests/test_cli_compose.py::test_cli_compose -v
- All 3 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-4-1-notes.md

---

## Cycle 4.2: CLI Options and Overrides

**Objective**: Implement CLI option overrides (--output, --validate, --verbose, --dry-run)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: CLI options (4 tests)

```python
# tests/test_cli_compose.py


def test_cli_compose_output_override(tmp_path):
    """Override output path with --output option."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag}
output: {tmp_path / 'default.md'}
""")

    custom_output = tmp_path / "custom.md"
    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config), '--output', str(custom_output)])

    assert result.exit_code == 0
    assert custom_output.exists()
    assert not (tmp_path / 'default.md').exists()


def test_cli_compose_validate_warn(tmp_path):
    """Use warn validation mode with --validate option."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag1}
  - {tmp_path / 'missing.md'}
output: {tmp_path / 'output.md'}
""")

    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config), '--validate', 'warn'])

    assert result.exit_code == 0
    assert 'WARNING' in result.output or 'WARNING' in result.stderr_bytes.decode()


def test_cli_compose_verbose(tmp_path):
    """Show verbose output with --verbose flag."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag}
output: {tmp_path / 'output.md'}
""")

    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config), '--verbose'])

    assert result.exit_code == 0
    assert 'Loading config' in result.output


def test_cli_compose_dry_run(tmp_path):
    """Show plan without writing with --dry-run flag."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag}
output: {tmp_path / 'output.md'}
""")

    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config), '--dry-run'])

    assert result.exit_code == 0
    assert 'Dry-run' in result.output
    assert not (tmp_path / 'output.md').exists()
```

**Expected failure:**
```
May pass - implementation supports this
```

**Verify RED**: pytest tests/test_cli_compose.py::test_cli_compose_output_override -v

---

**GREEN Phase:**

**Implementation**: Already implemented in Cycle 4.1

**Verify GREEN**: pytest tests/test_cli_compose.py::test_cli_compose_verbose -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-4-2-notes.md

---

## Cycle 4.3: CLI Error Handling and Exit Codes

**Objective**: Validate CLI error handling with correct exit codes
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test Batch**: CLI error handling (4 tests)

```python
# tests/test_cli_compose.py


def test_cli_compose_config_error_exit_code(tmp_path):
    """Exit code 1 for configuration errors."""
    config = tmp_path / "bad.yaml"
    config.write_text("output: missing_fragments_field.md")

    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config)])

    assert result.exit_code == 1
    assert 'Configuration error' in result.output


def test_cli_compose_fragment_error_exit_code(tmp_path):
    """Exit code 2 for missing fragments in strict mode."""
    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {tmp_path / 'missing.md'}
output: {tmp_path / 'output.md'}
""")

    runner = CliRunner()
    result = runner.invoke(main, ['compose', str(config)])

    assert result.exit_code == 2


def test_cli_compose_invalid_config_file_exit_code():
    """Exit code 4 for invalid config file path."""
    runner = CliRunner()
    result = runner.invoke(main, ['compose', 'nonexistent.yaml'])

    # Click automatically validates exists=True
    assert result.exit_code in (2, 4)  # Click may use 2 for usage errors


def test_cli_compose_error_message_to_stderr(tmp_path):
    """Print error messages to stderr."""
    config = tmp_path / "bad.yaml"
    config.write_text("invalid: config")

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, ['compose', str(config)])

    assert result.exit_code != 0
    # Error output should be present
    assert 'error' in result.output.lower() or 'Error' in result.output
```

**Expected failure:**
```
May pass - implementation supports this
```

**Verify RED**: pytest tests/test_cli_compose.py::test_cli_compose_config_error -v

---

**GREEN Phase:**

**Implementation**: Already implemented in Cycle 4.1

**Verify GREEN**: pytest tests/test_cli_compose.py::test_cli_compose_error -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-4-3-notes.md

---

## Design Decisions

**From design document (plans/unification/consolidation/design/compose-api.md):**

1. **Click framework for CLI**
   - Choice: Use Click for command-line interface
   - Rationale: Declarative command definition, built-in help and version support, exit code handling, type conversion (Path, Choice)

2. **Config file first approach**
   - Choice: YAML configuration as primary interface with CLI arg overrides
   - Rationale: Reusable across invocations, version-controllable, explicit over implicit, supports complex setups without CLI arg explosion

3. **YAML over JSON**
   - Choice: YAML for configuration format
   - Rationale: Human-readable and editable, supports comments, YAML anchors for path deduplication, standard in Python ecosystem

4. **UTF-8 encoding only**
   - Choice: Only support UTF-8 encoding for markdown files
   - Rationale: Simplifies implementation, standard for markdown documents, adequate for target use cases

5. **Strict and warn validation modes**
   - Choice: Two validation modes for missing fragments
   - Rationale: Fail-fast (strict) for CI/CD, graceful degradation (warn) for development

6. **Header adjustment as optional feature**
   - Choice: Conditional header level adjustment
   - Rationale: Needed for hierarchical composition (role files) but not for flat composition (CLAUDE.md)

7. **Pattern consolidation**
   - Choice: Combine tuick's programmatic API with emojipack's YAML configuration
   - Rationale: Balances simplicity (config-driven) with flexibility (CLI overrides), supports both use cases

8. **Exit codes**
   - Choice: Distinct exit codes for different error types
   - Rationale: Enables automated error handling in scripts and CI/CD pipelines
   - Mapping: 0=success, 1=config error, 2=fragment error, 3=output error, 4=arg error

---

## Dependencies

**Before**:
- PyYAML>=6.0 added to pyproject.toml dependencies
- click>=8.0.0 added to pyproject.toml dependencies

**After**:
- Composition API implemented with full test coverage
- All 11 cycles verified GREEN with no regressions
- CLI command available via `claudeutils compose`
- Ready for integration with build systems (justfile, Makefile)
