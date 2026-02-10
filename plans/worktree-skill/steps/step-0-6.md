# Cycle 0.6

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-6-notes.md`

---

## Cycle 0.6: clean-tree with clean repo

**Objective:** Implement `clean-tree` subcommand that validates clean state silently.

**RED Phase:**
**Test:** `test_clean_tree_clean`
**Assertions:**
- Running `claudeutils _worktree clean-tree` in clean repo with submodule exits 0
- No output to stdout or stderr (silent success)
**Expected failure:** `AttributeError` or command not found error
**Why it fails:** The `clean-tree` subcommand doesn't exist in the Click group yet.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_clean_tree_clean -v`

---

**GREEN Phase:**
**Implementation:** Add `clean-tree` subcommand checking parent and submodule status.
**Behavior:**
- Executes `git status --porcelain` for parent repo
- Executes `git -C agent-core status --porcelain` for submodule
- If both outputs are empty: exits 0 silently (clean state)
- If either has content: prints dirty files to stdout, exits 1
**Approach:** Use `@worktree.command(name="clean-tree")` decorator. Porcelain format: `XY filename` where X=index status, Y=worktree status. Empty output = clean state. Session file filtering added in next cycle.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add `clean_tree()` function with `@worktree.command(name="clean-tree")` decorator
  Location hint: After `ls`, before end of file
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_clean_tree_clean -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-6-notes.md

---
