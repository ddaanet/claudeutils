# Step 7

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 7: Create Validation CLI + Tests

**Objective**: Create unified `claudeutils validate [targets]` command (FR-1, D-4).

**Execution Model**: Haiku

**Implementation**:

1. Create `src/claudeutils/validation/cli.py`:
   - Click group `validate` with invoke_without_command=True (bare `claudeutils validate` runs all)
   - Subcommands: `learnings`, `memory-index`, `tasks`, `decisions`, `jobs`
   - Command tree:
     ```
     claudeutils validate              → runs all validators
     claudeutils validate learnings    → runs learnings only
     claudeutils validate memory-index → runs memory-index only
     claudeutils validate tasks        → runs tasks only
     claudeutils validate decisions    → runs decisions only
     claudeutils validate jobs         → runs jobs only
     ```
   - Each subcommand: resolves `root` via `find_project_root()`, calls validator, prints errors to stderr, exits 1 on failure
   - "All" mode: runs every validator, collects all errors, prints errors per-validator with headers, exits 1 if ANY failed (don't short-circuit on first failure)
   - Pattern: follow existing Click group structure (see `account`, `model`, `statusline` in `src/claudeutils/cli.py`)

2. Wire into main CLI:
   - Add `from claudeutils.validation.cli import validate` to `src/claudeutils/cli.py`
   - Add `cli.add_command(validate)` alongside existing command registrations

3. Update `src/claudeutils/validation/__init__.py`:
   - Export key functions for programmatic use: `validate_learnings`, `validate_jobs`, etc.

4. Create `tests/test_validation_cli.py`:
   - Test: `claudeutils validate` runs all validators (mock each validator function)
   - Test: `claudeutils validate learnings` runs only learnings validator
   - Test: exit code 1 when validation fails
   - Test: exit code 0 when validation passes
   - Test: error output goes to stderr
   - Use Click's `CliRunner` for testing (see existing test patterns in `tests/test_cli_*.py`)

**Expected Outcome**: `claudeutils validate` runs all validators, individual targets selectable.

**Success Criteria**: `pytest tests/test_validation_cli.py -q` passes, `claudeutils validate` works from command line.

---
