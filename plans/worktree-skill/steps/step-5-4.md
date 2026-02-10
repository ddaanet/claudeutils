# Cycle 5.4

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 5
**Report Path**: `plans/worktree-skill/reports/cycle-5-4-notes.md`

---

## Cycle 5.4: Justfile Recipe Deletion

**RED — Specify the behavior to verify:**

The justfile still contains five obsolete recipes: `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge`. These are superseded by the `_worktree` CLI subcommand. Running `just --list` should not display these recipes.

The cached help text `.cache/just-help.txt` still references the old recipes. Running `just cache` should regenerate this file without the obsolete entries.

**Test expectations:**
- Justfile does not contain `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, or `wt-merge` recipe definitions
- `just --list` output does not include these five recipes
- `.cache/just-help.txt` does not reference obsolete worktree recipes
- `just cache` completes successfully and updates cached help

**GREEN — Implement to make tests pass:**

Delete the five worktree recipe definitions from the justfile. Run `just cache` to regenerate `.cache/just-help.txt` with the updated recipe list.

**Approach:**
- Edit `justfile`: remove all five `wt-*` recipe blocks (likely contiguous section)
- Run `just cache` to regenerate cached help text
- Verify with `just --list`: no worktree recipes shown
- Verify `.cache/just-help.txt`: no references to `wt-new`, `wt-task`, etc.

**Note:** Recipe deletion may affect line count significantly. The justfile is tracked in version control, so git diff will show exact removals.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-5-4-notes.md
