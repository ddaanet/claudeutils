# Cycle 0.5

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-5-notes.md`

---

## Cycle 0.5: ls with multiple worktrees

**Objective:** Extend `ls` to parse and output multiple worktrees with slug extraction.

**RED Phase:**
**Test:** `test_ls_multiple_worktrees`
**Assertions:**
- With 2 worktrees (`wt/task-a/` on branch `task-a`, `wt/task-b/` on branch `task-b`), `_worktree ls` outputs exactly 2 lines
- First line matches pattern: `task-a\ttask-a\t<absolute-path>/wt/task-a`
- Second line matches pattern: `task-b\ttask-b\t<absolute-path>/wt/task-b`
- Exit code is 0
**Expected failure:** Current implementation doesn't loop over multiple worktrees or extract slugs correctly
**Why it fails:** Cycle 0.4 implementation may handle empty case only, or slug extraction logic not implemented.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_ls_multiple_worktrees -v`

---

**GREEN Phase:**
**Implementation:** Extend parsing to handle multiple worktrees and extract slugs from paths.
**Behavior:**
- Loops over all `worktree` lines in porcelain output
- For each worktree path matching `wt/<slug>/`, extracts the slug component
- Pairs slug with corresponding branch name from `branch` line
- Emits one tab-delimited line per worktree (format: `<slug>\t<branch>\t<path>`)
**Approach:** Porcelain format groups entries as `worktree`, `HEAD`, `branch`, blank line. Split path on `/`, find `wt` component, take next component as slug. Absolute paths in output enable direct navigation.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Extend `ls()` to loop over worktree entries, extract slugs
  Location hint: Inside `ls()` function body
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_ls_multiple_worktrees -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-5-notes.md

---
