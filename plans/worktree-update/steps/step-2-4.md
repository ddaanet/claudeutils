# Cycle 2.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.4: Deduplication logic — avoid adding existing paths

**Objective:** Check if path already exists in array before adding (idempotent operation).

**RED Phase:**

**Test:** `test_add_sandbox_dir_deduplication`
**Assertions:**
- Given settings file with `additionalDirectories: ["/path/a", "/path/b"]`
- After `add_sandbox_dir("/path/a", settings_path)`, array unchanged (no duplicate)
- After `add_sandbox_dir("/path/c", settings_path)`, array becomes `["/path/a", "/path/b", "/path/c"]`
- Deduplication uses exact string match (not path normalization)
- Function is idempotent (calling twice with same path has same effect as calling once)

**Expected failure:** AssertionError: duplicate path added to array

**Why it fails:** Function always appends without checking for existence

**Verify RED:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_deduplication -v`

---

**GREEN Phase:**

**Implementation:** Add existence check before append

**Behavior:**
- Before appending path to `additionalDirectories` array, check if path already in list
- Use simple `in` operator for membership check (string comparison)
- Only append if not present
- Preserves order of existing paths

**Approach:** Conditional append — `if container not in dirs: dirs.append(container)`

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add membership check before append in `add_sandbox_dir()` function
  Location hint: Where function appends to `additionalDirectories` list
- File: `src/claudeutils/worktree/cli.py`
  Action: Wrap append in conditional: only append if not already present
  Location hint: Replace unconditional `list.append()` with conditional

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_deduplication -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 2 tests still pass

---

**Checkpoint: Post-Phase 2**

**Type:** Light checkpoint (Fix + Functional)

**Process:**
1. **Fix:** Run `just dev`. If failures, sonnet quiet-task diagnoses and fixes. Commit when passing.
2. **Functional:** Sonnet reviews Phase 2 implementations against design.
   - Check: Are JSON manipulations real or stubbed? Does deduplication actually work?
   - Check: Are file operations tested with real filesystem or just mocked?
   - If stubs found: STOP, report which implementations need real behavior
   - If all functional: Proceed to Phase 3

**Rationale:** JSON manipulation is foundational for sandbox registration. Validate correctness before building dependent phases.

# Phase 3: Slug Derivation Edge Cases

**Complexity:** Low (1 cycle)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Fix edge cases in existing `derive_slug()` function — already exists but needs edge case verification.

**Dependencies:** Phase 1 (function already exists in codebase, verifying behavior)

---
