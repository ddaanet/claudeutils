---
title: Markdown Formatter Test Corpus
description: Edge cases for evaluating markdown formatter behavior
version: 1.0
---

# Markdown Formatter Test Corpus

This file contains critical test cases for evaluating markdown formatters.

## 1. Nested Fenced Code Blocks

The formatter MUST preserve nested fenced blocks correctly:

`````markdown
# Example Document

````text
This is a text block inside markdown.
It contains:
```
Inner fenced content
```
````

More content here.
`````

## 2. Inline Code Spans with Backticks

The formatter MUST preserve inline code containing backticks. This is where dprint failed thoroughly.

### Basic Cases

- Single backticks: `code`
- Multiple words: `const foo = 'bar'`
- With symbols: `$PATH` and `~/.bashrc`
- Empty code span: ` ` (space between delimiters is ignored)
- Whitespace trimmed: ` code ` becomes `code` (non-significant)

### Double Backtick Quoting (Quote Single Backtick)

**Without spaces around content:**
- Quote one backtick (no spaces): ``using ` backtick``
- Multiple backticks in content: ``use ` and ` backticks``

**With spaces for consistency (when content starts/ends with backtick):**
- Single backtick: `` ` `` (spaces at both ends for consistency)
- Backtick at start: `` `start`` (spaces at both ends)
- Backtick at end: ``end` `` (spaces at both ends)
- Multiple with spaces: `` ` and ` `` (spaces at both ends)

### Triple Backtick Quoting (Quote Double Backticks)

**Without spaces around content:**
- Quote double backticks: ``` using `` double ```
- Multiple in content: ``` use `` and `` backticks ```

**With spaces for consistency (when content starts/ends with backticks):**
- Double backtick: ``` `` ``` (spaces at both ends)
- At start: ``` ``start ``` (spaces at both ends)
- At end: ``` end`` ``` (spaces at both ends)
- Single in triple: ``` ` ``` (spaces at both ends)

### Mixed Quoting (Double and Triple in Same Span)

**Using triple backticks to quote both single and double:**
- Mixed: ``` using ` single and `` double ```
- Complex: ``` quote ` or `` or both ```
- At boundaries: ``` ` and `` mixed ```

### Quadruple Backtick Quoting (Quote Triple)

**Quoting triple backticks (code fence markers):**
- Quote triple (no spaces needed): ```` using ``` triple ````
- Fence example: ```` code fence: ```python ````
- Triple with spaces (if at boundaries): ```` ``` ```` (spaces at both ends)

### Edge Cases

**Content is just backticks (spaces added for consistency):**
- Just one backtick: `` ` `` (spaces at both ends)
- Just two backticks: ``` `` ``` (spaces at both ends)
- Just three backticks: ```` ``` ```` (spaces at both ends)

**Delimiter normalization (shortest delimiter when no inner backticks):**
- May normalize: ``no backticks`` → `no backticks`
- May normalize: ```also no backticks``` → `also no backticks`
- Normalization is a feature, not a bug

**Adjacent code spans:**
- Back to back: `code1``code2`
- With text: `code1` and ``code2``
- Multiple styles: `single` and `` `double` `` and ``` `triple` ```

**Backticks with other markdown:**
- Bold code: **`code`**
- Italic code: *`code`*
- Link with code: [`link`](url)
- Code with emphasis: `*not italic*`
- Code with underscore: `my_variable`

## 3. Horizontal Rules

The formatter MUST NOT convert these `---` lines into something else:

---

Text between horizontal rules.

---

## 4. YAML Frontmatter Preservation

The frontmatter at the top of this file (between `---` delimiters) MUST remain intact.

## 5. Code Blocks with Special Characters

```python
def escape_test():
    """Test special chars: $, `, *, _, [], (), etc."""
    regex = r"^(\w+):\s*(.*)$"
    template = f"Value: {value}"
    return True
