# Handoff Entry Point

## Current Status: Segmentation Bugs Analysis Complete - 3 Critical Bugs Found

- **Branch:** markdown
- **Issue:** `just format` corrupting 2 markdown files after Phases 1-5 implementation
- **Root Cause:** Bare fence protection failure + escape_inline_backticks() regex bug
- **Plan:** `plans/markdown/fix-warning-lines-tables.md`
- **Analysis:** `plans/markdown/segmentation-bugs-analysis.md`
- **Progress:** Phases 1-5 complete ✅, Phases 7-8-10 required ❌

### What Happened

**Phases 1-5: Complete** ✅ (2026-01-05)

- Phase 1: Table detection working
- Phase 2: Single label conversion fixed
- Phase 3: Bold label exclusion working
- Phase 4: YAML prolog detection fixed (commit 663059d)
- Phase 5: `extract_prefix()` rewritten (commit 663059d)
- Result: 52/52 tests passing

**BUT:** Running `just format` STILL corrupts 2 files! ❌

### NEW Critical Bugs Discovered (2026-01-06)

After Phases 1-5, examined diffs from `just format` and found THREE critical bugs:

**Bug #2: Bare Fence Protection Failure** ⚠️ CRITICAL
- Content inside bare ` ``` ` fences being processed when it should be protected
- Test expects `processable=False` but content is being converted to lists
- **Example corruption:**
  ```diff
   ```
  -✅ Issue #1: XPASS tests visible
  -✅ Issue #2: Setup failures captured
  +- ✅ Issue #1: XPASS tests visible
  +- ✅ Issue #2: Setup failures captured
   ```
  ```
- **Files affected:** `plans/markdown/agent-documentation.md`
- **Investigation needed:** Debug why segment parser protection failing

**Bug #5: escape_inline_backticks() Regex Breaks 4+ Backticks** ⚠️ CRITICAL

- Location: `markdown.py:297`
- Pattern `r"(?<!`` )```(\w*)"` matches first 3 backticks in ````
- **Example corruption:**
  `````python
  Input:  "Output: ````markdown block"
  Output: "Output: `` ``` ```markdown block"
  #                    ^^^^^^^^^ BROKEN - fence start mid-line!
  `````
- **Why:** Negative lookbehind only checks for "`` " (2 backticks + space)
- **Impact:** Corrupts any docs trying to display 4+ backticks inline
- **Blocks:** Phase 9 (doc fix) can't be applied until regex fixed

**Clarifications:**
- ✅ Bug #1: ```markdown blocks processable → INTENTIONAL (format doc snippets)
- ✅ Bug #3: Inline code with spaces quoted → REQUIRED (dprint strips spaces)
- ⚠️ Bug #4: Backtick escaping in docs → Can't fix without fixing Bug #5 first

### Required Work (Priority Order)

**Phase 7: Debug Bare Fence Protection** ⚠️ CRITICAL
- **Problem:** Content in bare ``` fences being processed (should be protected)
- **Investigation:** Add debug logging to `parse_segments()` and `apply_fix_to_segments()`
- **Investigation:** Add debug logging to `parse_segments()` and
  `apply_fix_to_segments()`
- **Test:** Integration test verifying bare fences actually protect content
- **Impact:** 1 file corrupted (`agent-documentation.md`)

**Phase 10: Fix escape_inline_backticks() Regex** ⚠️ CRITICAL
- **Location:** `markdown.py:297`
- **Current:** `r"(?<!`` )```(\w*)"` (matches first 3 in ````)
- **Fix Option A:** `r"(?<!`)`{3}(\w*)(?!`)"` (only standalone ```)
- **Fix Option B:** `r"(?<!``)```(\w*)"` (better negative lookbehind)
- **Tests:** 3 new tests for 4+ backtick handling
- **Impact:** Blocks Phase 9, corrupts 4+ backtick sequences

**Phase 8: Add Integration Tests** ⚠️ CRITICAL

- **Purpose:** Validate end-to-end protection works
- **Tests:** Python/YAML/markdown/bare fences unchanged, plain text processed
- **Status:** Required for validation

