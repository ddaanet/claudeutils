# Markdown Preprocessor Codebase Exploration

## Summary

The markdown preprocessor (`claudeutils.markdown`) is a multi-module system that fixes structural issues in Claude-generated markdown before external formatters (remark-cli, dprint) process the output. It uses a segment-based pipeline architecture that protects code blocks and YAML from being modified while applying targeted fixes to plain text content. The codebase includes 5 test files covering 77 unit tests, but lacks fixture-based and end-to-end integration tests.

## Key Findings

### 1. Source Module Structure

**Location:** `/Users/david/code/claudeutils-markdown-test-corpus/src/claudeutils/`

**Core modules (5 markdown-specific files):**

| Module | Responsibility | Key Functions |
|--------|---|---|
| `markdown.py` | Entry point, orchestrates pipeline | `process_lines()`, `process_file()` |
| `markdown_parsing.py` | Segment detection & protection | `parse_segments()`, `flatten_segments()`, `apply_fix_to_segments()` |
| `markdown_inline_fixes.py` | Backtick escaping, dunder wrapping | `escape_inline_backticks()`, `fix_dunder_references()`, `find_inline_code_spans()` |
| `markdown_list_fixes.py` | Metadata blocks, lists, warning lines | `fix_metadata_blocks()`, `fix_nested_lists()`, `fix_warning_lines()`, `fix_numbered_list_spacing()` |
| `markdown_block_fixes.py` | Code block nesting | `fix_markdown_code_blocks()` |

**Architecture pattern:** Functional pipeline with no classes. Each module exports 1-8 functions applied sequentially to line lists.

**Re-export pattern:** `markdown.py` re-exports all functions in `__all__` for backward compatibility (line 104-121).

---

### 2. Processing Pipeline

**Entry point:** `process_lines(lines: list[str]) -> list[str]` (markdown.py, lines 70-85)

**Pipeline stages (order matters):**

```
1. parse_segments()              — Segment document into processable + protected regions
2. escape_inline_backticks()     — Wrap triple backticks in `` `` when inline
3. fix_dunder_references()       — Wrap __name__.py in backticks in headings
4. fix_metadata_blocks()         — Convert **Label:** lines to list items
5. fix_warning_lines()           — Convert emoji/bracket/colon prefix lines to lists
6. fix_nested_lists()            — Normalize nested list markers (a/b/c → 1/2/3)
7. fix_numbered_list_spacing()   — Indent numbered lists after metadata blocks
8. fix_backtick_spaces()         — Quote single/double backticks in inline code
9. flatten_segments()            — Reconstruct lines from segments
10. fix_markdown_code_blocks()   — Nest 4-backtick fences around markdown blocks with inner fences
```

**Key design: Segment-aware processing**

- `parse_segments()` splits input into `Segment` objects (markdown_parsing.py, lines 242-282)
- Each segment has `processable` boolean flag
- `apply_fix_to_segments()` (lines 208-239) applies fixes ONLY to `processable=True` segments
- Protected segments: code blocks (non-markdown), YAML prologs, bare fences

**Protection rules** (markdown_parsing.py):

- ✅ Markdown blocks (`\`\`\`markdown`) → processable=True, content recursively parsed
- ❌ Code blocks (e.g., `\`\`\`python`, `\`\`\`bash`) → processable=False, unchanged
- ❌ YAML prologs (`---...---`) → processable=False, unchanged
- ❌ Bare fences (`\`\`\``) → processable=False, unchanged

---

### 3. Test Organization

**Location:** `/Users/david/code/claudeutils-markdown-test-corpus/tests/`

**5 test files covering 77 unit tests:**

| Test File | Focus | Test Count | Key Patterns |
|---|---|---|---|
| `test_markdown_core.py` | Integration, idempotency, file I/O | ~10 | `process_lines()`, `process_file()`, idempotency assertions |
| `test_markdown_inline.py` | Backtick escaping, dunder refs | ~15 | `escape_inline_backticks()`, `find_inline_code_spans()`, idempotent tests |
| `test_markdown_block.py` | Fence nesting | ~6 | `fix_markdown_code_blocks()`, inner fence detection |
| `test_markdown_list.py` | Metadata, warnings, nested lists | ~20+ | `fix_warning_lines()`, `fix_metadata_blocks()`, emoji/bracket/colon prefix patterns |
| `test_markdown_parsing.py` | Segment-aware protection | ~12 | YAML prolog, code block, bare fence protection, recursive parsing |

