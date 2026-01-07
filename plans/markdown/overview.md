# Markdown Cleanup: Overview and Context

- **Created:** 2026-01-04
- **Status:** Ready for implementation
- **Orchestrator:** Sonnet
- **Task Coders:** Haiku

---

## Purpose

Extend the markdown cleanup preprocessor to handle three new patterns found in
Claude-generated markdown output, specifically from the pytest-markdown-report project.

**Pipeline Context:**

```
Claude output → markdown.py (preprocessor) → dprint (formatter)
```

The markdown.py module is a **preprocessor for Claude markdown-like output** that fixes
structural issues before dprint formatting. It should eventually evolve into a dprint
plugin.

---

## Features to Implement

### Feature 1: Checklist Detection (Any Consistent Prefix)

**Current State:**

- `fix_warning_lines` handles `"⚠️ "` and `Option X:` patterns

**Required:**

- Extend to detect ANY consistent non-markup prefix pattern
- Convert consecutive lines (2+) with similar prefix structure to list items
- Don't trigger on existing list items (lines starting with `-`, `*`, or numbers)

**Example:**

```
Input:
✅ Issue #1: XPASS tests visible
✅ Issue #2: Setup failures captured

Output:
- ✅ Issue #1: XPASS tests visible
- ✅ Issue #2: Setup failures captured
```

---

### Feature 2: Markdown Code Block Nesting

**Current State:**

- No code block nesting logic

**Required:**

- Detect `` ```markdown `` blocks containing inner `` ``` `` fences
- Upgrade outer fence to `` ```` `` (4 backticks) for proper nesting
- **Validation:** Error out if inner `` ``` `` detected in non-markdown blocks
  (`` ```python ``, `` ```bash ``, etc.)
  - Rationale: Prevents dprint post-processing failures

**Example (Success):**

`````
Input:
```markdown
# Example
```python
code
```
```

Output:
````markdown
# Example
```python
code
```
````
`````

**Example (Error):**

````
Input:
```python
def foo():
    """
    Example:
    ```
    code
    ```
    """
```

Output: ERROR - Inner fence in non-markdown block
````

---

### Feature 3: Metadata List Indentation

**Current State:**

- `fix_metadata_blocks` converts consecutive `**Label:** value` lines to list items

**Required:**

- When metadata line (with or without content) is followed by a list, indent that list
  by 2 spaces
- Handles both `**Label:**` and `**Label**:` patterns

**Example:**

```
Input:
**Plan Files:**
- `plans/phase-1.md`
- `plans/phase-2.md`

Output:
- **Plan Files:**
  - `plans/phase-1.md`
  - `plans/phase-2.md`
```

---

## Implementation Approach

### TDD Workflow with Agent Reuse

**Each TDD iteration = one haiku agent call (test-red + code-green):**

1. **Launch haiku agent:** Pass current state + next test requirement
2. **Agent writes test** (red) and **minimal code** to pass (green)
3. **Agent returns:** Updated files + verification
4. **Reuse agent:** Resume same agent for next iteration while context < 75k
5. **New agent:** When context approaches 75k, launch fresh agent

**TDD iteration pattern:**

```
Iteration 1: haiku-agent-1 writes test + minimal code → green
Iteration 2: resume haiku-agent-1 with next test → green
Iteration 3: resume haiku-agent-1 with next test → green
...
Iteration N: context approaching 75k → launch haiku-agent-2
```

**Benefits of agent reuse:**

- Maintains context of previous iterations
- Understands evolving code structure
- Faster than launching new agents each time
- More coherent implementation

**Test increments:**

- Start with simplest case (2 lines with same prefix)
- Add complexity (mixed prefixes, edge cases)
- Test integration with existing fixes

### File Organization

- **Implementation:** `src/claudeutils/markdown.py`
- **Tests:** `tests/test_markdown.py`
- **Plans:** `plans/markdown/feature-*.md`

### Integration Order

Add fixes to `process_lines` in this order:

1. Existing: `fix_dunder_references`
2. Existing: `fix_metadata_blocks`
3. **NEW:** `fix_warning_lines` (extended for Feature 1)
4. Existing: `fix_nested_lists`
5. **NEW:** `fix_metadata_list_indentation` (Feature 3)
6. Existing: `fix_numbered_list_spacing`
7. **NEW:** `fix_markdown_code_blocks` (Feature 2 - last to avoid line interference)

---

## Documentation Updates

**Update markdown.py docstring:**

```python
"""Preprocessor for Claude markdown-like output.

This module fixes structural issues in Claude-generated markdown before
dprint formatting. It should eventually evolve into a dprint plugin.

Pipeline: Claude output → markdown.py fixes → dprint formatting
"""
```

**Add module-level comment explaining purpose:**

- Preprocessor for Claude output
- Fixes structure before dprint pass
- Future: evolve into dprint plugin

---

## Validation Criteria

**For each feature:**

- [ ] Minimal test cases pass
- [ ] Edge cases handled
- [ ] Doesn't break existing tests
- [ ] Follows existing code patterns

**Overall:**

- [ ] All tests pass (`just test`)
- [ ] No regressions in existing functionality
- [ ] Documentation updated
- [ ] Clean integration with existing fixes

---

## Task Breakdown

### Feature 1: Checklist Detection

See: `plans/markdown/feature-1-checklist-detection.md`

- Extend `fix_warning_lines` function
- 4-6 TDD cycles
- Estimated: 30-40 lines of code

### Feature 2: Code Block Nesting

See: `plans/markdown/feature-2-code-block-nesting.md`

- New `fix_markdown_code_blocks` function
- 3-4 TDD cycles
- Estimated: 40-50 lines of code

### Feature 3: Metadata List Indentation

See: `plans/markdown/feature-3-metadata-list-indent.md`

- New `fix_metadata_list_indentation` function
- 4-5 TDD cycles
- Estimated: 35-45 lines of code

### Documentation Updates

See: `plans/markdown/documentation-updates.md`

- Update module docstrings
- Update README.md
- No automated tests (manual verification)

### Agent Documentation Updates

See: `plans/markdown/agent-documentation.md`

- Update `agents/TEST_DATA.md` with markdown cleanup examples
- Update `agents/design-decisions.md` with design rationale
- Document pipeline architecture and error handling decisions

---

## Success Metrics

- All new tests pass
- All existing tests pass
- Code follows existing patterns
- Clean, minimal implementation
- Documentation updated

---

## Next Steps

1. Start with Feature 1 (checklist detection)
2. Complete TDD cycles for Feature 1
3. Move to Feature 2 (code block nesting)
4. Complete TDD cycles for Feature 2
5. Move to Feature 3 (metadata list indentation)
6. Complete TDD cycles for Feature 3
7. Final integration test
8. Documentation updates (module docstrings, README)
9. Agent documentation updates (TEST_DATA.md, design-decisions.md)
