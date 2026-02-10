# Cycle 1.2

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-2-notes.md`

---

## Cycle 1.2: new with collision detection

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_new_collision_detection`:
- Given: Existing branch `test-feature` created via `git branch test-feature HEAD`
- When: Run `_worktree new test-feature`
- Then: Exit 1
- Then: stderr contains error message about existing branch
- Then: No `wt/test-feature/` directory created

Create test `test_worktree_cli.py::test_new_directory_collision`:
- Given: Existing directory `wt/test-feature/` (untracked, created via `mkdir -p`)
- When: Run `_worktree new test-feature`
- Then: Exit 1
- Then: stderr contains error message about existing directory
- Then: No new branch created

**Expected failure:** Command proceeds despite collisions, creates worktree or fails with git error (not clean validation message).

**GREEN: Implement minimal behavior**

Add collision detection to `new` subcommand before creating worktree.

**Behavior:**
- Validate no existing `wt/{slug}/` directory
- Validate no existing `{slug}` branch
- Report specific error (directory or branch collision) to stderr and exit 1 if collision found
- Only proceed to worktree creation if both checks pass

**Hints:**
- Check directory: `Path('wt/{slug}').exists()`
- Check branch: `git rev-parse --verify {slug}` (exit code != 0 means branch doesn't exist)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-2-notes.md

---
