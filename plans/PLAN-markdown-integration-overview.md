# Integration Plan: fix_markdown_structure → src/claudeutils

## Overview

Integrate standalone `scripts/fix_markdown_structure.py` into `src/claudeutils` as a
proper CLI subcommand.

**Current State:**

- Script exists at `scripts/fix_markdown_structure.py` (193 lines)
- Tests exist at `scripts/test_fix_markdown_structure.py` (outside main test suite)
- Currently used in `just format` command for markdown preprocessing

**Target State:**

- New module: `src/claudeutils/markdown.py` (core functions)
- New CLI command: `uv run claudeutils format <files>` or similar
- Tests migrated to: `tests/test_markdown.py` (in main test suite)
- Update `just format` to use new module

---

## Architecture Decisions

### Decision 1: Command Name

**Options:**

- `claudeutils format` - Aligns with existing behavior, clear purpose
- `claudeutils fix-markdown` - More descriptive, avoids confusion with code formatting
- `claudeutils markdown` - Shorter, could have subcommands later

**Recommendation:** TBD - requires user input

### Decision 2: API Design

**Options:**

- **A) CLI-only** - No programmatic API, just expose via CLI
- **B) Module + CLI** - Public functions in `markdown.py`, CLI wraps them
- **C) Class-based** - `MarkdownFormatter` class with methods

**Recommendation:** Option B - matches existing pattern (see `extraction.py`,
`discovery.py`)

### Decision 3: File Discovery

**Current behavior:** Script reads file paths from stdin (piped from `git ls-files`)

**Options:**

- **A) Keep stdin-based** - Match current behavior
- **B) Add glob patterns** - `claudeutils format "*.md"` or `claudeutils format agents/`
- **C) Both** - Accept stdin OR file arguments

**Recommendation:** TBD - requires user input

---

## Implementation Steps

### Phase 1: Create Module (No Breaking Changes)

1. Create `src/claudeutils/markdown.py`
   - Copy functions from `scripts/fix_markdown_structure.py`
   - Keep same signatures for now
   - Add type annotations (already present)
   - Keep public API: `process_file()`, `process_lines()`
2. Create `tests/test_markdown.py`
   - Copy tests from `scripts/test_fix_markdown_structure.py`
   - Update imports: `from claudeutils.markdown import ...`
   - Run `just role-code tests/test_markdown.py` - verify all pass

### Phase 2: Add CLI Command

3. Add subcommand in `src/claudeutils/cli.py`
   - Add `handle_format()` function
   - Add parser in `main()` function
   - Wire to `markdown.process_file()`
4. Add integration test in `tests/test_cli_format.py`
   - Test basic file processing
   - Test error handling (missing files, non-.md files)
   - Test output format

### Phase 3: Update Justfile

5. Update `justfile` format target
   - Replace: `uv run scripts/fix_markdown_structure.py`
   - With: `uv run claudeutils format` (or equivalent)
   - Verify `just format` still works correctly

### Phase 4: Cleanup

6. Remove old files (only after all tests pass)
   - Delete `scripts/fix_markdown_structure.py`
   - Delete `scripts/test_fix_markdown_structure.py`

---

## Open Questions

1. **Command name?** (format vs fix-markdown vs markdown)
2. **File discovery?** (stdin-only vs glob vs both)
3. **Output behavior?**
   - Current: Prints modified file paths to stdout
   - Should CLI preserve this? Or show summary ("2 files modified")?
4. **Error handling?**
   - Current: Silently skips non-.md files
   - Should CLI warn/error?

---

## Testing Strategy

- **Unit tests:** All existing tests must pass after migration
- **Integration test:** `just format` produces identical results
- **No new tests needed** unless API/behavior changes

---

## Success Criteria

- [ ] All tests pass (`just dev`)
- [ ] `just format` behavior unchanged
- [ ] New CLI command functional: `uv run claudeutils format`
- [ ] No duplicate code (old script removed)
- [ ] Module under 300 lines (currently ~193, should stay similar)
