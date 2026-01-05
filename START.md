# Handoff Entry Point

## Current Status: Root Cause Analysis Complete - NEW Critical Bugs Found

- **Branch:** markdown
- **Issue:** `just format` corrupting markdown files (27 files affected)
- **Root Cause:** YAML prolog detection broken + prefix detection over-aggressive
- **Plan:** `plans/markdown/fix-warning-lines-tables.md`
- **Analysis:** `plans/markdown/root-cause-analysis.md`
- **Progress:** Phases 1-3 complete ✅, Phases 4-5 required ❌

### What Happened

**Phases 1-3: Complete** ✅
- Phase 1: Table detection working
- Phase 2: Single label conversion fixed
- Phase 3: Bold label exclusion working
- Result: 45/45 tests passing

**BUT:** Running `just format` STILL corrupts 27 files! ❌

### NEW Critical Bugs Discovered (2026-01-05)

After Phases 1-3, examined actual diff from `just format` and found TWO critical bugs:

**Bug #1: YAML Prolog Detection Broken** (`markdown.py:135`)
- Pattern `r"^\w+:\s"` requires space after colon
- Doesn't match YAML keys without values: `tier_structure:`, `critical:`
- Doesn't match keys with digits: `option_2:`, `key123:`
- Doesn't match keys with hyphens: `semantic-type:`, `author-model:`
- YAML sections not recognized → fall through to plain text → get mangled
- **Example corruption:**
  ```diff
  ---
  -tier_structure:
  -  critical:
  +- tier_structure:
  +- critical:
      - item
  ```

**Bug #2: Prefix Detection Over-Aggressive** (`markdown.py:447`)
- Pattern `r"^(\S+(?:\s|:))"` matches ANY non-whitespace + space/colon
- Matches regular prose: "Task agent" → converted to list ❌
- Matches block quotes: `> text` → converted to list ❌
- Matches tree diagrams: `├─ item` → converted to list ❌
- **Example corruption:**
  ```diff
  -Task agent prompt is a minimal replacement.
  -Task agent are effectively "interactive-only".
  +- Task agent prompt is a minimal replacement.
  +- Task agent are effectively "interactive-only".
  ```

### Required Work

**Phase 4: Fix YAML Prolog Detection** (CRITICAL)
- Location: `markdown.py:135`
- Change: `r"^\w+:\s"` → `r"^[a-zA-Z_][\w-]*:"`
- Effect: YAML content protected (processable=False), never mangled
- Supports: underscores, hyphens, digits (not as first char)
- Tests: 2 new segment parser tests

**Phase 5: Rewrite `extract_prefix()`** (CRITICAL)
- Location: `markdown.py:431-450`
- Change: Complete rewrite - only match emoji, `[TODO]`, `NOTE:` uppercase
- Effect: Defensive - even if content not in fenced blocks, don't mangle
- Tests: 5 new prefix detection tests

### Documentation

**Root Cause Analysis:** `plans/markdown/root-cause-analysis.md`
- Detailed technical analysis with evidence from diff
- Complete implementation code for both fixes
- Test requirements and expected behavior
- Risk assessment and rollback plan

**Implementation Plan:** `plans/markdown/fix-warning-lines-tables.md`
- Updated with Phases 4-5 complete code
- 7 new test cases ready to implement
- Integration testing steps
- Success criteria validation

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

**Immediate:** Implement Phases 4-5

**Phase 4: Fix YAML Prolog Detection**
```bash
# Edit markdown.py:135
# Change: r"^\w+:\s" → r"^[a-zA-Z_][\w]*:"
# Add 2 segment parser tests
just test tests/test_markdown.py
```

**Phase 5: Rewrite `extract_prefix()`**
```bash
# Replace markdown.py:431-450 with conservative implementation
# Add 5 prefix detection tests
just test tests/test_markdown.py
```

**Integration Testing**
```bash
just format           # Should produce minimal/no diffs
git diff              # Verify 27 files no longer corrupted
```

**Success criteria:**
- YAML prologs recognized (processable=False)
- Regular prose NOT converted to lists
- Emoji/bracket prefixes STILL work
- All 55 tests pass (48 existing + 7 new)
- `just format` produces minimal/no changes on 27 files

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
