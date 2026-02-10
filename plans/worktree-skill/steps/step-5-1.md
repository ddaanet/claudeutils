# Cycle 5.1

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 5
**Report Path**: `plans/worktree-skill/reports/cycle-5-1-notes.md`

---

## Cycle 5.1: CLI Registration and .gitignore

**RED — Specify the behavior to verify:**

The main `claudeutils` CLI does not yet expose the `_worktree` subcommand. Running `claudeutils _worktree --help` should display the worktree command group with all six subcommands (new, rm, merge, ls, clean-tree, add-commit).

The project `.gitignore` does not yet exclude the `wt/` directory. Git status should not show untracked `wt/` worktree directories.

**Test expectations:**
- `claudeutils _worktree --help` exits 0 and displays Click group help with six subcommands listed
- `.gitignore` contains `wt/` entry
- Creating a test worktree `wt/test-slug/` results in git status showing no untracked directory warning

**GREEN — Implement to make tests pass:**

Import the worktree command group from `claudeutils.worktree.cli` and register it with the main CLI using `cli.add_command(worktree, "_worktree")`. The underscore prefix indicates this is an internal subcommand (invoked by skill, not users directly).

Add `wt/` entry to `.gitignore` to exclude worktree directories from version control.

**Approach:**
- Edit `src/claudeutils/cli.py`: add import statement for worktree command group, register with main CLI
- Edit `.gitignore`: append `wt/` entry (one line)
- Verify with manual test: `claudeutils _worktree --help` displays expected output

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-5-1-notes.md

---
