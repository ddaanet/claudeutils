# Cycle 2.1

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.1: Basic YAML Configuration Loading

**Objective**: Implement load_config() with basic YAML parsing (happy path only)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Implementation Hint**: Happy path only - no error handling, no validation

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

**Implementation**: Add load_config() function with minimal YAML parsing

**Changes:**
- File: src/claudeutils/compose.py
  Action: Add imports and load_config() function

**Behavior**:
- Read YAML file from config_path
- Parse YAML into Python dict
- Return parsed configuration
- Must pass test assertions: basic structure, optional fields (title, separator), defaults (adjust_headers), YAML anchors

**Hint**: Use yaml.safe_load() with UTF-8 encoding. No error handling in this cycle.
**Implementation Hint**: Happy path only - no validation, no error handling

**Verify GREEN**: pytest tests/test_compose.py::test_load_config -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-2-1-notes.md

---
