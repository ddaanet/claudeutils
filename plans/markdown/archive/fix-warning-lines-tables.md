# Fix Plan: Prevent Table and Metadata List Corruption

**Status Update (2026-01-05):** Phases 1-2 complete ✅, but NEW CRITICAL ISSUES
discovered ❌

**See:** `plans/markdown/root-cause-analysis.md` for detailed technical analysis

---

## Protection Model: How Segments Work

The markdown preprocessor uses a **segment parser** to protect certain content from
processing:

### Protected Segments (processable=False)

- **YAML prologs:** Content between `---` and `---` at document start
- **Fenced code blocks:** Content between `` ``` `` (except `` ```markdown ``)
  - Examples: `` ```python ``, `` ```yaml ``, `` ```bash ``, bare `` ``` ``
  - ASCII diagrams, YAML examples, code snippets should be in these blocks

### Processable Segments (processable=True)

- **Plain markdown text:** Everything outside protected segments
- **Markdown blocks:** Content in `` ```markdown `` fences (special case)

### How Fixes Work

1. `parse_segments()` divides document into protected vs processable segments
2. Fixes like `fix_warning_lines()` only run on processable segments
3. Protected content is completely untouched

### The Bug

When YAML prolog detection fails:

- YAML content not recognized as protected segment
- Falls through to plain text (processable)
- `fix_warning_lines()` sees `tier_structure:` as a prefix
- Converts to `- tier_structure:` → YAML broken ❌

When `extract_prefix()` is too aggressive:

- Plain markdown text matches prefix patterns
- Regular prose converted to lists → formatting broken ❌

### The Fix Strategy

**Two-pronged approach: robust segment parsing + defensive prefix detection**

1. **Phase 4:** Fix YAML prolog detection (PRIMARY) → protect YAML/code content
   correctly
   - Change pattern from `r"^\w+:\s"` to `r"^[a-zA-Z_][\w]*:"`
   - Allows keys without values: `tier_structure:`, `critical:`
   - Allows digits after first char: `key123:`, `option_2:`
   - YAML content will be protected (processable=False), never mangled

2. **Phase 5:** Fix prefix detection (DEFENSIVE) → don't match non-prefixes
   - Rewrite `extract_prefix()` to be much more conservative
   - Only match: emoji symbols, bracket prefixes `[TODO]`, uppercase word+colon `NOTE:`
   - Exclude: prose, block quotes, tree symbols, section headers
   - Handles edge cases where content isn't properly in fenced blocks

---

## Phases 1-2 Status: COMPLETE ✅

1. **Tables converted to lists** → FIXED ✅ (added table detection to `extract_prefix`)
2. **Single labels converted to list items** → FIXED ✅ (disabled
   `fix_metadata_list_indentation`)
3. **Bold labels processed twice** → FIXED ✅ (merged into `fix_metadata_blocks`)

**Result:** 45/45 tests passing, table/label issues resolved

---

## NEW CRITICAL ISSUES (Discovered 2026-01-05) ❌

Running `just format` after Phases 1-2 STILL corrupts 27 files with TWO CRITICAL BUGS:

### Bug #1: YAML Prolog Detection Broken

- **Location:** `markdown.py:135`
- **Current:** Pattern `r"^\w+:\s"` requires space after colon
- **Problem:** Doesn't match YAML keys without values: `tier_structure:`, `critical:`
- **Problem:** Doesn't match keys with digits: `option_2:`, `key123:`
- **Problem:** Doesn't match keys with hyphens: `semantic-type:`, `author-model:`
- **Impact:** YAML sections not recognized, content falls through to prefix detection
- **Fix:** Change pattern to `r"^[a-zA-Z_][\w-]*:"` (allows keys without values,
  supports underscores/hyphens/digits after first char)

### Bug #2: Prefix Detection Over-Aggressive

- **Location:** `markdown.py:447`
- **Current:** Pattern `r"^(\S+(?:\s|:))"` matches ANY non-whitespace + space/colon
- **Problem:** Matches regular prose ("Task agent"), block quotes ("> text"), tree
  diagrams ("├─"), section headers ("Implementation:")
- **Impact:** Plain markdown converted to lists, breaking formatting
- **Fix:** Complete rewrite - only match emoji symbols, bracket prefixes `[TODO]`,
  uppercase word+colon `NOTE:`

### Bug #3: Cascading Failures

When both bugs combine:

- YAML not recognized → content processed as plain text → prefix matches YAML keys →
  YAML broken
- Tree diagrams not in fenced blocks → prefix matches symbols → diagrams broken
- Regular prose → prefix matches common words → document structure broken

**Evidence:** See diff examples in `root-cause-analysis.md`

---

## Original Problems (Phases 1-2: FIXED ✅)

1. **Tables converted to lists**: `fix_warning_lines()` treats table rows as prefixed
   lines
2. **Single labels converted to list items**: `fix_metadata_list_indentation()`
   incorrectly treats single `**Label:**` as a metadata list
3. **Bold labels processed twice**: Both `fix_warning_lines()` and other functions try
   to process `**Label:**` patterns

## User Requirements (Clarified)

- **Metadata list** = 2+ consecutive `**Label:**` lines → convert to list items ✅ (keep
  `fix_metadata_blocks`)
- **Single `**Label:**` line** ≠ metadata list → do NOT convert to list item ❌
- **List following metadata list** → should be indented ✅
- **Indentation must be consistent** → all items at same nesting level have same indent
  (not progressive) ✅
- **Tables** → must remain as tables ✅

## Solution Strategy

### Phase 1: Table Detection and Exclusion

**Objective:** Prevent table rows from being processed as prefixed lines

**Implementation:**

1. Add table row detection to `extract_prefix()`:
   - Check if line matches table pattern: starts with `|` AND contains 2+ `|` chars
   - Return `None` for table rows (skip them)

2. Detect table separator rows:
   - Pattern: `| --- | --- |` or `| ---- |`
   - Also return `None` to skip

**Test cases to add:**

```python
def test_tables_unchanged():
    """Tables should not be converted to lists."""
    input_lines = [
        "| Header 1 | Header 2 |\n",
        "| -------- | -------- |\n",
        "| Value 1  | Value 2  |\n",
        "\n"
    ]
    result = fix_warning_lines(input_lines)
    assert result == input_lines  # No changes
