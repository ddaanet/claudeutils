# Root Cause Analysis: Markdown Formatter Bugs

## Executive Summary

Three critical bugs in the markdown preprocessor are causing widespread file corruption:

1. **YAML Prolog Detection Failure** - Pattern requires trailing space, doesn't match nested structures
2. **Catastrophically Over-Aggressive Prefix Detection** - Matches regular prose, YAML keys, block quotes
3. **Secondary Effects** - YAML content falls through to prefix detection, creating cascading failures

**Impact:** 27 files corrupted when running `just format`

---

## Bug #1: YAML Prolog Detection Failure

### Location
`src/claudeutils/markdown.py:135-136`

### Current Implementation
```python
# Check for key: value pattern (identifier-colon-space)
if re.match(r"^\w+:\s", current_stripped):
    has_key_value = True
```

### Problems

**Problem 1A: Pattern requires trailing space**
- Pattern: `r"^\w+:\s"` requires whitespace after colon
- YAML keys without values (nested structures) don't match:
  ```yaml
  tier_structure:    # NO SPACE - doesn't match pattern
    critical:        # NO SPACE - doesn't match pattern
      - value
  ```
- Result: `has_key_value` stays False, prolog not recognized

**Problem 1B: Pattern doesn't match user requirements**
- User says: "must accept underscore in any position and digits in any position except first"
- `\w+` matches `[a-zA-Z0-9_]` (includes underscore, digits)
- BUT digits can't be first character in `\w+` if we want to be strict
- Should be: `r"^[a-zA-Z_][a-zA-Z0-9_]*:"` (explicit: letter or underscore first, then any combo)

**Problem 1C: Indented nested YAML content**
- YAML sections like:
  ```yaml
  ---
  tier_structure:
    critical:
      - item
  ```
- Line `"  critical:"` (indented) is stripped to `critical:`, doesn't match pattern
- Even if pattern fixed, indented content won't trigger `has_key_value = True`

### Evidence From Diff

```diff
 ---
-tier_structure:
-  critical:
+- tier_structure:
+- critical:
     - stop_on_unexpected
```

**Analysis:**

1. YAML prolog `---` to next `---` not recognized
2. Content falls through to plain text processing
3. `extract_prefix()` sees `tier_structure:` and `critical:` as colon-prefixed lines
4. Both lines converted to list items with `"- "` prefix
5. YAML structure completely broken

### Correct Fix

```python
# Check for key: value pattern or standalone key
# Accepts: "key: value", "key:", "key_name:", "key-name:", "key123:" (but not "123key:")
# Pattern allows underscores, hyphens, and digits except as first character
if re.match(r"^[a-zA-Z_][\w-]*:", current_stripped):
    has_key_value = True
```

**Changes:**
- Remove `\s` requirement (allow keys without values)
- Explicit first char: `[a-zA-Z_]` (letter or underscore, no digits/hyphens)
- Remaining chars: `[\w-]*` (zero or more: letters, digits, underscores, hyphens)
- Matches: `tier_structure:`, `author_model:`, `semantic_type:`, `_private:`, `semantic-type:`, `key123:`, etc.
- Rejects: `123key:` (digit first), `-key:` (hyphen first), `@key:` (special char), etc.

---

## Bug #2: Catastrophically Over-Aggressive Prefix Detection

### Location
`src/claudeutils/markdown.py:447`

### Current Implementation
```python
match = re.match(r"^(\S+(?:\s|:))", stripped)
if match:
    return match.group(1).rstrip()
```

### Problem

**Pattern matches EVERYTHING**

The pattern `r"^(\S+(?:\s|:))"` means: "Match one or more non-whitespace characters followed by a space OR colon"

