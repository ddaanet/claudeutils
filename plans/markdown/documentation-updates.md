# Documentation Updates

- **Feature:** Update markdown.py module documentation
- **File:** `src/claudeutils/markdown.py`
- **Model:** Haiku (task coder)

---

## Purpose

Clarify that markdown.py is a preprocessor for Claude markdown-like output, followed by
dprint formatting. Update module docstring and add explanatory comments.

---

## Updates Needed

### 1. Module Docstring

**Current:**

```python
"""Fix markdown structure before reformatting."""
```

**Updated:**

```python
"""Preprocessor for Claude markdown-like output.

This module fixes structural issues in Claude-generated markdown before
dprint formatting. It handles patterns that Claude commonly produces but
aren't valid markdown, such as:

- Consecutive lines with emoji/symbol prefixes needing list formatting
- Code blocks with improper fence nesting
- Metadata labels followed by lists needing indentation
- Other structural patterns from Claude output

Processing Pipeline:
    Claude output → markdown.py fixes → dprint formatting

Future Direction:
    This should eventually evolve into a dprint plugin for better integration.

Usage:
    # Process single file
    from pathlib import Path
    from claudeutils.markdown import process_file

    filepath = Path("output.md")
    modified = process_file(filepath)  # Returns True if file was changed

    # Process lines in memory
    from claudeutils.markdown import process_lines

    lines = ["**File:** test.md\\n", "**Model:** Sonnet\\n"]
    fixed_lines = process_lines(lines)
"""
```

---

### 2. Add Pipeline Explanation Comment

**Location:** Before `process_lines` function

**Add:**

```python
# ============================================================================
# Processing Pipeline
# ============================================================================
#
# This module applies multiple fixes in a specific order to handle
# Claude-generated markdown patterns:
#
# 1. fix_dunder_references    - Wrap `__init__.py` in backticks
# 2. fix_metadata_blocks      - Convert consecutive **Label:** to lists
# 3. fix_warning_lines        - Convert emoji/symbol prefixed lines to lists
# 4. fix_nested_lists         - Convert lettered items (a., b.) to numbered
# 5. fix_metadata_list_indentation - Indent lists after metadata labels
# 6. fix_numbered_list_spacing - Add proper blank lines around numbered lists
# 7. fix_markdown_code_blocks - Nest markdown blocks with inner fences
#
# Order matters: Line-based fixes run before block-based fixes to avoid
# interference. Spacing fixes run near the end after structure is correct.
#
```

---

### 3. Update Individual Function Docstrings

**Add context to key functions:**

`````python
def fix_warning_lines(lines: list[str]) -> list[str]:
    """Convert consecutive lines with consistent non-markup prefix to list items.

    Claude often generates consecutive lines with emoji or symbol prefixes
    that should be formatted as lists. This detects patterns like:
    - ✅ Task completed
    - ❌ Task failed
    - ⚠️ Warning message
    - [TODO] Action item

    Only converts groups of 2+ lines with similar prefix patterns.
    Skips lines already formatted as lists (-, *, numbered).
    """


def fix_markdown_code_blocks(lines: list[str]) -> list[str]:
    """Nest ```markdown blocks that contain inner ``` fences.

    Claude sometimes generates ```markdown blocks containing code examples
    with their own ``` fences. This uses ```` (4 backticks) for the outer
    fence to properly nest the content.

    Raises:
        ValueError: If inner fence detected in non-markdown code block.
                    This prevents dprint formatting failures downstream.

    Note: Only processes ```markdown blocks. Other language blocks with
          inner fences will error out to prevent silent formatting issues.
    """


def fix_metadata_list_indentation(lines: list[str]) -> list[str]:
    """Convert metadata labels to list items and indent following lists.

    Claude generates metadata labels like **Plan Files:** followed by lists.
    This converts the label to a list item and indents the following list
    by 2 spaces to create proper nested list structure.

    Example:
        **Plan Files:**          →    - **Plan Files:**
        - phase-1.md                    - phase-1.md
        - phase-2.md                    - phase-2.md

    Works with both **Label:** and **Label**: patterns.
    """
`````

---

### 4. Add README Section

**Location:** `README.md`, after main features section

**Add:**

````markdown
## Markdown Preprocessor

The `markdown` command preprocesses Claude-generated markdown output before dprint
formatting:

```bash
# Process files from git status
git status --short | cut -c4- | uv run claudeutils markdown

# Or pipe file paths directly
echo "output.md" | uv run claudeutils markdown
```

**What it fixes:**

- Consecutive emoji/symbol prefixed lines → proper lists
- Nested code blocks in ```markdown fences
- Metadata labels with following lists → indented nested lists
- Numbered list spacing issues
- And more...

**Processing Pipeline:**

```
Claude output → markdown.py → dprint → final output
```

The preprocessor handles structural issues that Claude commonly produces but aren't
valid markdown. After preprocessing, dprint applies consistent formatting.

**Note:** This is currently a standalone tool but should eventually evolve into a dprint
plugin for better integration.
````

---

## Implementation Steps

### Step 1: Update Module Docstring

**Test:** (No automated test - manual verification)

**Implementation:**

- Replace module-level docstring in `src/claudeutils/markdown.py`
- Verify formatting with `just format`

---

### Step 2: Add Pipeline Comment

**Test:** (No automated test - manual verification)

**Implementation:**

- Add comment block before `process_lines` function
- List all fixes in order with brief descriptions

---

### Step 3: Update Function Docstrings

**Test:** (No automated test - manual verification)

**Implementation:**

- Update `fix_warning_lines` docstring
- Update `fix_markdown_code_blocks` docstring
- Update `fix_metadata_list_indentation` docstring
- Ensure all docstrings explain the "why" (Claude patterns) not just "what"

---

### Step 4: Update README

**Test:** (No automated test - manual verification)

**Implementation:**

- Add new "Markdown Preprocessor" section to README.md
- Explain purpose, usage, and pipeline
- Include examples

---

## Validation

**Manual review:**

- Read through all updated docstrings
- Verify clarity and completeness
- Check that pipeline explanation is accurate

**Run tools:**

```bash
just format  # Auto-format
just check   # Lint check
```

**Documentation verification:**

- README section is clear and helpful
- Docstrings accurately describe behavior
- Pipeline comment lists all fixes in correct order

---

## Notes

- Documentation is critical for future maintainers
- Explain the "why" behind each fix (Claude patterns)
- Make it clear this is a preprocessor, not a formatter
- Note the future direction (dprint plugin)