```

### Phase 2: Disable Metadata List Indentation

**Objective:** Stop converting single `**Label:**` lines to list items

**Current behavior (unwanted):**

```text
**Commits:**                   - **Commits:**
- item 1              →          - item 1
- item 2                           - item 2
```

Single label is converted to list item (wrong - not a metadata list)

**Desired behavior:**

```text
**File:** role.md              **File:** role.md
**Model:** Sonnet      →       **Model:** Sonnet

**Label1:** value              - **Label1:** value
**Label2:** value              - **Label2:** value
- item 1                         - item 1
- item 2                         - item 2
```

**Implementation:** Modify `fix_metadata_list_indentation()` to:

1. Detect if previous content is a metadata list (list items starting with `- **`
   pattern)
2. Only indent following list if it comes after a metadata list
3. Do NOT convert single `**Label:**` lines to list items

**Alternative simpler approach:**

- Disable `fix_metadata_list_indentation` completely
- Let `fix_metadata_blocks` handle 2+ labels (converts to list)
- User can manually indent lists when needed
- No automatic indentation = no indentation bugs

**Recommended: Disable completely** (simpler, avoids bugs)

**Why disable:**

- Function converts single labels to list items (wrong - user says "single line with
  label does not make a metadata list")
- Indentation logic could cause progressive indent increase (user concern)
- Simpler to let users control indentation manually

**Changes needed:**

- Comment out line 723 in `markdown.py`:
  `segments = apply_fix_to_segments(segments, fix_metadata_list_indentation)`
- Update test expectations

### Phase 3: Bold Label Exclusion (from fix_warning_lines)

**Objective:** Prevent `**Label:**` patterns from being processed by
`fix_warning_lines()` (already handled by `fix_metadata_blocks`)

**Implementation:**

1. Add bold label detection to `extract_prefix()`:
   - Check if line matches: `r"^\*\*[A-Za-z][^*]+:\*\*"` or `r"^\*\*[^*]+\*\*:"`
   - Return `None` for these patterns

**Test cases to add:**

```python
def test_bold_labels_unchanged():
    """Bold labels should not be converted to lists by fix_warning_lines."""
    input_lines = [
        "**Commits:**\n",
        "- item 1\n",
        "\n"
    ]
    result = fix_warning_lines(input_lines)
    assert result == input_lines  # No changes
