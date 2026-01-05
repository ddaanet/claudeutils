# Session Notes

**⚠️ IMPORTANT: This file is for SHORT-TERM context only**

This file tracks:

- **Current work** in the active session
- **Pending tasks** that are queued up
- **Recently completed** tasks (last 1-2 sessions) for immediate context

**DO NOT** keep long-lived data here. Once tasks are complete and documented elsewhere
(DESIGN_DECISIONS.md, TEST_DATA.md, etc.), flush them from this file.

**Lifecycle:**

- Add tasks when starting work
- Update status as work progresses
- Move completed work to permanent docs
- Flush from here when no longer needed for immediate context

---

## Current Status: Bug Fix Planned 🔧

- **Branch:** markdown
- **Issue:** List detection corrupts content in non-markdown fenced blocks
- **Plan:** `plans/markdown-fence-aware-processing.md` (written 2026-01-05)
- **Next:** Execute plan in code role session

### The Problem

Discovered critical bug: ALL processing functions (not just list detection) operate on raw line lists without block context. This causes:

- Dictionary keys in ```python blocks → converted to list items
- Table rows → converted to list items
- YAML lists → further corrupted
- Any content with colons/prefixes inside ANY fenced block → corrupted

**Example:**
```python
# Input: dict in ```python block
config = {"name": "test", "version": "1.0"}

# Current output: BROKEN
config = {
- "name": "test",      # ❌
- "version": "1.0"     # ❌
}
```

### The Solution

Implement segment-aware architecture:
1. Parse document into segments (processable vs protected)
2. Apply fixes ONLY to: plain text + ````markdown` blocks
3. Protect: ```python, ```yaml, ```bash, ``` (bare), all other fenced blocks

**Plan:** 5 phases, 19 tests, checkpoints after each phase

---

## Pending Tasks

**Immediate:** Execute `plans/markdown-fence-aware-processing.md`

1. Phase 1: Segment parser foundation (5 tests)
2. Phase 2: Mixed content parsing (3 tests)
3. Phase 3: Segment integration (4 tests)
4. Phase 4: Backtick space preservation (5 tests)
5. Phase 5: Exception handling (2 tests)

---

## Previous Work (2026-01-05)

### Markdown Preprocessor Features Implemented

1. ✅ Generic prefix detection in fix_warning_lines
2. ✅ Code block nesting with inner fence handling
3. ✅ Metadata list indentation
4. ✅ Inline backtick escaping
5. ✅ Custom exception handling

**Note:** All features work correctly on plain text, but need segment-aware protection for fenced blocks

---

**Remember:** Flush completed items once documented elsewhere!
