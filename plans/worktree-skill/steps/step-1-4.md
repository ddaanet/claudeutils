# Cycle 1.4

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-4-notes.md`

---

## Cycle 1.4: new with submodule branching

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_submodule_branching`:
- Given: Repo with submodule initialized
- When: Run `_worktree new test-feature`
- Then: Submodule in `wt/test-feature/agent-core/` is on branch `test-feature` (not detached HEAD)
- Then: Branch is new (not existing branch)
- Then: Branch starts at submodule's current commit

**Expected failure:** Submodule remains in detached HEAD state after initialization.

**GREEN: Implement minimal behavior**

After submodule initialization, create and checkout branch in submodule:
- Run: `git -C wt/{slug}/agent-core checkout -b {slug}`
- This creates new branch at current HEAD (the commit from submodule pointer)
- Error handling: stderr + exit 1 on branch creation failure

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-4-notes.md

---
