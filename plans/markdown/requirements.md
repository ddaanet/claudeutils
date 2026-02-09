# Markdown Test Corpus: Requirements

## Problem Statement

The markdown preprocessor (`claudeutils.markdown`) has 77 unit tests that verify individual fix functions in isolation. A reference test corpus (`plans/markdown/test-corpus.md`) documents 12 categories of edge cases. But these two artifacts are disconnected:

- **No fixture-based testing** — The test corpus isn't consumed by any automated test
- **No end-to-end pipeline tests** — Unit tests verify the preprocessor, but not the full pipeline (preprocessor → dprint/remark-cli → output)
- **No pass-through verification** — Sections 9-12 of the corpus (links, escaping, HTML, mixed formatting) test content the preprocessor should leave untouched, but no tests assert this
- **No cross-formatter comparison** — The formatter evaluation (remark-cli vs prettier vs dprint) was manual; no automated regression suite exists

## Gap Analysis

### Covered by unit tests, absent from corpus

- Dunder references (`__init__.py` in headings)
- Metadata block conversion (`**Label:** value` → list items)
- Warning line prefix detection (emoji, brackets, uppercase colon)
- Block quote protection, tree diagram protection, table row protection
- Backtick space quoting (`blah ` → `"blah "`)

### In corpus, absent from unit tests

| Corpus Section | Gap |
|---|---|
| 3. Horizontal rules | No explicit preservation test |
| 5. Code blocks w/ special chars | Fence detection tested, but not char preservation |
| 6. GFM (tables, task lists, strikethrough) | Table row protection only; no formatting verification |
| 9. Links and images | No pass-through test |
| 10. Escaping (`\*`, `\#`, etc.) | No pass-through test |
| 11. Inline HTML | No pass-through test |
| 12. Mixed formatting | No pass-through test |

### Missing entirely from both

- **Full pipeline idempotency** — Running preprocessor + formatter multiple times
- **Formatter regression suite** — Automated detection when formatter behavior changes
- **Real-world Claude output samples** — Current fixtures are synthetic; no captured real output

## Requirements

### FR-1: Fixture-based preprocessor tests

Convert test corpus edge cases into parametrized pytest fixtures.

- Input files (`*.input.md`) and expected output files (`*.expected.md`)
- Location: `tests/fixtures/markdown/`
- Parametrized test reads each pair, runs through `process_lines()`, compares
- One fixture per corpus section (12 fixtures minimum)

### FR-2: Pass-through verification tests

Verify the preprocessor doesn't corrupt content it shouldn't modify.

- Links, images, reference-style links
- Backslash escaping
- Inline HTML
- Mixed formatting (bold + italic + code + strikethrough)
- Horizontal rules
- GFM features (tables, task lists, strikethrough)

### FR-3: Full pipeline integration tests

Test the complete pipeline: preprocessor → external formatter → output.

- Requires remark-cli (or dprint) available in test environment
- Skip gracefully if formatter not installed (`pytest.importorskip` pattern)
- Verify output correctness and idempotency

### FR-4: Idempotency property tests

Automated verification that running the pipeline N times produces identical output.

- Preprocessor-only idempotency (exists but limited)
- Full pipeline idempotency (new)
- Parameterize across all fixture files

### FR-5: Corpus completeness

Extend test-corpus.md with preprocessor-specific edge cases currently only in unit tests:

- Dunder references
- Metadata blocks
- Warning line prefix patterns
- Backtick space quoting

## Approach Recommendation

**Fixture files + parametrized tests** — the standard pytest pattern.

### Structure

```
tests/fixtures/markdown/
  01-nested-fences.input.md
  01-nested-fences.expected.md
  02-inline-backticks.input.md
  02-inline-backticks.expected.md
  ...
  12-mixed-formatting.input.md
  12-mixed-formatting.expected.md
  13-dunder-references.input.md    # Preprocessor-specific
  13-dunder-references.expected.md
  14-metadata-blocks.input.md
  14-metadata-blocks.expected.md
  ...
```

### Test organization

```python
# tests/test_markdown_fixtures.py
@pytest.mark.parametrize("fixture", glob("tests/fixtures/markdown/*.input.md"))
def test_preprocessor_fixture(fixture):
    """Verify preprocessor transforms input to expected output."""

@pytest.mark.parametrize("fixture", glob("tests/fixtures/markdown/*.input.md"))
def test_preprocessor_idempotency(fixture):
    """Verify preprocessor output is stable on re-processing."""

@pytest.mark.parametrize("fixture", glob("tests/fixtures/markdown/*.input.md"))
@pytest.mark.skipif(not shutil.which("remark"), reason="remark-cli not installed")
def test_full_pipeline(fixture):
    """Verify full pipeline (preprocessor + remark-cli) output."""
```

### Pass-through fixtures

For content the preprocessor should not modify, `.input.md` == `.expected.md`. The test runner detects this and verifies identity.

### Scope estimate

- ~15-20 fixture pairs (12 corpus sections + preprocessor-specific cases)
- 1 parametrized test module (~100 lines)
- Extensions to test-corpus.md for completeness
- Optional: full pipeline tests requiring remark-cli in CI

## Non-goals

- **Formatter comparison harness** — The remark-cli decision is made; no need to re-compare formatters
- **Property-based/fuzz testing** — Useful but out of scope for initial corpus work
- **Real-world sample collection** — Desirable but separate effort; synthetic fixtures sufficient for now
- **dprint plugin development** — Noted as future direction in design docs, separate plan

## Next Step

Route to `/design` for architectural decisions (fixture loading pattern, CI integration strategy for external formatters, test module organization).
