# Cycle 0.4

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-4-notes.md`

---

## Cycle 0.4: ls subcommand structure

**Objective:** Implement `ls` subcommand that lists worktrees with empty output for no worktrees.

**RED Phase:**
**Test:** `test_ls_empty`
**Assertions:**
- Running `claudeutils _worktree ls` in repo with no worktrees exits with code 0
- Output is empty (no worktree lines printed)
**Expected failure:** `AttributeError` or command not found error
**Why it fails:** The `ls` subcommand doesn't exist in the Click group yet.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_ls_empty -v`

---

**GREEN Phase:**
**Implementation:** Add `ls` subcommand with porcelain parsing.
**Behavior:**
- Executes `git worktree list --porcelain` to get structured output
- Parses porcelain format to extract worktree path and branch name
- For non-main worktrees: extracts slug from path, emits tab-delimited line
- Exits 0 unconditionally (empty output for no worktrees is valid)
**Approach:** Use `@worktree.command()` decorator. Parse porcelain format (worktree/branch line pairs). Main worktree (project root) excluded from output. Tab-delimited format enables machine parsing.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `ls()` function with `@worktree.command()` decorator
  Location hint: After `derive_slug`, before end of file
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_ls_empty -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-4-notes.md

---
