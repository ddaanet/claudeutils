# Cycle 2.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.1: Create `add_sandbox_dir()` — basic JSON read/write (happy path)

**Objective:** Add container directory to existing settings file with all required keys present.

**RED Phase:**

**Test:** `test_add_sandbox_dir_happy_path`
**Assertions:**
- Given settings file with structure `{"permissions": {"additionalDirectories": ["/existing/path"]}}`
- After `add_sandbox_dir("/new/path", settings_path)`, file contains both `/existing/path` and `/new/path`
- JSON structure preserved (all existing keys intact)
- File is valid JSON after write
- Array order preserved (new path appended, not prepended)

**Expected failure:** NameError: function `add_sandbox_dir` not defined

**Why it fails:** Function doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Create function to read JSON, append path to array, write back

**Behavior:**
- Read settings file as JSON
- Navigate to `permissions.additionalDirectories` (assume keys exist in happy path)
- Append new path to array (no deduplication in this cycle)
- Write JSON back with indent=2 for readability

**Approach:** Use `json.load()` and `json.dump()` from stdlib, straightforward nested key access

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new function `add_sandbox_dir(container: str | Path, settings_path: str | Path)` at module level
  Location hint: After `wt_path()` function, before command definitions
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement JSON read → append → write logic
  Location hint: Function body reads JSON, navigates to nested array, appends path, writes back with formatting

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_happy_path -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 tests still pass

---