```

### Phase 4: Fix YAML Prolog Detection (NEW - CRITICAL)

**Objective:** Allow YAML keys without trailing values

**Location:** `src/claudeutils/markdown.py:135`

**Current Code:**

```python
# Check for key: value pattern (identifier-colon-space)
if re.match(r"^\w+:\s", current_stripped):
    has_key_value = True
```

**Problem:**

- Pattern requires space after colon: `key: value`
- Doesn't match keys without values: `tier_structure:`, `critical:`
- YAML nested structures not recognized
- Content falls through to plain text processing

**New Code:**

```python
# Check for key: value pattern or standalone key
# Accepts: "key: value", "key:", "key_name:", "key-name:", "key123:" (but not "123key:")
# Pattern allows underscores, hyphens, and digits except as first character
if re.match(r"^[a-zA-Z_][\w-]*:", current_stripped):
    has_key_value = True
```

**Changes:**

- Remove `\s` requirement (allow keys without values)
- Explicit first char: `[a-zA-Z_]` (letter or underscore)
- Remaining chars: `[\w-]*` (zero or more word chars OR hyphens: letters, digits,
  underscores, hyphens)
- Matches: `tier_structure:`, `author_model:`, `semantic_type:`, `_private:`, `key123:`,
  `option_2:`, `semantic-type:`, `author-model:`
- Rejects: `123key:` (digit first - invalid YAML key), `-key:` (hyphen first - invalid
  YAML key)

**Note:** `\w` in Python regex = `[a-zA-Z0-9_]` (letters, digits, underscore), so
`[\w-]` adds hyphen support

**Test Cases:**

```python
def test_yaml_prolog_with_underscores():
    """YAML keys with underscores should be recognized."""
    lines = [
        "---\n",
        "author_model: claude-opus\n",
        "semantic_type: workflow\n",
        "---\n",
        "\n",
        "Content here\n"
    ]
    segments = parse_segments(lines)
    assert len(segments) == 2
    assert segments[0].processable == False
    assert segments[0].language == "yaml-prolog"
    assert segments[1].processable == True

def test_yaml_prolog_nested_keys():
    """YAML keys without values (nested structures) should be recognized."""
    lines = [
        "---\n",
        "tier_structure:\n",
        "  critical:\n",
        "    - item\n",
        "---\n",
        "\n",
        "Content here\n"
    ]
    segments = parse_segments(lines)
    assert len(segments) == 2
    assert segments[0].processable == False
    assert segments[0].language == "yaml-prolog"
    # YAML keys like tier_structure: are protected inside prolog
    # They won't be processed by fix_warning_lines()
