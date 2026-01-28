# Cycle 2.2

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.2: Configuration Error Handling

**Objective**: Add error handling and validation to load_config()
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku
**Implementation Hint**: Add file existence check, YAML parsing errors, field validation

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

**Implementation**: Add error handling to load_config()

**Changes:**
- File: src/claudeutils/compose.py
  Action: Update load_config() to add validation and error handling

**Behavior**:
- Raise FileNotFoundError if config file doesn't exist
- Raise yaml.YAMLError if YAML is malformed
- Raise ValueError if required fields missing (fragments, output)
- Raise ValueError if config is empty
- Validate fragments list not empty
- Must match test exception patterns and error messages

**Hint**: Check file existence before reading. Catch yaml.YAMLError during parsing. Validate dict structure after loading.
**Implementation Hint**: Add file existence check, YAML parsing errors, field validation

**Verify GREEN**: pytest tests/test_compose.py::test_load_config_missing -v
- All 4 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-2-2-notes.md

---
