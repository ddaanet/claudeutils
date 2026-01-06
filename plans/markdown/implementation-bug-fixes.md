# Implementation Plan: Fix Bugs #1, #2, #3

## Overview

Three bugs found via live formatter run on agent-documentation.md:

1. **Bug #3:** escape_inline_backticks() not idempotent - regex matches inside escaped
   sequences
2. **Bug #1:** Bare fence protection fails inside `` ```markdown `` blocks - no
   recursive parsing
3. **Bug #2:** Code block blank line insertion inside `` ```markdown `` blocks - same
   root cause as #1

---

## Phase 1: Fix Bug #3 (Idempotency)

### Test 1: Four-backtick idempotency

1. Add test `test_escape_inline_backticks_four_backticks_idempotent()` at
   `tests/test_markdown.py:306`
2. Given: ``"````markdown\n"`` (4 backticks with language)
3. When: Call `escape_inline_backticks()` twice
4. Then: Both passes produce identical output
5. **NEW CODE REQUIRED:** None - test will fail with current regex

### Fix: Update regex pattern

1. Edit `src/claudeutils/markdown.py:302`
2. Change: `r"(?<!`` )(`{3,})(\w*)(?! ``)"`
3. To: `r"(?<!`)(`{3,})(\w*)(?!``)"` (single backtick lookbehind, no space)
4. **RATIONALE:** Lookbehind now rejects ANY preceding backtick, not just "`` " - prevents matching inside escaped sequences

### Checkpoint 1

Run `just test tests/test_markdown.py::test_escape_inline_backticks*` - verify all
escape tests pass (9 tests including new idempotency test)

---

## Phase 2: Fix Bug #1 & #2 (Recursive Parsing)

### Test 2: Nested bare fence parsing

1. Add test `test_parse_segments_nested_bare_fence_in_markdown()` at
   `tests/test_segments.py:180`
2. Given:
   ```````
   ``````markdown\n
   \n
   ```\n
   ✅ Issue\n
   ```\n
   \n
   ``````\n
   ```````
3. When: Call `parse_segments()`
4. Then: Inner bare ``` fence marked `processable=False`
5. **NEW CODE REQUIRED:** Recursive parsing in `parse_segments()`

### Test 3: Nested code block no blank line
1. Add test `test_nested_python_block_in_markdown_no_blank_line()` at `tests/test_markdown.py:632`
2. Given: `process_lines()` with ```markdown containing ```python block
3. When: Process lines
4. Then: No blank line inserted after ```python fence
5. **DEPENDS ON:** Recursive parsing - this test validates Bug #2 is fixed

### Fix: Implement recursive parsing in parse_segments()

1. Read `src/claudeutils/markdown.py:166-230` (parse_segments function)
2. When `language == "markdown"`:
   - Extract inner content (exclude outer fence lines)
   - Calculate offset: `inner_start_line = outer_start + 1`
   - Call `parse_segments()` recursively on inner content
   - Adjust start_line for each nested segment: `seg.start_line += inner_start_line`
   - Return flattened list: [outer_fence_open_segment, *recursive_segments,
     outer_fence_close_segment]
3. For non-markdown languages: keep existing behavior

### Checkpoint 2

Run `just test tests/test_segments.py tests/test_markdown.py::test_nested*` - verify
nested fence tests pass (2 tests)

### Test 4: Integration - nested structure from agent-documentation.md

1. Add test `test_integration_nested_fences_in_markdown_block()` at
   `tests/test_markdown.py:1030`
2. Given: Real structure from `plans/markdown/agent-documentation.md:28-50`
   - ``````markdown block containing bare ``` with emoji lines
3. When: Call `process_lines()`
4. Then: Emoji lines remain unchanged (not converted to lists)
5. **DEPENDS ON:** Recursive parsing working correctly

### Checkpoint 3

Run `just test tests/test_markdown.py::test_integration_nested*` - awaiting approval
before proceeding

---

## Phase 3: Full Verification

### Run full test suite

1. Run `just test` - verify all 66 tests pass (62 existing + 4 new)
2. Expected: No failures from existing tests, all 4 new tests passing

### Integration verification

1. Run `just format` on repo
2. Verify no diffs on `plans/markdown/agent-documentation.md` (lines 28-50 bare fence)
3. Verify no diffs on `plans/markdown/feature-2-code-block-nesting.md` (line 48 backtick
   count)
4. Expected: Clean exit with no file modifications

### Commit changes

1. Stage test files: `git add tests/test_markdown.py tests/test_segments.py`
2. Stage implementation: `git add src/claudeutils/markdown.py`
3. Commit: `"Fix Bugs #1/#2/#3: Idempotent escaping and recursive fence parsing"`

---

## Constraints

- **MUST** maintain backward compatibility with existing 62 tests
- **MUST** pass new 4 tests before committing
- **NEVER** modify segment structure or flatten_segments() - only parse_segments()
  internals
- **NEVER** change pipeline order in process_lines() - only segment parsing logic