**Test patterns observed:**

- ✅ Explicit input/expected output assertions
- ✅ Idempotency tests (running `process_lines()` twice should be identical, lines 104-126 in test_markdown_core.py)
- ✅ Edge case coverage (inline backticks, nested fences, emoji prefixes, bracket patterns)
- ❌ NO fixture-based tests (synthetic test data inline only)
- ❌ NO end-to-end pipeline tests (preprocessor → remark-cli/dprint)
- ❌ NO pass-through verification (links, escaping, HTML should be untouched)

**Test data style:** All tests use inline `input_lines` lists (e.g., test_markdown_core.py lines 15-17):

```python
input_lines = ["## About __init__.py\n"]
expected = ["## About `__init__.py`\n"]
assert process_lines(input_lines) == expected
```

---

### 4. Test Configuration

**pytest setup** (pyproject.toml, lines 114-121):

```toml
[tool.pytest.ini_options]
strict = true
testpaths = ["tests"]
addopts = "--no-header --tb=short -m 'not e2e'"
markers = [
    "e2e: end-to-end tests requiring API credentials",
]
```

- Tests live in `tests/` directory
- E2E tests marked with `@pytest.mark.e2e` are skipped by default
- No fixtures currently configured

**CI/linting setup:**

- mypy strict mode enabled (pyproject.toml, line 101)
- ruff for code style (lines 43-85)
- docformatter for docstrings (lines 37-41)
- pytest-markdown-report in dev dependencies (line 29)

---

### 5. Current Fixture Situation

**Status:** No fixture files exist.

**Attempted search:**
- `tests/fixtures/markdown/` — Does not exist
- `tests/fixtures/` — Empty or non-existent
- References in requirements.md (FR-1) describe proposed structure, not current implementation

**Requirement (FR-1):** fixture files should follow pattern:

```
tests/fixtures/markdown/
  01-nested-fences.input.md
  01-nested-fences.expected.md
  02-inline-backticks.input.md
  02-inline-backticks.expected.md
  ...
```

---

### 6. Key Functions & Signatures

**Primary entry point:**
```python
def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
```

**Segment API:**
```python
class Segment(BaseModel):
    processable: bool
    language: str | None
    lines: list[str]
    start_line: int

def parse_segments(lines: list[str]) -> list[Segment]
def flatten_segments(segments: list[Segment]) -> list[str]
def apply_fix_to_segments(
    segments: list[Segment],
    fix_fn: Callable[[list[str]], list[str]],
) -> list[Segment]
```

**Fix functions (all take `list[str]` → `list[str]`):**

| Function | Module | Behavior |
|---|---|---|
| `escape_inline_backticks()` | inline_fixes | Wraps triple backticks in double backticks when inline |
| `fix_dunder_references()` | inline_fixes | Wraps `__name__.py` in backticks in heading lines |
| `find_inline_code_spans()` | inline_fixes | Returns `list[(start, end)]` of protected 1-2 backtick spans (not 3+) |
| `fix_metadata_blocks()` | list_fixes | Converts `**Label:**` lines to `- **Label:**` list items |
| `fix_warning_lines()` | list_fixes | Converts emoji/bracket/colon-prefixed lines to list items |
| `fix_nested_lists()` | list_fixes | Normalizes nested markers (a/b/c → 1/2/3) |
| `fix_numbered_list_spacing()` | list_fixes | Indents numbered lists following metadata blocks |
| `fix_backtick_spaces()` | list_fixes | Adds spaces in double/triple backtick inline code when needed |
| `fix_markdown_code_blocks()` | block_fixes | Upgrades `\`\`\`markdown` blocks to `\`\`\`\`markdown` if they contain inner fences |

---

### 7. Key Patterns & Design Decisions

**Pattern: Prefix extraction** (markdown_list_fixes.py, lines 27-56)

