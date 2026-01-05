# Plan: Fence-Aware Markdown Processing

## Context

### Current Problem

**Broken list detection triggers on ALL content:**
- Processes lines inside ```python, ```bash, ```javascript blocks
- Converts dictionary keys to list items: `"name": "test"` → `- "name": "test"`
- Converts table rows to list items: `| Build | Done |` → `- | Build | Done |`

**Root cause:** All processing functions operate on raw line lists without block context.

### Requirements

**Processing rules:**
- **MUST** process content outside any fenced blocks
- **MUST** process content inside ````markdown` blocks only
- **MUST NOT** process content inside ```python, ```bash, ```javascript, ``` (bare), etc.
- **MUST NOT** process markdown blocks nested inside non-markdown blocks
- **MUST NOT** process content inside YAML prolog sections (---...---)

**Backtick space preservation:**
- `` `blah ` `` → `` `"blah "` ``
- `` ` | ` `` → `` `" | "` ``
- Preserves semantic correctness for string discourse

**Scope:** ALL fixes affected (not just list detection):
- `fix_dunder_references`
- `fix_metadata_blocks`
- `fix_warning_lines`
- `fix_nested_lists`
- `fix_metadata_list_indentation`
- `fix_numbered_list_spacing`
- `escape_inline_backticks`

**Exception:** `fix_markdown_code_blocks` still must detect/fix inner fences in any block.

---

## Architecture Change

### Current: Line-by-line processing
```python
def process_lines(lines: list[str]) -> list[str]:
    result = fix_metadata_blocks(lines)  # Processes ALL lines
    result = fix_warning_lines(result)   # Processes ALL lines
    return result
```

### New: Segment-aware processing
```python
def process_lines(lines: list[str]) -> list[str]:
    segments = parse_segments(lines)     # Classify: processable vs protected
    for seg in segments:
        if seg.is_processable:
            seg.lines = fix_metadata_blocks(seg.lines)
            seg.lines = fix_warning_lines(seg.lines)
    return flatten_segments(segments)
```

---

## Implementation Plan

### Phase 1: Segment Parser (Foundation)

#### Test 1: Parse empty input
**Given:** `[]`
**When:** `parse_segments([])`
**Then:** Returns `[]`
**NEW:** Basic `parse_segments` function returning empty list

#### Test 2: Parse plain text (no fences)
**Given:** `["Line 1\n", "Line 2\n"]`
**When:** `parse_segments(lines)`
**Then:** Returns single segment, `processable=True`, contains both lines
**NEW:** Segment classification for non-fenced content

#### Test 3: Parse ```python block
**Given:**
```python
lines = [
    "```python\n",
    "x = 1\n",
    "```\n"
]
```
**When:** `parse_segments(lines)`
**Then:** Returns single segment, `processable=False`, language=`"python"`
**NEW:** Detect fenced block boundaries, classify as protected

#### Test 4: Parse ```markdown block
**Given:**
```python
lines = [
    "```markdown\n",
    "# Title\n",
    "```\n"
]
```
**When:** `parse_segments(lines)`
**Then:** Returns single segment, `processable=True`, language=`"markdown"`
**NEW:** Special case for markdown blocks (processable)

#### Test 5: Parse bare ``` block (no language)
**Given:**
```python
lines = [
    "```\n",
    "raw text\n",
    "```\n"
]
```
**When:** `parse_segments(lines)`
**Then:** Returns single segment, `processable=False`, language=`None`
**NEW:** Bare fences are protected (not processable)

**Checkpoint:** Run `just role-code tests/test_markdown.py::test_parse_segments*` - awaiting approval

---

### Phase 2: Mixed Content Parsing

#### Test 6: Parse text before and after fence
**Given:**
```python
lines = [
    "Text before\n",
    "```python\n",
    "code\n",
    "```\n",
    "Text after\n"
]
```
**When:** `parse_segments(lines)`
**Then:** Returns 3 segments:
1. `processable=True`, lines=`["Text before\n"]`
2. `processable=False`, language=`"python"`, lines=`["```python\n", "code\n", "```\n"]`
3. `processable=True`, lines=`["Text after\n"]`
**NEW:** Multi-segment parsing with state machine

#### Test 7: Parse consecutive fenced blocks
**Given:**
```python
lines = [
    "```bash\n",
    "echo hello\n",
    "```\n",
    "```python\n",
    "x = 1\n",
    "```\n"
]
```
**When:** `parse_segments(lines)`
**Then:** Returns 2 segments, both `processable=False`, different languages
**NEW:** State transitions between blocks

#### Test 8: Parse nested ```markdown inside ```python
**Given:**
```python
lines = [
    "```python\n",
    "# docstring with example:\n",
    "```markdown\n",
    "# Title\n",
    "```\n",
    "```\n"  # closes python block
]
```
**When:** `parse_segments(lines)`
**Then:** Returns 1 segment, `processable=False`, language=`"python"`, contains all lines
**NEW:** Nested markdown NOT processable when inside non-markdown block

**Checkpoint:** Run `just role-code tests/test_markdown.py::test_parse_segments*` - awaiting approval

---

### Phase 3: Segment Integration

#### Test 9: Apply fix to processable segment only
**Given:** Mixed content with ```python block
**When:** Apply `fix_metadata_blocks` via segment processor
**Then:**
- Plain text: `**File:** test` → `- **File:** test`
- Inside ```python: unchanged
**NEW:** `apply_fix_to_segments(segments, fix_fn)` wrapper

#### Test 10: Skip all fixes in YAML prolog block
**Given:** YAML prolog content
```
---
title: Document
tasks: [ build, test ]
---
```
**When:** `process_lines(lines)` (full pipeline)
**Then:** YAML prolog content completely unchanged
**NEW:** Full integration test, validates no false triggers

#### Test 11: Skip all fixes in bare ``` block
**Given:** Raw block with colon-prefixed lines
```
NOTE: Important
TODO: Action
```
**When:** `process_lines(lines)`
**Then:** Raw content unchanged (no list conversion)
**NEW:** Validates bare blocks protected

