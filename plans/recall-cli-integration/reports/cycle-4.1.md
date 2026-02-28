# Cycle 4.1: Diff lists changed files

**Timestamp:** 2026-02-28

## Status: GREEN_VERIFIED

## Test Execution

**Test command:**
- `pytest tests/test_recall_cli_diff.py::test_diff_lists_changed_files -xvs`

### RED Phase
- **test_diff_lists_changed_files:** FAIL (as expected)
  - Expected: `diff` subcommand not implemented (Click usage error, exit code 2)
  - Actual: Exit code 2, command not found

### GREEN Phase
- **Result:** PASS (1/1 test passing)
- **Implementation:** Added `diff` subcommand to `_recall` group
  - Takes `job` argument
  - Derives artifact path from `CLAUDE_PROJECT_DIR` env or `.`
  - Gets artifact mtime via `os.path.getmtime()`, formats as ISO 8601 for git
  - Runs `git log --since=<mtime> --name-only --pretty=format: -- plans/<job>/`
  - Filters output: removes blanks, excludes artifact path itself, dedup via `set()`, sort via `sorted()`
  - Outputs sorted file list to stdout, one per line
  - Exits 0 (always, even if empty list)
  - Precondition failures (no git, no artifact) exit 1

### Regression Check
- **Full test suite:** 1335/1336 passed, 1 xfail (expected)
- **Status:** No regressions introduced
- **Delta:** +1 new test (diff subcommand)

## Refactoring

### Code Quality
- Fixed DTZ006 linting: added `tz=datetime.timezone.utc` to `datetime.fromtimestamp()`
- Fixed D205 docstring formatting: expanded to multiline with blank line after summary
- Fixed PLC0415: moved `import time` to top-level in test file
- Precommit validation: PASS
- Lint: PASS

## Files Modified

- `src/claudeutils/recall_cli/cli.py` — Added subprocess and datetime imports, implemented `diff` subcommand
- `tests/test_recall_cli_diff.py` — New test file with real git repo setup using tmp_path fixture

## Stop Condition

None — cycle completed successfully.

## Decision Made

The `diff` subcommand uses `git log --since` with artifact mtime to detect changes. Real git repos in tests (tmp_path fixture) provide fast, realistic validation. E2E approach catches state transitions that mocks would miss. Exit code always 0 for empty result (no changes is valid), exit 1 only for preconditions (missing artifact, not in git repo).

## Commit

Commit: `0599850a` — "WIP: Cycle 4.1 Diff lists changed files"
