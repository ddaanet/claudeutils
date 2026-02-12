# Cycle 5.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.4: Sandbox registration — both main and worktree settings files

**Objective:** Register container directory in sandbox permissions for both main repo and worktree.

**RED Phase:**

**Test:** `test_new_sandbox_registration`
**Assertions:**
- After `new <slug>`, `.claude/settings.local.json` contains container path in `permissions.additionalDirectories`
- Worktree settings file `<wt-path>/.claude/settings.local.json` also contains container path
- Both files are valid JSON
- Container path is absolute (not relative)
- Deduplication works (running command twice doesn't add duplicate entries)

**Expected failure:** AssertionError: settings files don't exist or don't contain container path

**Why it fails:** Sandbox registration not yet called from `new` command

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_sandbox_registration -v`

---

**GREEN Phase:**

**Implementation:** Call `add_sandbox_dir()` function for both main and worktree settings

**Behavior:**
- Determine container path (absolute) from `wt_path()` result
- Call `add_sandbox_dir(container, ".claude/settings.local.json")` for main repo
- Call `add_sandbox_dir(container, f"{wt_path}/.claude/settings.local.json")` for worktree
- Function handles file creation, nested keys, deduplication (from Phase 2)

**Approach:** Two function calls at appropriate point in `new` command (after worktree creation)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `add_sandbox_dir()` calls in `new` command
  Location hint: After worktree and submodule creation, before env init
- File: `src/claudeutils/worktree/cli.py`
  Action: Call for main settings: `add_sandbox_dir(container, ".claude/settings.local.json")`
  Location hint: Use container path from `wt_path()` result
- File: `src/claudeutils/worktree/cli.py`
  Action: Call for worktree settings: `add_sandbox_dir(container, f"{wt_path}/.claude/settings.local.json")`
  Location hint: After main settings call

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_sandbox_registration -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All previous Cycle 5 tests still pass

---
