# Cycle 0.7

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-7-notes.md`

---

## Cycle 0.7: clean-tree with session files

**Objective:** Extend `clean-tree` to exempt session context files from dirty check.

**RED Phase:**
**Test:** `test_clean_tree_session_files_exempt`
**Assertions:**
- With modified `agents/session.md`, `agents/jobs.md`, `agents/learnings.md`, `_worktree clean-tree` exits 0
- No output to stdout (silent success, session files are exempt)
**Expected failure:** Current implementation treats session files as dirty, exits 1
**Why it fails:** Cycle 0.6 implementation doesn't filter session files, reports any modified file.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_clean_tree_session_files_exempt -v`

---

**GREEN Phase:**
**Implementation:** Add filtering to exclude session context files from status output.
**Behavior:**
- After getting porcelain status for parent and submodule, filters output lines
- Removes lines where filename is `agents/session.md`, `agents/jobs.md`, or `agents/learnings.md`
- Applies same filter to both parent and submodule status
- Exits 0 if filtered output empty, exits 1 with remaining files otherwise
**Approach:** Use exact filename match (no wildcards). Porcelain format: `XY filename` where filename follows space. Session files exempt because they're auto-committed during merge ceremony.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add filtering logic inside `clean_tree()` function
  Location hint: After status command execution, before exit decision
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_clean_tree_session_files_exempt -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-7-notes.md

---
