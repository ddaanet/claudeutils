# Segmentation Bugs Analysis

- **Date:** 2026-01-06
- **Status:** Formatter still corrupting files despite Phases 4-5 implementation
- **Branch:** markdown
- **Files Modified:** 7 files in plans/ directory

## Executive Summary

The segment parser is **fundamentally broken** - it's not protecting content inside code
fences as designed. Multiple critical bugs allow formatter functions to corrupt
protected content.

## Critical Bugs Identified

### Bug #1: `` ```markdown `` Blocks Marked as Processable

**Location:** `markdown.py:217`

**Code:**

```python
processable = open_lang == "markdown"
```

**Problem:**

- `` ```markdown `` blocks are intentionally marked as `processable=True`
- This causes ALL fixes to run on content inside `` ```markdown `` fences
- Documentation examples and test cases get corrupted

**Evidence:** In `plans/markdown/fix-warning-lines-tables.md:152-162`, content inside a
`` ```markdown `` fence:

````diff
 **Desired behavior:**
 ```markdown
-**File:** role.md              **File:** role.md
-**Model:** Sonnet      →       **Model:** Sonnet
+- **File:** role.md              **File:** role.md
+- **Model:** Sonnet      →       **Model:** Sonnet
````

The lines `**File:** role.md` and `**Model:** Sonnet` are being converted to list items
by `fix_metadata_blocks()`, even though they're inside a ```markdown fence.

**Impact:** HIGH - Corrupts all documentation with markdown examples

### Bug #2: Bare Fences Not Protected in Practice

**Location:** Unknown - segment parser logic issue

**Test Says:**

````python
def test_parse_segments_bare_fence_block() -> None:
    """Test: parse_segments detects bare ``` block as protected."""
    # ...
    assert result[0].processable is False
````

**Reality:** In `plans/markdown/agent-documentation.md:36-42`, content inside bare ```
fence:

```diff
 **Input:**

 ```
-✅ Issue #1: XPASS tests visible
-✅ Issue #2: Setup failures captured
-❌ Issue #3: Not fixed yet
+- ✅ Issue #1: XPASS tests visible
+- ✅ Issue #2: Setup failures captured
+- ❌ Issue #3: Not fixed yet
 ```
```

The emoji-prefixed lines are being converted to list items by `fix_warning_lines()`, despite being inside a bare fence.

**Impact:** HIGH - Corrupts examples and test data

### Bug #3: fix_backtick_spaces Running on Protected Content

**Location:** `markdown.py:785`, `markdown.py:556-587`

**Problem:**

- `fix_backtick_spaces()` adds quotes around inline code with leading/trailing spaces
- Function is applied via `apply_fix_to_segments()` which should only process
  processable segments
- But quotes are appearing in content that should be protected

**Evidence:** In `plans/markdown/root-cause-analysis.md:53`:

```diff
-- Line `  critical:` (indented) is stripped to `critical:`, doesn't match pattern
+- Line `"  critical:"` (indented) is stripped to `critical:`, doesn't match pattern
```

The inline code `` `  critical:` `` (with leading spaces) is being quoted as
`` `"  critical:"` ``.

**Note:** User said "not all changes incorrect, many are correct fixes recently
implemented" - so `fix_backtick_spaces` is intentional and working as designed when
applied to the RIGHT segments. The bug is that it's being applied to the WRONG segments.

**Impact:** MEDIUM - Adds visual noise, but may be working as intended for processable
text

### Bug #4: Missing Blank Line Additions

**Evidence:** Multiple locations show blank lines being added after headers:

```diff
 ### How Fixes Work
+
 1. `parse_segments()` divides document
```

```diff
 **Implementation:**
+
 1. Add table row detection
```

This appears to be `fix_numbered_list_spacing()` adding blank lines before numbered
lists.

**Impact:** LOW - Cosmetic, improves formatting but may be unexpected

## Root Cause Analysis

### Design Flaw: Processable Markdown Blocks

The original design (commit 5a5ad93) states:

> "Markdown blocks marked processable, all others protected."

This was intentional but **wrong**. The reasoning was likely: "If someone writes ```markdown, they want it formatted like markdown."

**Why This is Wrong:**

1. Documentation often contains ```markdown examples showing *before* state
2. Test data uses ```markdown to show expected unformatted output
3. Code fences are for **display**, not **processing**

**Correct Behavior:**

