# Handoff Entry Point

## Current Status: Formatter Bug Fixes - Phases 1-2 Complete

- **Branch:** markdown
- **Issue:** `just format` corrupting markdown files (27 files affected)
- **Plan:** `plans/markdown/fix-warning-lines-tables.md`
- **Progress:** Phases 1-2 implemented and tested ✅

### Completed Work

**Phase 1: Table Detection** ✅
- Added table detection in `extract_prefix()` (lines 425-427)
- Tables with `|` prefix and 2+ pipes now skipped
- Test: `test_fix_warning_lines_skips_table_rows` passing

**Phase 2: Metadata List Indentation** ✅
- Merged functionality into `fix_metadata_blocks()` (lines 301-354)
- Pattern updated to match labels with/without content: `^\*\*[A-Za-z][^*]+:\*\*|^\*\*[A-Za-z][^*]+\*\*:`
- Following lists automatically indented after 2+ metadata labels
- Disabled `fix_metadata_list_indentation()` (line 744)
- Test: `test_single_bold_label_not_converted_to_list` passing

### Results

- All 45/45 markdown tests passing
- Tables remain as tables (no `- |` prefixes)
- Single `**Label:**` lines NOT converted to list items
- 2+ consecutive `**Label:**` lines converted to list with indented following lists
- Fix is idempotent (multiple runs produce same output)

### User Requirements Met

- Metadata list (2+ `**Label:**` lines) → convert to list items ✅
- Single `**Label:**` line → do NOT convert ✅
- Tables → remain as tables ✅
- Lists after metadata lists → indented ✅
- Indentation → consistent at same level ✅

### Remaining Work

**Phase 3: Bold Label Exclusion** (Optional)
- Skip `**Label:**` patterns in `fix_warning_lines()`
- May prevent edge cases where single labels match prefix patterns

### Verification

```bash
# Run tests
just test tests/test_markdown.py  # 45/45 passing

# Test formatting (when ready)
just format && git diff  # Should show minimal changes
```

---

## What Was Completed (2026-01-05)

### Markdown Segment Processing - Complete ✅

Implemented segment-aware markdown processing to prevent false positives in fenced blocks:

1. **Segment parser** - Classify content (fenced blocks, YAML prologs, plain text)
2. **Stack-based nesting** - Handle `` ```markdown `` inside `` ```python ``
3. **Segment integration** - Apply fixes only to processable segments
4. **Backtick space preservation** - Quote spaces in inline code
5. **Exception handling** - MarkdownProcessingError and MarkdownInnerFenceError

### Results

- 48/48 tests passing (40 markdown + 8 segments)
- Content in `` ```python ``, `` ```yaml ``, bare `` ``` `` blocks protected
- Python dicts, tables, structured content no longer corrupted by fixes
- All fixes respect segment boundaries

---

## Key Files

| File                             | Purpose                                        |
| -------------------------------- | ---------------------------------------------- |
| `session.md`                     | Current session notes (short-term only)        |
| `AGENTS.md`                      | Core agent rules and role definitions          |
| `agents/TEST_DATA.md`            | Data types and sample entries                  |
| `agents/DESIGN_DECISIONS.md`     | Architectural and implementation decisions     |
| `plans/markdown/fix-warning-lines-tables.md` | Current fix plan for formatter bugs |

---

## Next Steps

**Immediate:** Execute `plans/markdown/fix-warning-lines-tables.md`

```bash
# Load code role and execute plan
just role-code
```

**Plan structure:**
- Phase 1: Table detection (skip table rows in fix_warning_lines)
- Phase 2: Disable metadata list indentation (single labels stay as-is)
- Phase 3: Bold label exclusion (avoid duplicate processing)
- Phase 4: Tighten prefix patterns (optional)

**Success criteria:**
- Tables remain as tables after `just format`
- Single `**Label:**` lines not converted to list items
- 48/48 tests pass

---

## Quick Reference

```bash
# Development workflow
just dev              # Format, check, and test
just test            # Run pytest
just check           # Run ruff + mypy
just format          # Auto-format code

# Tool usage
uv run claudeutils list                    # List sessions
uv run claudeutils extract <prefix>        # Extract feedback
uv run claudeutils markdown               # Process markdown files
uv run claudeutils tokens sonnet file.md  # Count tokens

# Git workflow
git status           # Check staged changes
git log --oneline -10  # Recent commits
```

---

**Note:** See `AGENTS.md` for detailed agent instructions, roles, and rules.
