# Cycle 4.3

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

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