- ALL code fences should be protected, including ```markdown
- Only plain text segments should be processable
- If you want to format markdown inside a block, extract it first

### Segment Parser Logic Issues

The segment parser appears to have correct logic for bare fences:

- Test expects bare ``` fences to be protected (`processable=False`)
- Code in `parse_segments()` treats bare fences (language=None) as protected

But corruption is still happening. Possible causes:

1. **Nested fence handling bug** - Inner fences not being tracked correctly
2. **Segment boundary bug** - Fence lines not being included in protected segment
3. **flatten_segments bug** - Protected segments being merged with processable ones
4. **apply_fix_to_segments bug** - Not actually checking processable flag

Need deeper investigation to find exact cause.

## Test Coverage Gap

The test `test_parse_segments_bare_fence_block()` checks segment **parsing**, but there's no test checking that fixes are **actually skipped** for protected segments.

**Missing Test:**
```python
def test_fixes_skip_protected_segments():
    """Test: Fixes like fix_warning_lines don't run on protected segments."""
    lines = [
        "Normal text\n",
        "```\n",
        "✅ Should stay unchanged\n",
        "✅ Should stay unchanged\n",
        "```\n",
        "More text\n",
    ]
    result = process_lines(lines)
    # Should NOT convert to list items inside fence
    assert result[2] == "✅ Should stay unchanged\n"
    assert not result[2].startswith("- ")
```

## Evidence Summary

### Files Modified (7 total)

Analysis of each file:

1. **plans/markdown/agent-documentation.md**
   - ❌ CORRUPTION: Bare fence content converted to lists
   - Example: `✅ Issue #1` → `- ✅ Issue #1` inside ``` fence

2. **plans/markdown/feature-2-code-block-nesting.md**
   - ✅ CORRECT: Triple backticks in text escaped to double-backtick format
   - Example: ` ``` ` → `` `` ``` `` `` (inline code escaping)
   - This is `escape_inline_backticks()` working as designed

3. **plans/markdown/fix-warning-lines-tables.md**
   - ❌ CORRUPTION: ```markdown fence content converted to lists
   - Example: `**File:** role.md` → `- **File:** role.md` inside ```markdown fence
   - ✅ CORRECT: Blank lines added before numbered lists

4. **plans/markdown/root-cause-analysis.md**
   - ⚠️ DEBATABLE: Inline code with spaces quoted
   - Example: `` `  critical:` `` → `` `"  critical:"` ``
   - This is `fix_backtick_spaces()` making whitespace visible
   - ✅ CORRECT: Blank lines added before numbered lists

5. **plans/prompt-composer/design.md**
   - ✅ CORRECT: ```markdown upgraded to ````markdown (4 backticks)
   - This is `fix_markdown_code_blocks()` handling inner fences

6. **src/claudeutils/markdown.py**
   - ✅ CORRECT: Docstring line wrapping (dprint formatting)

7. **tests/test_markdown.py**
   - ✅ CORRECT: Added `r` prefix for raw strings in regex docstrings

**Summary:**

- **Real corruption:** 2 files (agent-documentation.md, fix-warning-lines-tables.md)
- **Working as designed:** 5 files (most changes are correct)
- **Core issue:** Content inside code fences (bare and ```markdown) being processed when
  it should be protected

### Corruption Patterns

| Pattern                      | Function                    | Should Skip          | Actually Skips?              |
| ---------------------------- | --------------------------- | -------------------- | ---------------------------- |
| Content in `` ```markdown `` | All fixes                   | ✅ Yes               | ❌ No - marked processable   |
| Content in bare `` ``` ``    | All fixes                   | ✅ Yes               | ❌ No - unknown bug          |
| Inline code with spaces      | `fix_backtick_spaces`       | ✅ Yes (if in fence) | ❌ No                        |
| Before numbered lists        | `fix_numbered_list_spacing` | ⚠️ Maybe              | ✅ Yes - working as designed |

## Clarifications from User

### ```markdown Blocks Being Processable: ✅ INTENTIONAL FEATURE

- **Not a bug** - This is by design
- **Purpose:** Correctly format documentation snippets included in rule files and plans
- **Example use case:** Plans containing markdown examples that should be formatted
- **Conclusion:** Keep `processable = open_lang == "markdown"` as-is

### Quoting Spaces in Inline Code: ✅ REQUIRED FEATURE

- **Not a bug** - This is necessary for disambiguation
- **Reason:** dprint strips inner spaces in ` text `, making them invisible
- **Solution:** `fix_backtick_spaces()` adds quotes: `` `  text  ` `` →
  `` `"  text  "` ``
