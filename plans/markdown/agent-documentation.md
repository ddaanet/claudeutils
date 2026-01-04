# Agent Documentation Updates

- **Feature:** Update agent documentation with markdown cleanup context
- **Files:** `agents/TEST_DATA.md`, `agents/DESIGN_DECISIONS.md`
- **Model:** Haiku (task coder)

---

## Purpose

After implementing the markdown cleanup features, update agent documentation to:

1. Provide example data for future reference
2. Document design decisions and rationale
3. Explain pipeline architecture

This ensures future agents understand the context and decisions behind the
implementation.

---

## Updates Needed

### 1. TEST_DATA.md

**Add new section: Markdown Cleanup Examples**

``````markdown
## Markdown Cleanup Examples

The markdown module preprocesses Claude-generated markdown output before dprint
formatting. These examples show common patterns and transformations.

### Checklist Detection

**Input:**

```
✅ Issue #1: XPASS tests visible
✅ Issue #2: Setup failures captured
❌ Issue #3: Not fixed yet
```

**Output:**

```
- ✅ Issue #1: XPASS tests visible
- ✅ Issue #2: Setup failures captured
- ❌ Issue #3: Not fixed yet
```

### Code Block Nesting

**Input:**

````
```markdown
# Example
```python
code
```
```
````

**Output:**

`````
````markdown
# Example
```python
code
```
````
`````

**Error Case (Invalid):**

````
```python
def foo():
    """
    Example:
    ```
    code
    ```
    """
```

Error: Inner fence detected in non-markdown block (prevents dprint failure)
````

### Metadata List Indentation

**Input:**

```
**Plan Files:**
- `plans/phase-1.md`
- `plans/phase-2.md`
```

**Output:**

```
- **Plan Files:**
  - `plans/phase-1.md`
  - `plans/phase-2.md`
```

---

### Pipeline Flow

```
Claude generates markdown
  ↓
markdown.py preprocessor (fix structure)
  ├─ fix_dunder_references
  ├─ fix_metadata_blocks
  ├─ fix_warning_lines (extended)
  ├─ fix_nested_lists
  ├─ fix_metadata_list_indentation (new)
  ├─ fix_numbered_list_spacing
  └─ fix_markdown_code_blocks (new)
  ↓
dprint formatter (consistent style)
  ↓
Final markdown output
```
``````

---

### 2. DESIGN_DECISIONS.md

**Add new section: Markdown Cleanup Architecture**

````markdown
## Markdown Cleanup Architecture

- **Decision Date:** 2026-01-04
- **Context:** Extend markdown preprocessor for Claude output patterns

### Problem

Claude generates markdown-like output that isn't always valid markdown:

1. Consecutive lines with emoji/symbol prefixes that should be lists
2. Code blocks with improper fence nesting
3. Metadata labels followed by lists needing indentation

These patterns break dprint formatting or produce suboptimal output.

### Solution

**Preprocessor approach:**

- Run markdown.py fixes BEFORE dprint formatting
- Fix structural issues while preserving content
- Error out on invalid patterns (prevent silent failures)

**Pipeline:**

```
Claude output → markdown.py (structure) → dprint (style) → final output
```

### Design Decisions

#### 1. Extend vs. New Functions

**Decision:** Extend `fix_warning_lines` for checklist detection, create new functions
for code blocks and metadata indentation.

**Rationale:**

- Checklist detection is conceptually similar to existing warning line handling
- Code block nesting is fundamentally different (block-based vs. line-based)
- Metadata list indentation is a new pattern distinct from metadata blocks

**Alternatives considered:**

- Create all new functions → More code duplication
- Single mega-function → Harder to test and maintain

#### 2. Error on Invalid Patterns

**Decision:** Error out when inner fences detected in non-markdown blocks.

**Rationale:**

- Prevents dprint formatting failures downstream
- Makes issues visible immediately (fail fast)
- Invalid patterns indicate malformed Claude output that needs fixing

**Alternatives considered:**

- Silent skip → Hides problems, dprint fails later
- Auto-fix → Risk of corrupting code content

#### 3. Processing Order

**Decision:**

```python
1. fix_dunder_references        # Line-based
2. fix_metadata_blocks          # Line-based
3. fix_warning_lines            # Line-based (extended)
4. fix_nested_lists             # Line-based
5. fix_metadata_list_indentation # Line-based (new)
6. fix_numbered_list_spacing    # Spacing (after structure)
7. fix_markdown_code_blocks     # Block-based (last)
```

**Rationale:**

- Line-based fixes before block-based (avoid interference)
- Spacing fixes after structural changes
- Code block nesting last (operates on complete structure)

**Alternatives considered:**

- Random order → Some fixes would break others
- All new fixes at end → Spacing issues with numbered lists

#### 4. Prefix Detection Strategy

**Decision:** Generic prefix detection (any consistent non-markup prefix), not
hard-coded patterns.

**Rationale:**

- Handles current patterns (✅, ❌, [TODO], etc.)
- Adapts to new patterns Claude might generate
- Reduces maintenance (no pattern list to update)

**Alternatives considered:**

- Whitelist specific prefixes → Brittle, needs updates
- No grouping logic → Each pattern needs separate fix

#### 5. Indentation Amount

**Decision:** 2 spaces for nested lists.

**Rationale:**

- Standard markdown convention
- Matches dprint default formatting
- Consistent with existing codebase style

**Alternatives considered:**

- 3 spaces → Not standard
- 4 spaces → Too much nesting, harder to read

### Future Direction

**Evolution to dprint plugin:**

Current preprocessor is a separate step. Ideally, this should be a dprint plugin that
runs during formatting. Benefits:

- Single-pass processing
- Better integration with dprint configuration
- Cleaner toolchain

**Migration path:**

1. Keep preprocessor functional (backwards compatibility)
2. Develop dprint plugin with same logic
3. Test plugin thoroughly
4. Deprecate preprocessor, migrate users
5. Remove preprocessor once plugin is stable

### Testing Strategy

**TDD approach:**

- Red test → minimal code → green test
- Each feature: 4-6 test cycles
- Integration tests verify no conflicts
- Edge cases documented and tested

**Test coverage:**

- Valid patterns (should convert)
- Invalid patterns (should skip or error)
- Edge cases (empty blocks, unclosed fences, etc.)
- Integration (multiple fixes together)

### Success Metrics

- All new tests pass
- All existing tests pass (no regressions)
- Code follows existing patterns
- Clear error messages for invalid input
- Documentation complete and accurate
````

---

## Implementation Steps

### Step 1: Update TEST_DATA.md

**Task:** Add "Markdown Cleanup Examples" section

**Location:** After existing examples, before any "Future" sections

**Content:** Copy examples from this plan

**Verification:** Read through, ensure examples are clear and accurate

---

### Step 2: Update DESIGN_DECISIONS.md

**Task:** Add "Markdown Cleanup Architecture" section

**Location:** Append to end of file (latest decisions)

**Content:** Copy design decisions from this plan

**Verification:**

- Design rationale is clear
- Alternatives are documented
- Future direction is explained

---

## Validation

**Manual review:**

- Examples in TEST_DATA.md are accurate
- Design decisions in DESIGN_DECISIONS.md are complete
- All rationale clearly explained
- Future direction documented

**Format check:**

```bash
just format  # Auto-format
```

**No automated tests needed** - documentation only

---

## Notes

- Update after implementation complete (accurate examples)
- Document "why" decisions were made (helps future maintainers)
- Include alternatives considered (shows thought process)
- Explain future direction (guides evolution)
