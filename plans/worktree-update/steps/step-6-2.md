# Cycle 6.2

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.2: Worktree registration probing — parent and submodule

**Objective:** Detect whether parent and/or submodule worktrees are registered (handle partial states).

**RED Phase:**

**Test:** `test_rm_worktree_registration_probing`
**Assertions:**
- Given registered parent worktree at `<wt-path>`: `git worktree list` contains path
- Given registered submodule worktree at `<wt-path>/agent-core`: `git -C agent-core worktree list` contains path
- Probe detects: both registered, only parent, only submodule, neither registered
- Function handles all four states without error
- Registration info used to decide removal commands (probed state determines which `git worktree remove` calls to make)

**Expected failure:** Error when worktree not registered, or wrong removal commands attempted

**Why it fails:** No registration probing, assumes both always registered

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_worktree_registration_probing -v`

---

**GREEN Phase:**

**Implementation:** Add registration detection for parent and submodule worktrees

**Behavior:**
- Parse `git worktree list --porcelain` output to check if `<wt-path>` is registered
- Parse `git -C agent-core worktree list --porcelain` to check if `<wt-path>/agent-core` is registered
- Use path matching (not grep) for reliable detection
- Store boolean flags: `parent_registered`, `submodule_registered`
- Use flags to conditionally execute removal commands (only remove what's registered)

**Approach:** Two subprocess calls with output parsing, path-based matching, boolean flags

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add parent registration check in `rm` command
  Location hint: Run `git worktree list --porcelain`, parse output for `<wt-path>`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule registration check
  Location hint: Run `git -C agent-core worktree list --porcelain`, parse for `<wt-path>/agent-core`
- File: `src/claudeutils/worktree/cli.py`
  Action: Store registration state as boolean flags
  Location hint: Two variables tracking parent and submodule registration

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_worktree_registration_probing -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_rm_command_path_resolution -v`
- Cycle 6.1 test still passes

---
