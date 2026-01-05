# Handoff Entry Point

## Current Status: Markdown Bug Fix Planned 🔧

- **Branch:** markdown
- **Issue:** List detection triggers on ALL fenced blocks (yaml, python, tables)
- **Plan:** `plans/markdown-fence-aware-processing.md`
- **Next:** Execute plan in code role session

### The Bug

Processing functions apply to ALL content, including inside fenced blocks:

```python
# Input: ```python block with dict
config = {
    "name": "test",
    "version": "1.0"
}

# Current output: BROKEN
config = {
- "name": "test",      # ❌ Converted to list item
- "version": "1.0"     # ❌ Converted to list item
}
```

Tables, YAML lists, and other structured content also corrupted.

### The Fix

Implement segment-aware processing:
- Parse document into segments (processable vs protected)
- Apply fixes ONLY to: plain text + ````markdown` blocks
- Protect ALL other blocks: ```python, ```yaml, ```bash, ``` (bare), etc.

**Implementation:** 5 phases, 19 tests, ~100 LOC
**Checkpoint:** After each phase for validation

---

## What Was Completed (2026-01-05)

### Markdown Preprocessor Features

Implemented three major features plus bonus improvements:

1. **Generic prefix detection** - Extended fix_warning_lines to handle any consistent
   non-markup prefix (emoji, brackets, colons)
2. **Code block nesting** - Handle inner fences in ```markdown blocks using ````
3. **Metadata list indentation** - Convert labels to list items with proper nesting
4. **Inline backtick escaping** - Wrap `` ```language `` to prevent fence ambiguity
5. **Custom exception handling** - MarkdownProcessingError and MarkdownInnerFenceError

### Documentation

- ✅ Module docstrings explaining preprocessor purpose and pipeline
- ✅ README section with usage examples and what it fixes
- ✅ Function docstrings for all key functions
- ✅ TEST_DATA.md with input/output transformations
- ✅ DESIGN_DECISIONS.md with architecture rationale

### Test Coverage

- 40 total tests passing (32 markdown + 8 CLI)
- All features validated through TDD
- Exception handling and error reporting tested

---

## Key Files

| File                        | Purpose                                 |
| --------------------------- | --------------------------------------- |
| `session.md`                | Current session notes (short-term only) |
| `AGENTS.md`                 | Core agent rules and role definitions   |
| `agents/TEST_DATA.md`       | Data types and sample entries           |
| `agents/DESIGN_DECISIONS.md` | Architectural and implementation decisions |
| `agents/ROADMAP.md`         | Future enhancement ideas                |

---

## Next Steps

**Immediate:** Execute `plans/markdown-fence-aware-processing.md`

```bash
# Load code role and execute plan
just role-code
```

**Plan structure:**
- Phase 1: Segment parser foundation (5 tests)
- Phase 2: Mixed content parsing (3 tests)
- Phase 3: Segment integration (4 tests)
- Phase 4: Backtick space preservation (5 tests)
- Phase 5: Exception handling (2 tests)

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