- **Conclusion:** Keep this behavior, it prevents data loss

## New Bugs Discovered

### Bug #4: Incorrect Backtick Escaping in Documentation

**Location:** `plans/markdown/feature-2-code-block-nesting.md:48`

**Current (broken):**
```markdown
   - Output: ````markdown block (4 backticks)
```

This starts a 4-backtick code fence, which is invalid/broken markdown.

**Should be:**
```markdown
   - Output: `` ````markdown `` block (4 backticks)
```

Where `` ````markdown `` renders as ````markdown in inline code.

**CommonMark Rule:** To display N consecutive backticks in inline code, use N+1
backticks as delimiters.

**Status:** Initially thought to be pre-existing, but further investigation reveals...

### Bug #5: escape_inline_backticks() Regex Breaks 4+ Backticks ⚠️ CRITICAL

**Location:** `markdown.py:297`

**Code:**

````python
escaped_line = re.sub(r"(?<!`` )```(\w*)", r"`` ```\1 ``", line)
````

**Problem:** The regex matches the FIRST 3 backticks in any sequence of 4+ backticks and
wraps them incorrectly.

**Evidence:**

`````python
# Test with the regex:
Input:  "- Output: ````markdown block"
Output: "- Output: `` ``` ```markdown block"
#                        ^^^^^^^^^ BROKEN - creates fence start mid-line!

Input:  "- Output: `` ````markdown `` block"  # Attempted fix
Output: "- Output: `` ``` ```markdown `` `` block"  # Also broken!
`````

**Why it happens:**
1. Regex looks for 3 consecutive backticks: ` ``` `
2. Negative lookbehind `(?<!`` )` checks if "`` " (2 backticks + space) comes before
3. In ```` there's no space before the first 3, so it matches
4. Replaces ``` with `` ``` ``
5. Creates: `` ``` ` + ```markdown (broken - starts a code fence!)

**Correct behavior needed:**

- 3 backticks: `` ``` `` → should match (escape triple backticks)
- 4 backticks: `` ```` `` → should NOT match (already in inline code)
- Bare ````markdown → should NOT be escaped (it's invalid markdown to begin with)

**Impact:** HIGH - Actively corrupts any documentation trying to display 4+ backticks in
inline code

**Root cause of Bug #4:** The doc bug in feature-2-code-block-nesting.md:48 exists
because any attempt to fix it properly gets re-broken by this regex!

## Recommended Fixes

### Phase 6: Fix Markdown Block Processing ~~⚠️ CRITICAL~~ ✅ NOT NEEDED

**Status:** User confirms this is intentional - keep as-is

**Change:**

```python
# markdown.py:217
# OLD:
processable = open_lang == "markdown"

# NEW:
processable = False  # ALL fences are protected
```

**Update Tests:**

````python
# test_segments.py:33-43
def test_parse_segments_markdown_block() -> None:
-    """Test: parse_segments detects ```markdown block as processable."""
+    """Test: parse_segments detects ```markdown block as protected."""
    # ...
-    assert result[0].processable is True
+    assert result[0].processable is False
````

**Impact:** This will break the intentional "process markdown blocks" feature. Need to
verify no code depends on this.

### Phase 7: Debug Bare Fence Protection ⚠️ CRITICAL (ONLY REAL BUG)

**Investigation needed:**

1. Add debug logging to `parse_segments()` showing what segments are created
2. Add debug logging to `apply_fix_to_segments()` showing what's being processed
3. Run formatter on test file and examine logs
4. Identify where protection is failing

**Test to write:**

````python
def test_bare_fence_protection_integration():
    """Integration test: Verify bare fences actually protect content."""
    lines = [
        "```\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
        "```\n",
    ]
    result = process_lines(lines)
    assert result[1] == "✅ Task 1\n"  # Not converted to list
    assert result[2] == "✅ Task 2\n"
````

### Phase 8: Add Integration Tests ⚠️ CRITICAL

Add end-to-end tests that verify:

1. Content in ```python fences is unchanged
2. Content in ```markdown fences is unchanged
3. Content in bare ``` fences is unchanged
4. Content in YAML prologs is unchanged
5. Plain text IS processed correctly

**Test to write:**

````python
def test_bare_fence_protection_integration():
    """Integration test: Verify bare fences actually protect content."""
    lines = [
        "```\n",
        "✅ Task 1\n",
        "✅ Task 2\n",
        "```\n",
    ]
    result = process_lines(lines)
    assert result[1] == "✅ Task 1\n"  # Not converted to list
    assert result[2] == "✅ Task 2\n"
