# Cycle 2.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 2

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
