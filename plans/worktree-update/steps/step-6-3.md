# Cycle 6.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 6

---

## Cycle 6.3: Submodule-first removal ordering

**Objective:** Remove submodule worktree BEFORE parent worktree (git enforces this order).

**Prerequisite:** Read design lines 109-112 — understand submodule-first removal ordering requirement and git error message.

**RED Phase:**

**Test:** `test_rm_submodule_first_ordering`
**Assertions:**
- Removal order: submodule worktree removed first, parent worktree second
- When both registered: `git -C agent-core worktree remove --force <path>/agent-core` runs before `git worktree remove --force <path>`
- If order violated (parent first): git refuses with error "fatal: 'remove' refusing to remove..."
- Test verifies correct order by checking command sequence (mock subprocess to track order)
- When only parent registered: only parent removal attempted (no submodule command)

**Expected failure:** AssertionError: wrong removal order, or error from git when order violated

**Why it fails:** Removal order not enforced, or both commands attempted regardless of registration state

**Verify RED:** `pytest tests/test_worktree_cli.py::test_rm_submodule_first_ordering -v`

---

**GREEN Phase:**

**Implementation:** Enforce submodule-first removal order using registration flags

**Behavior:**
- If `submodule_registered == True`: run `git -C agent-core worktree remove --force <wt-path>/agent-core`
- Then, if `parent_registered == True`: run `git worktree remove --force <wt-path>`
- Order guaranteed by sequential execution (submodule first, then parent)
- Use `--force` flag to bypass uncommitted changes warnings (already warned in 6.1)

**Approach:** Sequential subprocess calls conditional on registration flags, explicit ordering

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule removal in `rm` command
  Location hint: First removal step, conditional on `submodule_registered`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add parent removal after submodule removal
  Location hint: Second removal step, conditional on `parent_registered`
- File: `src/claudeutils/worktree/cli.py`
  Action: Use `--force` flag for both removals
  Location hint: In git worktree remove commands

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_rm_submodule_first_ordering -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Cycle 6.1 and 6.2 tests still pass

---