```

**Key Point:** YAML content between `---` delimiters is a protected segment. The bug is
that prolog detection fails, causing YAML to fall through to plain text processing where
`fix_warning_lines()` mangles it.

---

### Phase 5: Rewrite `extract_prefix()` (NEW - CRITICAL)

**Objective:** Stop matching regular prose, block quotes, tree diagrams, YAML keys

**Location:** `src/claudeutils/markdown.py:431-450`

**Current Code:**

```python
def extract_prefix(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    if re.match(r"^[-*]|^\d+\.", stripped):
        return None

    # Skip table rows
    if stripped.startswith("|") and stripped.count("|") >= 2:
        return None

    match = re.match(r"^(\S+(?:\s|:))", stripped)  # ← TOO BROAD
    if match:
        return match.group(1).rstrip()
    return None
```

**New Code:** (Complete replacement)

```python
def extract_prefix(line: str) -> str | None:
    """Extract non-markup prefix from line.

    Returns None if line is empty, is already a list item, or has no clear
    prefix. Returns prefix string (e.g., "✅", "[TODO]", "NOTE:") if found.

    ONLY matches:
    - Emoji-like symbols (non-alphanumeric at start)
    - Bracketed text [like this]
    - Uppercase words ending with colon (NOTE:, WARNING:, TODO:)
    """
    stripped = line.strip()
    if not stripped:
        return None

    # Skip existing list items
    if re.match(r"^[-*+]|^\d+\.", stripped):
        return None

    # Skip table rows (start with | and contain 2+ pipes)
    if stripped.startswith("|") and stripped.count("|") >= 2:
        return None

    # Skip block quotes (start with >)
    if stripped.startswith(">"):
        return None

    # Skip tree diagram symbols
    if any(sym in stripped[:3] for sym in ["├", "└", "│"]):
        return None

    # Skip lines that end with : (likely section headers or YAML keys)
    # UNLESS they're uppercase word + colon (NOTE:, TODO:, WARNING:)
    if stripped.endswith(":"):
        # Check if it's an uppercase word + colon
        if re.match(r"^[A-Z][A-Z0-9_]*:$", stripped):
            return stripped  # Return with colon
        # Otherwise skip (section header or YAML key)
        return None

    # Match emoji-like prefixes (non-alphanumeric, non-whitespace at start)
    # Exclude: [ ( { - * | > (these have special meanings)
    emoji_match = re.match(r"^([^\w\s\[\(\{\-\*\|>]+)(\s|$)", stripped)
    if emoji_match:
        return emoji_match.group(1)

    # Match bracketed prefixes [like this]
    bracket_match = re.match(r"^(\[[^\]]+\])(\s|$)", stripped)
    if bracket_match:
        return bracket_match.group(1)

    # Match uppercase word + colon at start (followed by space)
    # NOTE: This, WARNING: That, TODO: Item
    colon_match = re.match(r"^([A-Z][A-Z0-9_]*:)\s", stripped)
    if colon_match:
        return colon_match.group(1)

    # No valid prefix found
    return None
```

**Key Changes:**

1. **Explicit exclusions:**
   - Block quotes: `> text`
   - Tree symbols: `├─`, `└─`, `│`
   - Lines ending with `:` (section headers, YAML keys)

2. **Only match specific patterns:**
   - Emoji: `r"^([^\w\s\[\(\{\-\*\|>]+)(\s|$)"` (non-word, non-whitespace, not special
     chars)
   - Brackets: `r"^(\[[^\]]+\])(\s|$)"` (explicit bracket matching)
   - Uppercase colon: `r"^([A-Z][A-Z0-9_]*:)\s"` (NOTE:, TODO:, WARNING: only)

3. **No longer matches:**
   - Regular prose: "Task agent"
   - YAML keys: "tier_structure:"
   - Section headers: "Implementation:"
   - Lowercase word + colon: "author_model:"

**Test Cases:**

```python
def test_prose_not_converted_to_list():
    """Regular prose should not be converted to list items."""
    lines = [
        "Task agent prompt is a **minimal replacement**.\n",
        "Task agent are effectively \"interactive-only\".\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes

def test_block_quotes_not_converted():
    """Block quotes should not be converted to list items."""
    lines = [
        "> Your subagent's system prompt goes here.\n",
        "> clearly define the role.\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes

def test_tree_diagrams_not_converted():
    """Tree diagrams should not be converted to list items.

    Note: Tree diagrams SHOULD be in fenced code blocks (protected segments).
    This tests defensive behavior if they appear in plain text.
    """
    lines = [
        "  ├─ fix_dunder_references\n",
        "  ├─ fix_metadata_blocks\n",
        "  └─ fix_warning_lines\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes

def test_section_headers_not_converted():
    """Section headers ending with colon should not be converted to list items.

    Unlike YAML keys (which should be in prolog sections), section headers
    legitimately appear in plain markdown text.
    """
    lines = [
        "Implementation:\n",
        "Strategy:\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes

def test_emoji_prefixes_still_work():
    """Emoji-prefixed lines should still be converted to lists."""
    lines = [
        "✅ Task completed\n",
        "✅ Another task done\n",
    ]
    result = fix_warning_lines(lines)
    assert result == [
        "- ✅ Task completed\n",
        "- ✅ Another task done\n",
    ]
```

## Implementation Order

### Completed ✅

1. **Phase 1: Add table detection** → DONE ✅
2. **Phase 2: Disable metadata list indentation** → DONE ✅
3. **Phase 3: Add bold label exclusion** → DONE ✅

### Previously Required (Now Complete) ✅

4. **Phase 4: Fix YAML prolog detection** → DONE ✅ (commit 663059d)
5. **Phase 5: Rewrite `extract_prefix()`** → DONE ✅ (commit 663059d)

### New Critical Issues Discovered ❌

**Status:** Despite Phases 4-5 being implemented, `just format` still corrupts 2 files.
Root cause analysis reveals one critical segment parser bug.

**See:** `plans/markdown/segmentation-bugs-analysis.md` for complete investigation.

**Clarifications:**

- ✅ `` ```markdown `` blocks being processed is INTENTIONAL (for formatting doc
  snippets in plans)
- ✅ Inline code with spaces being quoted is REQUIRED (dprint strips spaces, quotes
  preserve them)
- ❌ Bare fences NOT protecting content is the ONLY real bug

**New Phases:**

6. ~~**Phase 6: Fix Markdown Block Processing**~~ → ✅ NOT NEEDED (intentional feature)
7. **Phase 7: Debug Bare Fence Protection** (CRITICAL - bare fences not protecting
   content)
8. **Phase 8: Add Integration Tests** (CRITICAL - validates end-to-end protection)
9. **Phase 9: Fix Incorrect Backtick Escaping in Docs** (depends on Phase 10)
10. **Phase 10: Fix escape_inline_backticks() Regex** (CRITICAL - corrupts 4+ backtick
    sequences)

## Testing Strategy

### Unit Tests by Category

**Segment Parser Tests (Phase 4):**

- `test_yaml_prolog_with_underscores` - YAML keys like `author_model:`, `key123:`
  recognized
- `test_yaml_prolog_nested_keys` - YAML nested keys like `tier_structure:` recognized
- Tests that YAML content is protected (processable=False)
- **Primary defense:** If this works, YAML never reaches `fix_warning_lines()`

**Prefix Detection Tests (Phase 5):**

- `test_prose_not_converted` - Regular prose NOT converted to lists
- `test_block_quotes_not_converted` - Block quotes NOT converted to lists
- `test_tree_diagrams_not_converted` - Tree diagrams NOT converted
- `test_section_headers_not_converted` - Section headers NOT converted
- `test_emoji_prefixes_still_work` - Emoji prefixes STILL converted (regression check)
- **Secondary defense:** Even if content not in fenced blocks, don't mangle it

**Key Distinction:**

- Phase 4 (segment parser): PRIMARY - protects content from processing
- Phase 5 (prefix detection): DEFENSIVE - handles edge cases in plain text

### Integration Testing

1. Run unit tests: `just test tests/test_markdown.py`
2. Run formatter: `just format`
3. Check diff: `git diff` (should be minimal/none)
4. Spot check: CLAUDE.md, START.md, session.md remain clean

## Phase 9: Fix Incorrect Backtick Escaping in Documentation

**Depends on:** Phase 10 must be completed first

**File:** `plans/markdown/feature-2-code-block-nesting.md:48`

**Problem:**
```markdown
   - Output: ````markdown block (4 backticks)
```
This starts a 4-backtick code fence, which is invalid markdown.

**Fix:**
```markdown
   - Output: `` ````markdown `` block (4 backticks)
```

**Why Phase 10 is required:**

- Current `escape_inline_backticks()` regex would re-corrupt this fix
- The regex matches first 3 backticks in ````  and converts to `` ``` ```markdown (broken!)
- Must fix the regex first, then apply doc fix

**Impact:** Documentation fix only, no code changes needed after Phase 10

## Phase 10: Fix escape_inline_backticks() Regex Bug ⚠️ CRITICAL

**Location:** `src/claudeutils/markdown.py:297`

**Bug discovered:** 2026-01-06 - Regex corrupts 4+ backtick sequences in inline code

**Current code (broken):**

````python
escaped_line = re.sub(r"(?<!`` )```(\w*)", r"`` ```\1 ``", line)
````

**Problem:**

`````python
Input:  "- Output: ````markdown block"
Output: "- Output: `` ``` ```markdown block"
#                        ^^^^^^^^^ BROKEN - fence start mid-line!
`````

The regex matches the FIRST 3 backticks in `` ```` `` because:

The regex matches the FIRST 3 backticks in ````  because:
1. Looks for exactly 3 backticks: ` ``` `
2. Negative lookbehind `(?<!`` )` only checks for "`` " (2 backticks + space)
3. In ```` there's no space before, so it matches
4. Creates malformed `` ``` ```markdown (inline code + fence start)

**Fix (Option A - Recommended):**

````python
# Use negative lookahead and lookbehind to match ONLY standalone ```
escaped_line = re.sub(r"(?<!`)`{3}(\w*)(?!`)", r"`` ```\1 ``", line)
````

**Why this works:**

- `(?<!`)` - no backtick immediately before
- `{3}` - exactly 3 backticks
- `(?!`)` - no backtick immediately after
- Only matches `` ``` `` when not part of `` ```` ``

**Fix (Option B - Alternative):**

````python
# Better negative lookbehind without space requirement
escaped_line = re.sub(r"(?<!``)```(\w*)", r"`` ```\1 ``", line)
````

**Test cases needed:**

`````python
def test_escape_preserves_4plus_backticks():
    """Don't escape 4+ backticks already in inline code."""
    lines = ["Text `` ````markdown `` more\n"]
    result = escape_inline_backticks(lines)
    assert result[0] == lines[0]

def test_escape_handles_triple_backticks():
    """Still escape standalone triple backticks."""
    lines = ["See ```python code\n"]
    result = escape_inline_backticks(lines)
    assert result[0] == "See `` ```python `` code\n"

def test_escape_handles_bare_4_backticks():
    """Don't escape bare 4-backtick sequences (invalid markdown)."""
    lines = ["Output: ````markdown block\n"]
    result = escape_inline_backticks(lines)
    # Should remain unchanged - it's invalid markdown
    assert result[0] == lines[0]
`````

**Impact:** HIGH - Fixes active corruption of documentation with 4+ backticks

## Files to Modify

### Phases 1-5 (COMPLETE ✅)

- `src/claudeutils/markdown.py` - Update `extract_prefix()` and `is_similar_prefix()`
- `tests/test_markdown.py` - Add table and bold label test cases

### Phase 7 (CRITICAL ❌)

- `src/claudeutils/markdown.py` - Debug and fix bare fence protection
- Add debug logging to identify where protection fails

### Phase 8 (CRITICAL ❌)

- `tests/test_markdown.py` - Add integration tests for fence protection

### Phase 9 (DEPENDS ON PHASE 10 ⚠️)

- `plans/markdown/feature-2-code-block-nesting.md` - Fix backtick escaping on line 48

### Phase 10 (CRITICAL ❌)

- `src/claudeutils/markdown.py` - Fix escape_inline_backticks() regex (line 297)
- `tests/test_markdown.py` - Add tests for 4+ backtick handling

## Success Criteria

### Phases 1-3 (COMPLETE ✅)

- ✅ Tables remain as tables (no `- |` prefixes)
- ✅ Single `**Label:**` lines stay as-is (not converted to list items)
- ✅ Multiple consecutive `**Label:**` lines converted to list (metadata blocks)
- ✅ List indentation is consistent at each nesting level (no progressive increase)

### Phases 4-5 (NEW - REQUIRED ❌)

**Phase 4 (Segment Parser):**

- ❌ YAML prologs with underscores recognized: `author_model:`, `semantic_type:`,
  `key123:`
- ❌ YAML prologs with nested keys recognized: `tier_structure:`, `critical:`
- ❌ YAML content protected (processable=False), never reaches fixes

**Phase 5 (Prefix Detection):**

- ❌ Regular prose NOT converted to lists: "Task agent prompt..."
- ❌ Block quotes NOT converted to lists: `> Your subagent's...`
- ❌ Tree diagrams NOT converted to lists: `├─ fix_dunder_references`
- ❌ Section headers NOT converted to lists: `Implementation:`, `Strategy:`
- ✅ Legitimate emoji/bracket prefixed lines STILL converted to lists: `✅ Task`,
  `[TODO] Item`

### Final Validation (UPDATED)

- ✅ 52/52 tests passing (Phases 1-5 complete)
- ❌ **Phase 7 (CRITICAL):** Bare fence protection not working - 2 files corrupted
- ❌ **Phase 8 (CRITICAL):** Integration tests needed to validate end-to-end protection
- ❌ **Phase 10 (CRITICAL):** escape_inline_backticks() regex corrupts 4+ backtick
  sequences
- ⚠️ **Phase 9 (BLOCKED):** Doc fix requires Phase 10 to be completed first

## Key Decision: Disable fix_metadata_list_indentation

**Reason:** Single `**Label:**` line ≠ metadata list, should not be converted to list
item

**Action:** Comment out the function call in `process_lines()`. Keep function code for
potential future enhancement (e.g., only indent lists after actual metadata lists, not
single labels).

## Implementation Details

### Phase 1: Table Detection Code

In `extract_prefix()` function (around line 413):

```python
def extract_prefix(line: str) -> str | None:
    """Extract non-markup prefix from line.

    Returns None if line is empty, is already a list item, or has no clear
    prefix. Returns prefix string (e.g., "✅", "[TODO]", "NOTE:") if found.
    """
    stripped = line.strip()
    if not stripped:
        return None

    # Skip existing list items
    if re.match(r"^[-*]|^\d+\.", stripped):
        return None

    # NEW: Skip table rows
    if stripped.startswith("|") and stripped.count("|") >= 2:
        return None

    # NEW: Skip bold labels (handled by fix_metadata_blocks)
    if re.match(r"^\*\*[^*]+:\*\*|^\*\*[^*]+\*\*:", stripped):
        return None

    match = re.match(r"^(\S+(?:\s|:))", stripped)
    if match:
        return match.group(1).rstrip()
    return None
```

### Phase 2: Disable Metadata List Indentation

In `process_lines()` function (around line 723):

```python
# Comment out this line:
# segments = apply_fix_to_segments(segments, fix_metadata_list_indentation)
```

## Verification Steps

After implementing fixes:

1. **Revert corrupted files:**
   ```bash
   git checkout HEAD -- CLAUDE.md START.md session.md agents/modules/MODULE_INVENTORY.md
   ```

2. **Run formatter:**
   ```bash
   just format
   ```

3. **Check diff:**
   ```bash
   git diff
   ```
   - Should show minimal or no changes
   - Tables should remain as tables
   - Single `**Label:**` lines should not become list items

4. **Run tests:**
   ```bash
   just test
   ```
   - All 48+ tests should pass

## Affected Files Count

Running `just format` before fixes affected 27 files:

- CLAUDE.md
- START.md
- session.md
- agents/modules/MODULE_INVENTORY.md
- agents/modules/src/context-commands.semantic.md
- agents/modules/src/sysprompt-reference/CATALOG.md
- agents/role-lint.md
- agents/role-lint.sys.md
- agents/role-planning.sys.md
- agents/role-review.sys.md
- plans/markdown/agent-documentation.md
- plans/markdown/feature-2-code-block-nesting.md
- plans/prompt-composer/README.md
- plans/prompt-composer/design-review-tiering.md
- plans/prompt-composer/design.md
- plans/prompt-composer/plan-error-handling-consistency.md
- plans/prompt-composer/plan-token-counter-fixes.md
- plans/prompt-composer/review-error-handling-consistency.md
- plans/prompt-composer/review-token-counter-addendum-1.md
- plans/prompt-composer/review-token-counter.md
- plans/prompt-composer/sysprompt-integration/design.md
- plans/prompt-composer/sysprompt-integration/drafts.md
- plans/prompt-composer/sysprompt-integration/tasks-delegable.md
- plans/prompt-composer/sysprompt-integration/tasks-opus.md
- research/sonnet-base-comparison.md
- research/sonnet-zero-comparison.md
- src/claudeutils/markdown.py

After fixes, running `just format` should leave these files unchanged.