```

```bash
# Shell commands with special syntax
echo "Test: $VAR and `command`"
ls -la | grep "*.md"
```

```javascript
const regex = /`backticks`/g;
const template = `String with ${variable}`;
```

## 6. GFM Features

### Tables

| Feature | Status | Notes |
|---------|--------|-------|
| Tables | ✓ | Must align correctly |
| Checkboxes | ✓ | See below |

### Task Lists

- [x] Completed task
- [ ] Incomplete task
- [ ] Another task

### Strikethrough

~~This text is struck through~~

## 7. Lists and Nesting

1. First item
   - Nested bullet
   - Another nested bullet
     - Deeply nested
2. Second item
   ```python
   # Code in list
   def foo():
       pass
   ```
3. Third item

## 8. Block Quotes

> This is a quote.
>
> It has multiple paragraphs.
>
> ```python
> # Code in quote
> print("hello")
> ```

## 9. Links and Images

[Link text](https://example.com)

![Alt text](image.png)

Reference-style: [link][ref]

[ref]: https://example.com

## 10. Escaping Test

These should remain escaped:

- \* Not a bullet
- \# Not a heading
- \[Not a link\]
- \`Not code\`

## 11. Inline HTML

<div class="custom">
  <p>HTML should be preserved</p>
</div>

## 12. Mixed Formatting

**Bold text** with *italic* and `code` and ~~strikethrough~~.

## 13. Dunder References

The formatter MUST preserve or appropriately format Python dunder references (like `__init__.py`, `__name__`):

- Heading with dunder: About __init__.py
- Multiple dunders in heading: Using __init__.py and __name__
- Already wrapped dunder: `__init__.py` (should not be double-wrapped)
- Non-dunder variables like my_var should pass through unchanged
- Special attributes: __dict__ and __class__
- Complex case: Using __init__.py in __main__.py

## 14. Metadata Blocks

The formatter MUST preserve metadata block formatting with labels and content:

**Status:** Draft
**Context:** Testing
**Author:** Test Suite

Content between metadata blocks.

**Plan Files:**
- `plans/phase-1.md`
- `plans/phase-2.md`

**Implementation Date:**
- 2026-01-04

**Another Single Label:** Content on same line

**Nested:**
- Item 1
- Item 2

## 15. Warning Line Prefixes

The formatter MUST preserve warning-line patterns (consecutive lines with emoji or bracket prefixes):

### Emoji Checkmarks

✅ Issue #1: XPASS tests visible
✅ Issue #2: Setup failures captured
✅ Issue #3: Module imports work

### Error Markers

❌ Test failed for module A
❌ Test failed for module B

### Bracket Prefixes

[TODO] Implement feature X
[TODO] Write comprehensive tests
[TODO] Update documentation

[WARNING] This is critical
[WARNING] Handle with care

### Uppercase Colon Prefixes

NOTE: First important note
NOTE: Second important note
NOTE: Third important note

ERROR: Configuration missing
ERROR: Setup incomplete

### Single Lines (no grouping)

Single-line prefixes that don't form consecutive groups should pass through unchanged:

✅ Only one line here

[NOTE] Single bracket line

ERROR: Single error line

## 16. Backtick Space Quoting

The formatter MUST preserve spaces around inline code when significant:

### Cases with Leading Spaces

- Leading space: ` code`
- Multiple leading: `   code`
- Only space: `   `

### Cases with Trailing Spaces

- Trailing space: `code `
- Multiple trailing: `code   `
- Only space: `   `

### Cases with Both Spaces

- Both ends: ` code `
- Both multiple: `   code   `
- Both with symbols: ` $VAR `

### Cases without Spaces (unchanged)

- Normal: `code`
- No spaces: `const x = 'y'`
- Path: `~/.bashrc`

### Mixed in Sentence

The empty span ` ` (space only) should preserve spaces.
Variable ` name ` needs visible spaces.
The path `./file` should be unchanged.

---

## Idempotency Test

Run formatter 3 times. Output of run 2 and run 3 MUST be identical to run 1.
