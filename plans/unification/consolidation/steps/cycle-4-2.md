# Cycle 4.2

**Plan**: `plans/unification/consolidation/runbook.md`
**Common Context**: See plan file for context

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
