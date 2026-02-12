# Phase 2: Sandbox Registration

**Complexity:** Medium (4 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** JSON manipulation for sandbox permissions — add worktree container to allowed directories.

**Dependencies:** Phase 1 (needs `wt_path()` for container determination)

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

## Cycle 2.2: Missing file handling — create from scratch

**Objective:** Handle case where settings file doesn't exist (create new file with minimal structure).

**RED Phase:**

**Test:** `test_add_sandbox_dir_missing_file`
**Assertions:**
- Given settings file path that doesn't exist
- After `add_sandbox_dir("/new/path", nonexistent_path)`, file exists
- Created file is valid JSON
- Contains structure: `{"permissions": {"additionalDirectories": ["/new/path"]}}`
- File has correct minimal structure (no extra keys)

**Expected failure:** FileNotFoundError or JSONDecodeError when trying to read nonexistent file

**Why it fails:** Function assumes file exists, doesn't handle missing file case

**Verify RED:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_missing_file -v`

---

**GREEN Phase:**

**Implementation:** Add file existence check and initial structure creation

**Behavior:**
- Check if settings file exists via `Path(settings_path).exists()`
- If missing: create parent directories, initialize with `{}` structure
- Then proceed with normal append logic (which will handle nested key creation in 2.3)

**Approach:** Conditional at function start — if not exists, create parent dirs and empty JSON file

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add file existence check at start of `add_sandbox_dir()` function
  Location hint: Before JSON read operation
- File: `src/claudeutils/worktree/cli.py`
  Action: Create parent directories with `Path(settings_path).parent.mkdir(parents=True, exist_ok=True)` if needed
  Location hint: In the file-doesn't-exist branch
- File: `src/claudeutils/worktree/cli.py`
  Action: Initialize with `{}` and write to file
  Location hint: After parent directory creation

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_missing_file -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_add_sandbox_dir_happy_path -v`
- Cycle 2.1 test still passes

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