Three types of prefixes trigger list conversion:
- Emoji-like (non-alphanumeric): ✅, ❌, ⚠️, etc.
- Bracketed: `[TODO]`, `[NOTE]`, etc.
- Uppercase colon: `NOTE:`, `WARNING:`, `TODO:`, etc.

Consecutive lines with similar prefix types → converted to list.

**Pattern: Segment-based idempotency**

Fixes applied only to `processable=True` segments ensures:
- Repeated runs produce identical output
- Code blocks/YAML never corrupted
- Pipeline is idempotent (test_markdown_core.py lines 104-126)

**Pattern: Inline code span protection** (markdown_inline_fixes.py, lines 19-94)

- Only protects 1-2 backtick delimiters (not 3+)
- Rationale: 3+ backticks are fence markers, should be escaped (not protected)
- Uses CommonMark spec: backtick strings are atomic, matching delimiters are required

**Pattern: YAML prolog validation** (markdown_parsing.py, lines 14-61)

- Requires `---` opening, content with key-value pairs, `---` closing
- No blank lines allowed inside prolog
- Must have `key:` pattern match to be recognized

---

### 8. Exception Handling

**Custom exceptions** (imported from claudeutils.exceptions):

- `MarkdownInnerFenceError` — Raised when fence parsing fails
- `MarkdownProcessingError` — Wraps inner fence errors with file path context

**Error handling in process_file()** (markdown.py, lines 88-100):

```python
def process_file(filepath: Path) -> bool:
    try:
        lines = process_lines(original_lines)
    except MarkdownInnerFenceError as e:
        raise MarkdownProcessingError(str(filepath), e) from e
```

---

### 9. Type Annotations & Validation

**Pydantic usage:**
- `Segment` is a `BaseModel` (markdown_parsing.py, line 191)
- Enables type validation and structured serialization

**Type strictness:**
- mypy strict mode enabled (pyproject.toml, line 101)
- Full type annotations on all functions
- `list[str]` (modern syntax, requires Python 3.9+)
- `Callable[[list[str]], list[str]]` for fix function types

---

### 10. Markdown Module Exports

**Public API** (markdown.py, lines 104-121):

```python
__all__ = [
    "Segment",
    "apply_fix_to_segments",
    "escape_inline_backticks",
    "find_inline_code_spans",
    "fix_backtick_spaces",
    "fix_dunder_references",
    "fix_markdown_code_blocks",
    "fix_metadata_blocks",
    "fix_metadata_list_indentation",
    "fix_nested_lists",
    "fix_numbered_list_spacing",
    "fix_warning_lines",
    "flatten_segments",
    "parse_segments",
    "process_file",
    "process_lines",
]
```

**Note:** `fix_metadata_list_indentation` exported but not found in module (possible omission or removed function).

---

## Patterns & Observations

### Processing Order Matters
Pipeline order is documented in markdown.py (lines 62-66) and must be preserved:
1. Inline escaping before dunder refs
2. Dunder refs before metadata blocks
3. Metadata blocks trigger indentation of following lists
4. Block fixes last (depends on all text fixes being complete)

### Recursion in Markdown Blocks
Markdown blocks are recursively parsed (markdown_parsing.py, lines 139-164), allowing nested structures within `\`\`\`markdown` sections to be fixed while preserving code block content.

### Line-based Processing
All fixes work on `list[str]` (lines including `\n`). No streaming or string manipulation. Segment model enables protecting regions without string-level complexity.

### Segment Protection Hierarchy
1. YAML prologs checked first (highest priority)
2. Fenced blocks checked second
3. Plain text collected as fallback
This ensures YAML isn't accidentally treated as fence content.

### Idempotency by Design
Each fix is idempotent in isolation; segment-based processing ensures entire pipeline is idempotent. Running `process_lines()` N times produces identical output.

---

## Gap Analysis

### Fixture-Based Testing
- **Status:** Not implemented
- **Need:** 12-20 fixture pairs in `tests/fixtures/markdown/`
- **Requirement:** FR-1 (requirements.md, lines 42-49)
- **Pattern:** `.input.md` / `.expected.md` pairs, parametrized pytest

### End-to-End Pipeline Tests
- **Status:** Not implemented
- **Need:** Preprocessor → remark-cli/dprint → verify output
- **Requirement:** FR-3 (requirements.md, lines 62-68)
- **Challenge:** Requires remark-cli or dprint in test environment

