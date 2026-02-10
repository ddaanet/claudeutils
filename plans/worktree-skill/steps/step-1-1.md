# Cycle 1.1

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-1-notes.md`

---

## Cycle 1.1: new subcommand basic flow

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_basic_flow`:
- Given: Clean git repo with `.gitignore` containing `wt/` entry
- When: Run `_worktree new test-feature`
- Then: Directory `wt/test-feature/` exists
- Then: Branch `test-feature` exists (not `wt/test-feature`)
- Then: Worktree is checked out to branch `test-feature`
- Then: Command exits 0, stdout contains `wt/test-feature`

**Expected failure:** `_worktree new` subcommand does not exist (Click command not defined).

**GREEN: Implement minimal behavior**

Create `new` subcommand in `cli.py` that creates a worktree with branch.

**Behavior:**
- Accept slug as required argument, optional `--base` and `--session` flags
- Create worktree at `wt/{slug}/` on new branch `{slug}` from base commit
- Print worktree path to stdout on success
- Report errors to stderr and exit 1 on failure

**Hints:**
- Use Click's `@worktree.command()` decorator pattern
- Git command: `git worktree add wt/{slug} -b {slug} {base}`
- Skip submodule init for this cycle (added in 1.3-1.4)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-1-notes.md

---
