# Cycle 5.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.2: Worktree-based submodule creation — replace `--reference`

**Objective:** Use `git -C agent-core worktree add` instead of `submodule update --init --reference` for shared object store.

**Prerequisite:** Read justfile `wt-new` recipe lines 150-180 — understand worktree-based submodule approach and object store verification.

**RED Phase:**

**Test:** `test_new_worktree_submodule`
**Assertions:**
- After `new <slug>`, `git -C agent-core worktree list` includes `<wt-path>/agent-core`
- Submodule worktree created at correct path (inside parent worktree)
- Submodule branch named same as parent worktree slug
- No `--reference` used (worktree shares object store inherently)
- Submodule is on correct branch (matches slug)
- Old `--reference` logic NOT present in code

**Expected failure:** AssertionError: `--reference` still used, or submodule not created as worktree, or subprocess.run error from git command

**Why it fails:** Command still uses old `submodule update --init --reference` approach

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_worktree_submodule -v`

---

**GREEN Phase:**

**Implementation:** Replace submodule initialization with worktree-based approach

**Behavior:**
- Check if submodule branch exists: `git -C agent-core rev-parse --verify <slug>` (same pattern as 5.1)
- If submodule branch exists: `git -C agent-core worktree add <wt-path>/agent-core <slug>` (no `-b`)
- If submodule branch doesn't exist: `git -C agent-core worktree add <wt-path>/agent-core -b <slug>`
- Remove all `--reference` logic and `git checkout -B` step (worktree handles branch automatically)

**Approach:** Similar conditional pattern as 5.1, but for submodule in agent-core directory. Reference justfile recipe for command structure.

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Replace `submodule update --init --reference` logic in `new` command
  Location hint: In submodule initialization section
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule branch detection check
  Location hint: Before submodule worktree creation
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditional submodule worktree add command (with or without `-b` flag)
  Location hint: Replace existing submodule initialization
- File: `src/claudeutils/worktree/cli.py`
  Action: Remove `checkout -B` step (no longer needed with worktree)
  Location hint: Delete old checkout logic

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_worktree_submodule -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py::test_new_command_sibling_paths -v`
- Cycle 5.1 test still passes

---
