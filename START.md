# Handoff Entry Point

## Current Status: Formatter Bug Fixes - Ready to Implement

- **Branch:** markdown
- **Issue:** `just format` corrupting markdown files (27 files affected)
- **Plan:** `plans/markdown/fix-warning-lines-tables.md`
- **Progress:** Analysis complete, fix plan ready

### The Problem

Running `just format` corrupts markdown:
- Tables converted to lists (`| Header |` → `- | Header |`)
- Single labels converted to list items (`**Label:**` → `- **Label:**`)
- 27 files affected: AGENTS.md, START.md, session.md, MODULE_INVENTORY.md, etc.

### Root Causes

1. **fix_warning_lines()** treats table pipes `| ` as prefixes
2. **fix_metadata_list_indentation()** converts single `**Label:**` to list items (wrong)
3. **Bold labels processed twice** by multiple functions

### The Fix (3 Phases)

**Phase 1: Table Detection** - Skip table rows in `fix_warning_lines()`
**Phase 2: Disable Metadata List Indentation** - Comment out function call
**Phase 3: Bold Label Exclusion** - Skip `**Label:**` in `fix_warning_lines()`

### User Requirements

- Metadata list (2+ `**Label:**` lines) → convert to list items ✅
- Single `**Label:**` line → do NOT convert ❌
- Tables → remain as tables ✅
- Indentation → consistent at same level ✅

### Next Steps

Execute plan: `plans/markdown/fix-warning-lines-tables.md`

```bash
# Implement fixes
just role-code

# Verify
just format && git diff  # Should show no unwanted changes
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
