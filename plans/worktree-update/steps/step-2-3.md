# Cycle 2.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Cycle 2.3: Nested key creation — `permissions.additionalDirectories` absent

**Objective:** Handle case where JSON exists but nested keys are missing (create key path).

**RED Phase:**

**Test:** `test_add_sandbox_dir_missing_keys`
**Assertions:**
- Given settings file with `{}` or `{"permissions": {}}` (missing `additionalDirectories` key)
- After `add_sandbox_dir("/new/path", settings_path)`, nested structure created
- Result contains `permissions.additionalDirectories` as array with single path
- No existing keys removed (if `permissions` had other keys, they're preserved)
- Works for partial key presence: just `permissions` missing, or both missing

**Expected failure:** KeyError when accessing `data["permissions"]["additionalDirectories"]` on missing keys, or TypeError if `permissions` exists but isn't a dict

**Why it fails:** Function assumes nested keys exist, doesn't create them

**Verify RED:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_missing_keys -v`

---

**GREEN Phase:**

**Implementation:** Add nested key creation with `.setdefault()` pattern

**Behavior:**
- Use `.setdefault()` to create keys if missing: `data.setdefault("permissions", {})` and `perms.setdefault("additionalDirectories", [])`
- Pattern ensures keys exist without overwriting if present
- Creates empty array for `additionalDirectories` if missing
- Preserves existing values at each level

**Approach:** Replace direct key access with `.setdefault()` pattern for safe nested navigation

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace nested key access in `add_sandbox_dir()` with `.setdefault()` pattern
  Location hint: Where function accesses `data["permissions"]["additionalDirectories"]`
- File: `src/claudeutils/worktree/cli.py`
  Action: Ensure pattern handles both missing `permissions` and missing `additionalDirectories`
  Location hint: Two-level `.setdefault()` calls

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_missing_keys -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Cycle 2.1 and 2.2 tests still pass

---
