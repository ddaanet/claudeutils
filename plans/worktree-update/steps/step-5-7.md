# Cycle 5.7

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.7: Task mode — slug derivation, focused session, tab-separated output

**Objective:** Implement task mode logic combining all helper functions and special output format.

**RED Phase:**

**Test:** `test_new_task_mode_integration`
**Assertions:**
- `claudeutils _worktree new --task "Implement feature X"` derives slug `"implement-feature-x"`
- Focused session generated from `agents/session.md` (calls `focus_session()`)
- Focused session written to temporary file for session creation
- Worktree created at derived slug path
- Output format: `<slug>\t<path>` (tab-separated, not just path)
- Temporary session file cleaned up after creation

**Expected failure:** AssertionError: wrong output format (no tab separator), or focused session not generated, or slug not derived

**Why it fails:** Task mode logic not implemented (slug derivation, focus_session call, output format)

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_task_mode_integration -v`

---

**GREEN Phase:**

**Implementation:** Wire task mode logic using helper functions from previous phases

**Behavior:**
- When `--task` provided:
  1. Derive slug: `slug = derive_slug(task_name)`
  2. Generate focused session: `session_content = focus_session(task_name, session_md_path)`
  3. Write to temp file: use `tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)`
  4. Proceed with normal `new` logic using derived slug and temp session path
  5. At end: print `f"{slug}\t{wt_path}"` (tab-separated) instead of just path
  6. Clean up temp file in finally block
- When explicit slug mode: output just path (existing behavior)

**Approach:** Conditional logic branch for task mode, compose helper functions, special output format

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add task mode branch in `new` command
  Location hint: Early in function, after validation
- File: `src/claudeutils/worktree/cli.py`
  Action: Call `derive_slug(task_name)` to get slug
  Location hint: In task mode branch
- File: `src/claudeutils/worktree/cli.py`
  Action: Call `focus_session(task_name, session_md_path)` to generate content
  Location hint: After slug derivation
- File: `src/claudeutils/worktree/cli.py`
  Action: Create temp file with focused session content
  Location hint: Use `tempfile` module, write content
- File: `src/claudeutils/worktree/cli.py`
  Action: Update output format — tab-separated for task mode, path-only for explicit mode
  Location hint: At end of function, conditional print based on mode
- File: `src/claudeutils/worktree/cli.py`
  Action: Add finally block to clean up temp file
  Location hint: Wrap main logic in try-finally

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_task_mode_integration -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous tests still pass (explicit mode unchanged)

---
