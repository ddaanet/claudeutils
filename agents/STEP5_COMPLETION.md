# Step 5 Completion: CLI Subcommands

**Status:** ✅ COMPLETE (2025-12-19)

## Summary

Implemented full CLI interface with `list` and `extract` subcommands. All 18 tests passing.

## Test Results

```bash
$ just test tests/test_cli*.py -v
tests/test_cli_list.py ........                [8 tests]
tests/test_cli_extract_basic.py .......        [7 tests]
tests/test_cli_extract_output.py ...           [3 tests]
============================== 18 passed ==============================
```

## Implementation

**Main file:** `src/claudeutils/cli.py`

**Key functions:**
- `main()` - CLI entry point with argparse subcommands (cli.py:52)
- `find_session_by_prefix(prefix, project_dir)` - Session ID matching (cli.py:15)

**Subcommands:**
1. `list [--project PATH]` - Display sessions with `[prefix] title` format
2. `extract SESSION_PREFIX [--project PATH] [--output FILE]` - Extract feedback as JSON

**Features:**
- Session prefix matching (partial UUID match from start)
- JSON output with full field serialization (`model_dump(mode="json")`)
- Error handling to stderr with exit codes
- File output with `--output` flag

## Design Decisions

1. **Module split:** Test files split into 3 focused modules:
   - `test_cli_list.py` - List command tests
   - `test_cli_extract_basic.py` - Extract command and session matching tests
   - `test_cli_extract_output.py` - JSON output and integration tests

2. **Path.cwd() vs os.getcwd():** Used `Path.cwd()` for consistency with pathlib usage throughout codebase

3. **Error messages:** Print to stderr using `print(..., file=sys.stderr)` before `sys.exit(1)`

## Entry Point

Added `[project.scripts]` configuration in `pyproject.toml`:
```toml
[project.scripts]
claudeutils = "claudeutils.cli:main"
```

This enables direct invocation: `uv run claudeutils list` (no `python -m` needed).

## File Locations

**Implementation:**
- `src/claudeutils/cli.py` - CLI entry point and logic

**Tests:**
- `tests/test_cli_list.py` - List command (8 tests)
- `tests/test_cli_extract_basic.py` - Extract basics (7 tests)
- `tests/test_cli_extract_output.py` - JSON output (3 tests)
- `tests/pytest_helpers.py` - Shared test utilities

## Next Steps

All planned steps (1-5) are now complete. The project delivers a working CLI tool to extract user feedback from Claude Code conversation history.

**To use the tool:**
```bash
# List sessions
uv run claudeutils list

# Extract feedback from a session
uv run claudeutils extract e12d203f

# Extract to file
uv run claudeutils extract e12d203f --output feedback.json
```

**Potential future enhancements:**
- Add `--format` flag for output options (pretty JSON, CSV, etc.)
- Add `--filter` flag to filter by feedback type
- Add `--since` / `--until` for date range filtering
