# Cycle 1.6

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-6-notes.md`

---

## Cycle 1.6: rm subcommand with worktree removal

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_rm_basic`:
- Given: Worktree created via `_worktree new test-feature`
- When: Run `_worktree rm test-feature`
- Then: Directory `wt/test-feature/` does not exist
- Then: Branch `test-feature` does not exist
- Then: Exit 0
- Then: Success message to stderr

Create test `test_worktree_cli.py::test_rm_dirty_warning`:
- Given: Worktree with uncommitted changes (create file in `wt/test-feature/`)
- When: Run `_worktree rm test-feature`
- Then: Warning to stderr about uncommitted changes
- Then: Worktree and branch still removed (forced)
- Then: Exit 0

**Expected failure:** `_worktree rm` subcommand does not exist.

**GREEN: Implement minimal behavior**

Create `rm` subcommand that removes worktree and branch with safety warnings.

**Behavior:**
- Remove worktree directory (if exists) with force flag
- Remove branch (always attempt, even if worktree already gone)
- Warn to stderr if worktree has uncommitted changes (but proceed with removal)
- Warn to stderr if branch is unmerged (but don't fail command)
- Report success to stderr, exit 0

**Approach:**
- Check worktree existence before attempting removal
- Use `--force` for worktree removal (handles submodule and uncommitted changes)
- Use `-d` (not `-D`) for branch removal (preserves unmerged branch warning)
- Detect dirty state before removal for warning message

**Hints:**
- Worktree check: `Path(f'wt/{slug}').exists()`
- Dirty check: `git -C wt/{slug} diff --quiet HEAD` (exit code indicates state)
- Worktree removal: `git worktree remove --force wt/{slug}`
- Branch removal: `git branch -d {slug}` (warns but doesn't block on unmerged)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-6-notes.md

---
