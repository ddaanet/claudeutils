# Warning Line Prefix Test

## Emoji Checkmarks

✅ Issue #1: XPASS tests visible
✅ Issue #2: Setup failures captured
✅ Issue #3: Module imports work

Some text here.

❌ Test failed for module A
❌ Test failed for module B

## Bracket Prefixes

[TODO] Implement feature X
[TODO] Write comprehensive tests
[TODO] Update documentation

Some content between sections.

[WARNING] This is critical
[WARNING] Handle with care

## Uppercase Colon Prefixes

NOTE: First important note
NOTE: Second important note
NOTE: Third important note

Some paragraph text.

ERROR: Configuration missing
ERROR: Setup incomplete

## Mixed in Code Block

This should not be processed:

```
✅ This is in a code block
✅ Should not be converted
```

## Single Lines (no grouping)

✅ Only one line here

This is standalone, should skip it.

[NOTE] Single bracket line

And this is alone too.

ERROR: Single error line

## Table Example

| Header 1 | Header 2 |
|----------|----------|
| ✅ Pass  | ❌ Fail  |
| [TODO]   | [DONE]   |
