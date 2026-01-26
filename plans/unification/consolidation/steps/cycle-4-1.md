# Cycle 4.1

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

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

**Behavior**:
- Add @main.command() decorator for compose subcommand
- Accept config_file as required argument (must exist)
- Support --output option to override config output path
- Support --validate option for mode (strict/warn, default strict)
- Support --verbose flag for detailed output
- Support --dry-run flag (show plan, don't write)
- Load config using load_config()
- Call compose() with config values
- Handle errors with appropriate exit codes (FileNotFoundError→4, ValueError→1, other→3)
- Must pass all 3 tests: basic compose, missing config, invalid YAML

**Hint**: Use @main.command() decorator. Use click.argument() for required parameters with type validation. Use click.option() for optional flags. Use click.echo() for output. Use SystemExit(code) for exit codes. Import compose and load_config from claudeutils.compose.

**Verify GREEN**: pytest tests/test_cli_compose.py::test_cli_compose -v
- All 3 tests must pass

**Verify no regression**: pytest

---

**Expected Outcome**: GREEN verification, no regressions
**Report Path**: plans/unification/consolidation/reports/cycle-4-1-notes.md

---
