# Fix Plan: Prevent Table and Metadata List Corruption

## Problems

1. **Tables converted to lists**: `fix_warning_lines()` treats table rows as prefixed lines
2. **Single labels converted to list items**: `fix_metadata_list_indentation()` incorrectly treats single `**Label:**` as a metadata list
3. **Bold labels processed twice**: Both `fix_warning_lines()` and other functions try to process `**Label:**` patterns

## User Requirements (Clarified)

- **Metadata list** = 2+ consecutive `**Label:**` lines → convert to list items ✅ (keep `fix_metadata_blocks`)
- **Single `**Label:**` line** ≠ metadata list → do NOT convert to list item ❌
- **List following metadata list** → should be indented ✅
- **Indentation must be consistent** → all items at same nesting level have same indent (not progressive) ✅
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
```markdown
**Commits:**                   - **Commits:**
- item 1              →          - item 1
- item 2                           - item 2
```
Single label is converted to list item (wrong - not a metadata list)

**Desired behavior:**
```markdown
**File:** role.md              **File:** role.md
**Model:** Sonnet      →       **Model:** Sonnet

**Label1:** value              - **Label1:** value
**Label2:** value              - **Label2:** value
- item 1                         - item 1
- item 2                         - item 2
```

**Implementation:**
Modify `fix_metadata_list_indentation()` to:
1. Detect if previous content is a metadata list (list items starting with `- **` pattern)
2. Only indent following list if it comes after a metadata list
3. Do NOT convert single `**Label:**` lines to list items

**Alternative simpler approach:**
- Disable `fix_metadata_list_indentation` completely
- Let `fix_metadata_blocks` handle 2+ labels (converts to list)
- User can manually indent lists when needed
- No automatic indentation = no indentation bugs

**Recommended: Disable completely** (simpler, avoids bugs)

**Why disable:**
- Function converts single labels to list items (wrong - user says "single line with label does not make a metadata list")
- Indentation logic could cause progressive indent increase (user concern)
- Simpler to let users control indentation manually

**Changes needed:**
- Comment out line 723 in `markdown.py`: `segments = apply_fix_to_segments(segments, fix_metadata_list_indentation)`
- Update test expectations

### Phase 3: Bold Label Exclusion (from fix_warning_lines)

**Objective:** Prevent `**Label:**` patterns from being processed by `fix_warning_lines()` (already handled by `fix_metadata_blocks`)

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

### Phase 4: Enhanced Prefix Pattern Validation (Optional)

**Objective:** Make prefix detection more conservative (optional - may not be needed if Phases 1-3 fix all issues)

**Implementation:**
1. Tighten the prefix regex pattern:
   - Current: `r"^(\S+(?:\s|:))"`  (too broad)
   - Proposed: Only match known safe patterns:
     - Emoji: `r"^([^\w\s\[\(\{\-\*\|])"` (exclude `|`)
     - Brackets: `r"^(\[[^\]]+\])"`
     - Word colon: `r"^([A-Z][A-Z0-9]*:)"` (uppercase words only, exclude `**`)

2. Add explicit checks in `extract_prefix()`:
   - Skip if line is a table row
   - Skip if line is a bold label
   - Only then check for emoji/bracket/word+colon patterns

## Implementation Order

1. **Add table detection** (HIGHEST priority - most files affected)
2. **Disable metadata list indentation** (prevents single label conversion)
3. **Add bold label exclusion** (prevents duplicate processing)
4. **Tighten prefix patterns** (optional - only if needed after 1-3)

## Testing Strategy

1. Add unit tests for each exclusion pattern
2. Run `just format` on corrupted files and verify they're fixed
3. Run full test suite to ensure no regressions
4. Manually verify a few affected files (AGENTS.md, START.md, session.md)

## Files to Modify

- `src/claudeutils/markdown.py` - Update `extract_prefix()` and `is_similar_prefix()`
- `tests/test_markdown.py` - Add table and bold label test cases

## Success Criteria

✅ Tables remain as tables (no `- |` prefixes)
✅ Single `**Label:**` lines stay as-is (not converted to list items)
✅ Multiple consecutive `**Label:**` lines converted to list (metadata blocks)
✅ List indentation is consistent at each nesting level (no progressive increase)
✅ Legitimate emoji/bracket prefixed lines still converted to lists
✅ All tests pass (update expectations)
✅ Running `just format` on session.md, AGENTS.md, START.md produces minimal/no changes

## Key Decision: Disable fix_metadata_list_indentation

**Reason:** Single `**Label:**` line ≠ metadata list, should not be converted to list item

**Action:** Comment out the function call in `process_lines()`. Keep function code for potential future enhancement (e.g., only indent lists after actual metadata lists, not single labels).

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
   git checkout HEAD -- AGENTS.md START.md session.md agents/modules/MODULE_INVENTORY.md
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
- AGENTS.md
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
