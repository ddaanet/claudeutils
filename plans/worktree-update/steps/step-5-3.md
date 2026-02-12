# Cycle 5.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.3: Existing submodule branch detection and reuse

**Objective:** Detect and reuse existing submodule branches (don't create duplicate branches).

**RED Phase:**

**Test:** `test_new_submodule_branch_reuse`
**Assertions:**
- Given existing submodule branch "feature-x" in agent-core
- `new feature-x` reuses parent branch AND submodule branch (both exist)
- No error from git about branch already existing
- Submodule worktree points to existing branch (not new branch)
- Branch refs preserved (not recreated)

**Expected failure:** Error from git attempting to create branch that already exists, or wrong branch checked out

**Why it fails:** Submodule branch detection not implemented (always tries to create with `-b`)

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_submodule_branch_reuse -v`

---

**GREEN Phase:**

**Implementation:** Verify Cycle 5.2 logic handles submodule branch detection correctly

**Behavior:**
- Logic from 5.2 already checks submodule branch existence
- Conditional logic handles both cases (existing vs new)
- No additional code needed if 5.2 implemented correctly
- Test verifies the behavior works end-to-end

**Approach:** This cycle validates that 5.2's branch detection applies to both parent and submodule

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Verify submodule branch detection logic from 5.2 is correct (likely no changes needed)
  Location hint: Review conditional logic in submodule worktree creation

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_submodule_branch_reuse -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All Cycle 5.1 and 5.2 tests still pass

---