This matches:
- ✅ **Intended:** `✅ Task` → prefix `✅`
- ✅ **Intended:** `[TODO]` → prefix `[TODO]` (but pattern doesn't actually match this - `]` is not `" "` or `:`)
- ❌ **Regular prose:** `Task agent` → prefix `Task`
- ❌ **YAML keys:** `tier_structure:` → prefix `tier_structure:`
- ❌ **Block quotes:** `> Your` → prefix `>`
- ❌ **Tree diagrams:** `├─ fix` → prefix `├─`
- ❌ **Section headers:** `Use Read` → prefix `Use`
- ❌ **Bold text:** `**Label:**` → prefix `**Label:**` (caught by other checks, but still problematic)

### Evidence From Diff

**Example 1: Regular Prose Converted to List**
```diff
 ## Scope Analysis: Main Prompt vs Task Agent

-Task agent prompt is a **minimal replacement** for the main system prompt. Rules NOT in
-Task agent are effectively "interactive-only" in default Claude Code.
+- Task agent prompt is a **minimal replacement** for the main system prompt. Rules NOT in
+- Task agent are effectively "interactive-only" in default Claude Code.
```

**Analysis:**

1. Line 1 starts with "Task agent"
2. Line 2 starts with "Task agent"
3. `extract_prefix()` extracts "Task " from both lines (word + space)
4. `is_similar_prefix()` sees both end with `:` (FALSE) → checks if both are colon-prefix (TRUE - both end with implicit word boundary)
5. Wait, let me re-check the logic...

Actually, looking at `is_colon_prefix()` at line 466:
```python
def is_colon_prefix(prefix: str) -> bool:
    return prefix.endswith(":")
```

The prefix "Task " doesn't end with ":", so it wouldn't match colon-prefix. Let me check the other matchers:

```python
def is_emoji_prefix(prefix: str) -> bool:
    return bool(re.match(r"^[^\w\s\[\(\{\-\*]", prefix))

def is_bracket_prefix(prefix: str) -> bool:
    return prefix.startswith("[")
```

"Task " doesn't match emoji or bracket either. So how are they being grouped?

Oh! At line 456-457:
```python
if p1 == p2:
    return True
```

Both lines have prefix "Task " (exact match), so they're considered similar! The categorization (emoji, bracket, colon) is only for cross-prefix matching.

So the logic is:

1. Extract prefix "Task " from line 1
2. Extract prefix "Task " from line 2
3. `p1 == p2` → TRUE → similar
4. Convert both to list items

This confirms the prefix detection is way too broad.

**Example 2: Block Quotes Converted to Lists**
```diff
-> Your subagent's system prompt goes here. This can be multiple paragraphs and should
-> clearly define the subagent's role, capabilities, and approach to solving problems.
+- > Your subagent's system prompt goes here. This can be multiple paragraphs and should
+- > clearly define the subagent's role, capabilities, and approach to solving problems.
```

**Analysis:**

1. Both lines start with `"> "` (block quote marker)
2. `extract_prefix()` extracts `>` (non-whitespace followed by space)
3. Both have same prefix `>` → similar
4. Converted to list items, breaking block quote formatting

**Example 3: Tree Diagrams Converted to Lists**
```diff
 Claude generates markdown
   ↓
 markdown.py preprocessor (fix structure)
-  ├─ fix_dunder_references
-  ├─ fix_metadata_blocks
-  ├─ fix_warning_lines (extended)
+- ├─ fix_dunder_references
+- ├─ fix_metadata_blocks
+- ├─ fix_warning_lines (extended)
```

**Analysis:**

1. Lines start with `"├─ "` (tree branch symbol)
2. `extract_prefix()` extracts `├─` (non-whitespace followed by space)
3. All have same prefix `├─` → similar
4. Converted to list items, breaking tree structure

### Correct Fix Strategy

**Principle:** Only match patterns that Claude ACTUALLY generates as pseudo-lists, not valid markdown or prose

**Patterns to Match (Intended):**
- Emoji prefixes: `✅ Task`, `❌ Failed`, `⚠️ Warning`
- Bracket prefixes: `[TODO] Item`, `[NOTE] Something`
- Maybe uppercase word + colon: `NOTE: Something`, `WARNING: Issue`

**Patterns to EXCLUDE (Not prefixes):**
- Regular prose: `Task agent`, `Use Read`
- Block quotes: `> quote text`
- Tree diagrams: `├─ item`, `└─ item`, `│  item`
- YAML keys: `tier_structure:`, `author_model:`
- Section-like headers: `Implementation:`, `Strategy:`
- Indented content: `"  ├─ item"`

**Implementation Strategy:**

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
            return stripped[:-1] + ":"  # Return with colon
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

1. Explicit exclusions for block quotes, tree symbols, section headers
2. Only match emojis (specific character class)
3. Only match brackets (explicit pattern)
4. Only match uppercase word + colon (not any word + colon)
5. Much more conservative - when in doubt, return None

---

## Bug #3: Secondary Effects

### Evidence From Diff

**Example: Bold Labels Excluded**

Phases 1-2 already added exclusions for:
- Tables: Lines starting with `|` and containing 2+ `|` chars (line 444-445)
- Bold labels: `**Label:**` patterns (handled by `fix_metadata_blocks`)

These exclusions are working, but the YAML and prose issues remain.

---

## Test Requirements

### Understanding the Protection Model

**Key Concept:** Content is divided into segments

- **Protected segments (processable=False):** YAML prologs, fenced code blocks
  - YAML between `---` delimiters should be protected
  - Code in `` ```python ``, `` ```yaml ``, etc. should be protected
  - ASCII diagrams should be in fenced blocks → protected
- **Processable segments (processable=True):** Plain markdown text
  - Only these segments are processed by `fix_warning_lines()` and other fixes

**Why Bugs Happen:**

1. YAML prolog detection fails → YAML becomes plain text → gets mangled
2. Prefix detection too broad → plain markdown text gets mangled

**Fix Strategy:**

1. Fix segment detection (Phase 5) → protect more content correctly
2. Fix prefix detection (Phase 6) → defensive, handle edge cases

---

### Unit Tests Needed

**Test 1: YAML Prolog with Underscores (Segment Parser)**
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
    assert segments[0].processable == False
    assert segments[0].language == "yaml-prolog"
```

**Test 2: YAML Prolog with Nested Keys (Segment Parser)**
```python
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
    assert segments[1].processable == True
    # YAML keys like tier_structure: are protected inside the prolog segment
    # They won't be processed by fix_warning_lines()
```

**Test 3: Regular Prose Not Converted (Prefix Detection)**
```python
def test_prose_not_converted_to_list():
    """Regular prose should not be converted to list items.

    Tests defensive behavior - prose appears in plain markdown text,
    should not be matched by prefix detection.
    """
    lines = [
        "Task agent prompt is a **minimal replacement**.\n",
        "Task agent are effectively \"interactive-only\".\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes
```

**Test 4: Block Quotes Not Converted (Prefix Detection)**
```python
def test_block_quotes_not_converted():
    """Block quotes should not be converted to list items.

    Tests defensive behavior - block quotes appear in plain markdown text,
    should not be matched by prefix detection.
    """
    lines = [
        "> Your subagent's system prompt goes here.\n",
        "> clearly define the role.\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes
```

**Test 5: Tree Diagrams Not Converted (Defensive)**
```python
def test_tree_diagrams_not_converted():
    """Tree diagrams should not be converted to list items.

    Note: These should ideally be in fenced blocks, but this tests
    defensive behavior if they appear in plain text.
    """
    lines = [
        "  ├─ fix_dunder_references\n",
        "  ├─ fix_metadata_blocks\n",
        "  └─ fix_warning_lines\n",
    ]
    result = fix_warning_lines(lines)
    assert result == lines  # No changes
```

**Note:** Tree diagrams and ASCII art SHOULD be in fenced code blocks (protected segments). This test is defensive - it ensures that if they somehow appear in plain text, they won't be mangled. The real fix is to ensure content is properly segmented.

**Test 6: Emoji Prefixes Still Work**
```python
def test_emoji_prefixes_converted():
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

---

## Implementation Plan

### Phase 1: Fix YAML Prolog Detection (CRITICAL)

**File:** `src/claudeutils/markdown.py:135`

**Change:**
```python
# OLD:
if re.match(r"^\w+:\s", current_stripped):
    has_key_value = True

# NEW:
if re.match(r"^[a-zA-Z_][\w-]*:", current_stripped):
    has_key_value = True
```

**Impact:**
- Fixes YAML keys with underscores: `author_model:`, `semantic_type:`
- Fixes YAML keys with hyphens: `semantic-type:`, `author-model:`
- Fixes YAML keys with digits: `key123:`, `option_2:`
- Fixes YAML nested keys without values: `tier_structure:`, `critical:`
- Prevents YAML content from falling through to prefix detection

**Risk:** Low - more permissive pattern, only adds valid matches

---

### Phase 2: Fix Prefix Detection (CRITICAL)

**File:** `src/claudeutils/markdown.py:431-450`

**Replace entire `extract_prefix()` function with conservative implementation**

**Impact:**
- Stops matching regular prose ("Task agent")
- Stops matching block quotes ("> text")
- Stops matching tree diagrams ("├─ item")
- Still matches emoji prefixes ("✅ Task")
- Still matches bracket prefixes ("[TODO] Item")

**Risk:** Medium - complete rewrite, needs thorough testing

---

### Phase 3: Add Unit Tests

**File:** `tests/test_markdown.py`

**Add 6 new tests** (see Test Requirements above)

**Impact:**
- Validates YAML prolog detection
- Validates prefix exclusions
- Validates emoji prefixes still work

**Risk:** Low - tests only, no behavior changes

---

### Phase 4: Integration Testing

**Process:**

1. Revert corrupted files: `git checkout HEAD -- .`
2. Run unit tests: `just test tests/test_markdown.py`
3. Run formatter: `just format`
4. Check diff: `git diff`
5. Verify: Should show minimal or NO changes to 27 previously corrupted files

**Success Criteria:**
- All unit tests pass
- `just format` produces minimal/no diffs on AGENTS.md, START.md, session.md
- Tables remain as tables
- Block quotes remain as block quotes
- YAML prologs protected
- Regular prose unchanged

---

## Risk Assessment

**High Risk:**
- `extract_prefix()` rewrite could break existing functionality
- Need comprehensive testing of emoji/bracket prefix detection

**Medium Risk:**
- YAML prolog pattern change could have edge cases
- Need to test with various YAML structures

**Low Risk:**
- Unit tests are additive, no risk to functionality

---

## Rollback Plan

If fixes cause issues:

1. Revert `extract_prefix()` changes
2. Revert YAML prolog pattern changes
3. Add explicit exclusions only (block quotes, tree symbols) as hotfix
4. Reassess approach

---

## Summary

**Root Causes:**

1. YAML prolog pattern too restrictive (requires trailing space)
2. Prefix detection pattern too permissive (matches everything)
3. Cascading failures from #1 → #2

**Fix Strategy:**

1. Loosen YAML pattern (accept keys without values)
2. Tighten prefix pattern (explicit inclusions, explicit exclusions)
3. Comprehensive testing

**Confidence:** High - root causes identified, fix strategy validated against evidence