### Pass-Through Verification
- **Status:** Partial
- **Covered:** Code block content, YAML prolog, bare fences (via segment protection)
- **Missing:** Explicit assertions for links, escaping, HTML, mixed formatting (FR-2)

### Corpus Sections Not Covered
From requirements.md gap analysis (lines 24-32):

| Corpus Section | Coverage Status |
|---|---|
| 1. Nested fences | ✅ Unit tests (test_markdown_block.py) |
| 2. Inline backticks | ✅ Unit tests (test_markdown_inline.py) |
| 3. Horizontal rules | ⚠️ Documented, no explicit test |
| 4. YAML frontmatter | ✅ Covered (test_markdown_parsing.py) |
| 5. Code blocks w/ special chars | ✅ Partial (fence detection, not char preservation) |
| 6. GFM (tables, task lists) | ⚠️ Table protection only, no format test |
| 7. Lists and nesting | ✅ Unit tests (test_markdown_list.py) |
| 8. Block quotes | ✅ Covered (segment protection) |
| 9. Links and images | ❌ No test |
| 10. Escaping | ❌ No test |
| 11. Inline HTML | ❌ No test |
| 12. Mixed formatting | ⚠️ Partial (parsing tests, not format preservation) |

---

## File Organization

```
src/claudeutils/
├── markdown.py                 # Entry point, pipeline orchestration
├── markdown_parsing.py         # Segment model & parsing
├── markdown_inline_fixes.py    # Backtick escaping, dunder refs
├── markdown_list_fixes.py      # Metadata, lists, warnings (410 lines)
├── markdown_block_fixes.py     # Code block nesting (113 lines)

tests/
├── test_markdown_core.py       # Integration, idempotency (127 lines)
├── test_markdown_inline.py     # Backtick & dunder tests (~80 lines)
├── test_markdown_block.py      # Fence nesting tests (~80 lines)
├── test_markdown_list.py       # Metadata & list tests (~150+ lines)
├── test_markdown_parsing.py    # Segment & protection tests (~120 lines)
└── fixtures/                   # MISSING: Should contain .input.md & .expected.md pairs

plans/markdown/
├── requirements.md             # 5 FRs + gap analysis
└── test-corpus.md              # 12 corpus sections
```

---

## Unresolved Questions

1. **Function mismatch:** `fix_metadata_list_indentation` in `__all__` but not defined in module. Is this exported but unused?

2. **Backtick quoting function:** `fix_backtick_spaces()` referenced in pipeline but only briefly mentioned in tests. What exactly does it do?

3. **Horizontal rules:** How are `---` at doc boundaries distinguished from YAML prolog closers? markdown_parsing.py lines 181-184 check for blank lines; is this sufficient?

4. **Mixed prefix types:** When lines have emoji AND bracket prefixes, does `_is_similar_prefix()` group them? Current logic suggests emoji ≠ bracket.

5. **Formatter integration:** Requirements mention "dprint plugin future direction" (markdown.py line 16) — is this pre-design analysis or post-decision?

---

## Recommendations for Fixture Implementation

**Phase 1: Create fixture files** (~2 hours)
- Add 15-20 fixture pairs to `tests/fixtures/markdown/`
- Map corpus sections 1-8 + preprocessor-specific cases (dunder refs, metadata blocks)
- Include both transformation (input ≠ expected) and pass-through (input == expected) cases

**Phase 2: Parametrized test module** (~1 hour)
```python
# tests/test_markdown_fixtures.py
@pytest.mark.parametrize("fixture", glob("tests/fixtures/markdown/*.input.md"))
def test_preprocessor_fixture(fixture):
    """Load input, apply process_lines(), compare to expected."""

@pytest.mark.parametrize("fixture", glob("tests/fixtures/markdown/*.input.md"))
def test_preprocessor_idempotency(fixture):
    """Verify output is stable on re-processing."""
```

**Phase 3: Optional end-to-end tests** (separate plan)
- Requires remark-cli in CI environment
- Use `subprocess.run()` + `pytest.importorskip()` for conditional execution
- Verify dprint/remark output correctness

