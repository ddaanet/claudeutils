# Cycle 0.3

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-3-notes.md`

---

## Cycle 0.3: Slug Derivation Utility

**Objective:** Convert task names to worktree slugs with deterministic transformation.

**RED Phase:**
**Test:** `test_derive_slug`
**Assertions:**
- `derive_slug("Implement ambient awareness")` returns `"implement-ambient-awareness"`
- `derive_slug("Design runbook identifiers")` returns `"design-runbook-identifiers"`
- `derive_slug("Review agent-core orphaned revisions")` returns `"review-agent-core-orphaned-rev"` (truncated at 30 chars)
- `derive_slug("Multiple    spaces   here")` returns `"multiple-spaces-here"` (collapsed)
- `derive_slug("Special!@#$%chars")` returns `"special-chars"` (removed)
**Expected failure:** `AttributeError` or `NameError` (function doesn't exist)
**Why it fails:** No `derive_slug` function is defined in `cli.py`.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_derive_slug -v`

---

**GREEN Phase:**
**Implementation:** Pure function performing string transformation to slug format.
**Behavior:**
- Converts input to lowercase
- Replaces sequences of non-alphanumeric characters with single hyphens
- Strips leading and trailing hyphens
- Truncates to maximum 30 characters
- Strips trailing hyphens after truncation
**Approach:** Use regex substitution with `re.sub(r'[^a-z0-9]+', '-', ...)` pattern. Apply string slicing for truncation.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `derive_slug(task_name: str, max_length: int = 30) -> str` function
  Location hint: Module level, above Click group (utilities before commands)
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_derive_slug -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-3-notes.md

---