**Phase 9: Fix Incorrect Backtick Escaping in Docs** (BLOCKED by Phase 10)

- **File:** `plans/markdown/feature-2-code-block-nesting.md:48`
- **Change:** ````markdown block → `` ````markdown `` block
- **Why blocked:** Current regex would re-corrupt this fix
- **Impact:** Low priority, documentation only

### Documentation

**Segmentation Bugs Analysis:** `plans/markdown/segmentation-bugs-analysis.md` (NEW)

- Complete investigation of post-Phase-5 corruption
- Evidence with git diffs and test output showing regex bug
- User clarifications on intentional features vs bugs
- Phases 7-10 implementation details with test cases

**Root Cause Analysis:** `plans/markdown/root-cause-analysis.md` (COMPLETE)

- Original analysis that led to Phases 4-5
- YAML prolog and prefix detection bugs
- Implemented in commit 663059d

**Implementation Plan:** `plans/markdown/fix-warning-lines-tables.md`

- Phases 1-5: Complete ✅
- Phases 7, 8, 10: Required ❌
- Phase 9: Blocked (depends on Phase 10)
- Complete test cases and success criteria

---

## What Was Completed (2026-01-05)

### Markdown Segment Processing - Complete ✅

Implemented segment-aware markdown processing to prevent false positives in fenced
blocks:

1. **Segment parser** - Classify content (fenced blocks, YAML prologs, plain text)
2. **Stack-based nesting** - Handle `` ```markdown `` inside `` ```python ``
3. **Segment integration** - Apply fixes only to processable segments
4. **Backtick space preservation** - Quote spaces in inline code
5. **Exception handling** - MarkdownProcessingError and MarkdownInnerFenceError

### Results (Updated 2026-01-06)

- 52/52 tests passing (Phases 1-5 complete)
- Content in `` ```python ``, `` ```yaml `` blocks protected ✅
- YAML prologs with underscores/hyphens/digits recognized ✅
- Regular prose no longer converted to lists ✅
- **Remaining issues:**
  - Bare ``` fences NOT protecting content ❌ (Bug #2)
  - 4+ backticks corrupted by escape regex ❌ (Bug #5)

---

## Key Files

| File                                         | Purpose                                    |
| -------------------------------------------- | ------------------------------------------ |
| `session.md`                                 | Current session notes (short-term only)    |
| `AGENTS.md`                                  | Core agent rules and role definitions      |
| `agents/TEST_DATA.md`                        | Data types and sample entries              |
| `agents/DESIGN_DECISIONS.md`                 | Architectural and implementation decisions |
| `plans/markdown/fix-warning-lines-tables.md` | Current fix plan for formatter bugs        |

---

## Next Steps

**Immediate:** Implement Phases 7, 10, 8 (in order)

**Phase 7: Debug Bare Fence Protection** ⚠️ CRITICAL

```bash
# Add debug logging to markdown.py parse_segments()
# Add integration test for bare fence protection
# Run formatter on test file and examine logs
# Identify where protection is failing
just test tests/test_markdown.py
```

**Phase 10: Fix escape_inline_backticks() Regex** ⚠️ CRITICAL

````bash
# Edit markdown.py:297
# Change: r"(?<!`` )```(\w*)" → r"(?<!`)`{3}(\w*)(?!`)"
# Add 3 tests for 4+ backtick handling
just test tests/test_markdown.py
````

**Phase 8: Add Integration Tests**

```bash
# Add end-to-end tests for all fence types
# Verify Python/YAML/markdown/bare fences protected
# Verify plain text still processed
just test tests/test_markdown.py
```

**Phase 9: Fix Doc Backtick Escaping** (after Phase 10)

`````bash
# Edit plans/markdown/feature-2-code-block-nesting.md:48
# Change: ````markdown block → `` ````markdown `` block
`````

**Integration Testing**

```bash
just format           # Should produce minimal/no diffs
git diff              # Verify 2 remaining files no longer corrupted
```

**Success criteria:**

- Bare fences protect content (processable=False)
- 4+ backticks in inline code not corrupted
- All integration tests pass
- `just format` produces minimal/no changes

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
