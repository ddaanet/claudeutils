# Cycle 1.3

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-3-notes.md`

---

## Cycle 1.3: new with submodule initialization

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_submodule_init`:
- Given: Repo with submodule `agent-core` initialized in main worktree
- When: Run `_worktree new test-feature`
- Then: Submodule `wt/test-feature/agent-core/` exists and is initialized
- Then: Submodule is at same commit as parent repo's submodule pointer
- Then: Submodule uses local objects from `<project-root>/agent-core` (verify via `.git/objects/info/alternates`)

**Expected failure:** Submodule directory is empty or uninitialized in new worktree.

**GREEN: Implement minimal behavior**

After `git worktree add`, run submodule initialization:
- Get project root: `git rev-parse --show-toplevel`
- Run: `git -C wt/{slug} submodule update --init --reference {project_root}/agent-core`
- `--reference` flag uses local objects as alternates (avoids fetching from remote)
- Error handling: stderr + exit 1 on submodule init failure

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-3-notes.md

---