````

### Phase 9: Fix Incorrect Backtick Escaping in Documentation

**Depends on:** Phase 10 (must fix regex first)

**Change:**
```
# plans/markdown/feature-2-code-block-nesting.md:48
# OLD:
   - Output: ````markdown block (4 backticks)

# NEW:
   - Output: `` ````markdown `` block (4 backticks)
```

**Rationale:** Display 4 backticks in inline code using CommonMark escaping rules

**Impact:** LOW - Documentation fix, but requires Phase 10 first or regex will re-break it

### Phase 10: Fix escape_inline_backticks() Regex ⚠️ CRITICAL

**Location:** `markdown.py:297`

**Current regex (broken):**

````python
escaped_line = re.sub(r"(?<!`` )```(\w*)", r"`` ```\1 ``", line)
````

**Problem:** Matches first 3 backticks in 4+ backtick sequences, corrupting them.

**Fix strategy:**

1. **Option A - Stricter negative lookbehind:** Check for any backtick before the match
   ````python
   escaped_line = re.sub(r"(?<!`)`{3}(\w*)(?!`)", r"`` ```\1 ``", line)
   ````
   - `(?<!`)` ensures no backtick before
   - `{3}` matches exactly 3 backticks
   - `(?!`)` ensures no backtick after
   - This only matches standalone ```

2. **Option B - Skip already-escaped:** Better negative lookbehind
   ````python
   escaped_line = re.sub(r"(?<!``)```(\w*)", r"`` ```\1 ``", line)
   ````
   - `(?<!``)` checks for any 2 backticks before (whether or not there's a space)
   - Simpler but might miss edge cases

**Recommended:** Option A with negative lookahead for precision

**Test cases needed:**

`````python
def test_escape_inline_backticks_handles_4plus():
    """Test: 4+ backticks in inline code not corrupted."""
    lines = ["Text `` ````markdown `` more text\n"]
    result = escape_inline_backticks(lines)
    assert result[0] == lines[0]  # Should be unchanged

def test_escape_inline_backticks_handles_triple():
    """Test: Triple backticks still escaped."""
    lines = ["Text ```python code\n"]
    result = escape_inline_backticks(lines)
    assert result[0] == "Text `` ```python `` code\n"

def test_escape_inline_backticks_bare_4_backticks():
    """Test: Bare 4-backtick sequences unchanged."""
    lines = ["Output: ````markdown block\n"]
    result = escape_inline_backticks(lines)
    assert result[0] == lines[0]  # Invalid markdown, leave as-is
`````

**Impact:** HIGH - Fixes corruption of 4+ backtick sequences, enables Phase 9

## Revised Summary

**Real Bugs Found:** 3

1. ~~Bug #1: ```markdown blocks processable~~ → ✅ INTENTIONAL FEATURE
2. **Bug #2: Bare fences not protecting content** → ❌ CRITICAL, NEEDS FIX (Phase 7)
3. ~~Bug #3: Inline code with spaces quoted~~ → ✅ REQUIRED FEATURE
4. **Bug #4: Incorrect backtick escaping in docs** → ⚠️ Can't be fixed without fixing
   Bug #5
5. **Bug #5: escape_inline_backticks() regex bug** → ❌ CRITICAL, breaks 4+ backtick
   sequences (Phase 10)

**Files with Real Corruption:** 2

- `plans/markdown/agent-documentation.md` - Bare fence content → lists (Bug #2)
- `plans/markdown/fix-warning-lines-tables.md` - ```markdown fence content → lists
  (INTENTIONAL)

**Core Issues:**

- **Bug #2:** Bare fence protection failure - CRITICAL
- **Bug #5:** Regex in escape_inline_backticks() corrupts 4+ backtick sequences -
  CRITICAL

## Next Steps

1. ~~Update `plans/markdown/fix-warning-lines-tables.md`~~ → ✅ Done
2. **Implement Phase 7:** Debug and fix bare fence protection (CRITICAL)
3. **Implement Phase 8:** Add integration tests (CRITICAL)
4. **Implement Phase 10:** Fix escape_inline_backticks() regex (CRITICAL - blocks
   Phase 9)
5. **Implement Phase 9:** Fix backtick escaping in documentation (depends on Phase 10)