#### Test 12: Skip all fixes in table rows
**Given:** Table inside ```markdown block nested in ```python block
**When:** `process_lines(lines)`
**Then:** Table pipes not converted to lists
**NEW:** Validates nested markdown protection

**Checkpoint:** Run `just dev` - all existing tests + new tests pass - awaiting approval

---

### Phase 4: Backtick Space Preservation

#### Test 13: Quote backticks with leading space
**Given:** `` "`blah `" ``
**When:** `fix_backtick_spaces(line)`
**Then:** `` "`\"blah \"`" ``
**NEW:** `fix_backtick_spaces` function, handles leading space

#### Test 14: Quote backticks with trailing space
**Given:** `` "` blah`" ``
**When:** `fix_backtick_spaces(line)`
**Then:** `` "`\" blah\"`" ``
**NEW:** Handle trailing space

#### Test 15: Quote backticks with both leading and trailing space
**Given:** `` "` | `" ``
**When:** `fix_backtick_spaces(line)`
**Then:** `` "`\" | \"`" ``
**NEW:** Handle both spaces

#### Test 16: Skip backticks without spaces
**Given:** `` "`code`" ``
**When:** `fix_backtick_spaces(line)`
**Then:** `` "`code`" `` (unchanged)
**NEW:** Avoid false positives

#### Test 17: Skip backticks inside fenced blocks
**Given:** Backtick with space inside ```python block
**When:** `process_lines(lines)` with new fix enabled
**Then:** No quoting applied inside protected blocks
**NEW:** Integrate with segment processing

**Checkpoint:** Run `just dev` - awaiting approval

---

### Phase 5: Exception Handling

#### Test 18: Inner fence detection still works
**Given:** ```python block with inner ```
**When:** `process_lines(lines)`
**Then:** Raises `MarkdownInnerFenceError`
**NEW:** Verify `fix_markdown_code_blocks` unaffected by segment changes

#### Test 19: Inner fence detection in ```markdown block
**Given:** ````markdown` block with inner ```
**When:** `process_lines(lines)`
**Then:** Converts outer fence to `````markdown`
**NEW:** Verify markdown block nesting still works

**Checkpoint:** Run `just dev` - awaiting approval

---

## Data Structures

### Segment Model
```python
class Segment(BaseModel):
    processable: bool
    language: str | None  # None for bare blocks or plain text
    lines: list[str]
    start_line: int  # For error reporting
```

### Segment Types
- **Processable:** Plain text, ```markdown blocks
- **Protected:** All other fenced blocks (```python, ```bash, ``` bare, etc.), YAML prolog sections

---

## Success Criteria

1. ✅ All existing tests continue passing
2. ✅ Lists not detected inside ```python, ```bash, ```javascript, ``` (bare) blocks, or YAML prolog sections
3. ✅ All fixes skip content inside protected blocks
4. ✅ Backtick space preservation works correctly
5. ✅ Inner fence detection/fixing still works for ```markdown blocks
6. ✅ No changes to `fix_markdown_code_blocks` behavior

---

## Open Questions

**Q:** Should `escape_inline_backticks` also respect segments?
**A:** Yes - it escapes ``` in text, shouldn't process inside fenced blocks

**Q:** Do we need recursion depth tracking for deeply nested blocks?
**A:** No - outer block protection is sufficient (all content inside protected block is protected)

**Q:** Should we validate fence balance?
**A:** Not in this phase - malformed fences degrade gracefully (rest of doc becomes protected)

---

## Design Decisions

**Decision:** Segment parser runs first, then fixes operate on segments
**Rationale:** Clean separation of concerns, testable in isolation

**Decision:** Segment model includes `start_line` for error reporting
**Rationale:** Preserves line numbers for `MarkdownInnerFenceError` context

**Decision:** `fix_markdown_code_blocks` operates on flattened output
**Rationale:** It needs full document view to detect/fix nesting, runs after other fixes

**Decision:** Backtick space quoting is separate fix function
**Rationale:** New concern, add to pipeline rather than modify existing functions

---

## File Impact

**Modified:**
- `src/claudeutils/markdown.py` (~100 lines added for segment parsing)
- `tests/test_markdown.py` (~19 new tests)

**New:**
- None (all changes in existing files)

**Documentation:**
- Update `agents/DESIGN_DECISIONS.md` with segment architecture
- Update `agents/TEST_DATA.md` with segment examples
