# Phase 3: Slug Derivation Edge Cases

**Complexity:** Low (1 cycle)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Fix edge cases in existing `derive_slug()` function — already exists but needs edge case verification.

**Dependencies:** Phase 1 (function already exists in codebase, verifying behavior)

---

## Cycle 3.1: Edge case handling — special chars, truncation, empty input

**Objective:** Verify and fix edge cases in slug derivation (function exists but may have gaps).

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` lines 1-200 — understand existing `derive_slug()` implementation and current edge case handling.

**RED Phase:**

**Test:** `test_derive_slug_edge_cases`
**Assertions:**
- Special characters replaced with hyphens: `derive_slug("feat: add login")` returns `"feat-add-login"`
- Multiple consecutive hyphens collapsed: `derive_slug("fix:  space")` returns `"fix-space"` (not `"fix--space"`)
- Trailing hyphen removed: `derive_slug("feature-")` returns `"feature"` (not `"feature-"`)
- Leading hyphen removed: `derive_slug("-feature")` returns `"feature"`
- Long string truncated to reasonable length (e.g., 50 chars) with trailing hyphen cleanup after truncation
- Empty string raises ValueError: `derive_slug("")` raises ValueError with message "slug cannot be empty"
- Whitespace-only string raises ValueError: `derive_slug("   ")` raises ValueError
- Lowercase conversion: `derive_slug("Feature-Name")` returns `"feature-name"`

**Expected failure:** AssertionError: various edge cases not handled (trailing hyphens, empty input, etc.) or AttributeError if function doesn't exist at expected location

**Why it fails:** Existing function may not handle all edge cases correctly

**Verify RED:** `pytest tests/test_worktree_cli.py::test_derive_slug_edge_cases -v`

---

**GREEN Phase:**

**Implementation:** Fix edge cases in existing `derive_slug()` function

**Behavior:**
- Input validation: check for empty/whitespace-only, raise ValueError if invalid
- Character replacement: replace non-alphanumeric chars with hyphens (except existing hyphens)
- Collapse multiple consecutive hyphens into single hyphen
- Strip leading and trailing hyphens
- Truncate to max length (e.g., 50 chars), then strip trailing hyphen again (truncation might create new trailing hyphen)
- Convert to lowercase

**Approach:** String processing pipeline — validate, replace, collapse, strip, truncate, strip again, lowercase

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Update `derive_slug()` function to handle edge cases
  Location hint: Find existing function, enhance validation and string processing
- File: `src/claudeutils/worktree/cli.py`
  Action: Add empty/whitespace validation at function start
  Location hint: Before any string processing
- File: `src/claudeutils/worktree/cli.py`
  Action: Add trailing hyphen stripping AFTER truncation (critical: truncation can create new trailing hyphens)
  Location hint: After truncation logic

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_derive_slug_edge_cases -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All existing slug tests still pass

---
