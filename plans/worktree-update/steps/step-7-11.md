# Cycle 7.11

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.11: Phase 3 conflict handling — source file abort

**Objective:** Abort merge and clean debris when source file conflicts remain (manual resolution required).

**RED Phase:**

**Test:** `test_merge_conflict_source_files`
**Assertions:**
- When conflicts remain after auto-resolution (not agent-core, session.md, learnings.md): abort merge
- Run `git merge --abort` to cancel merge
- Clean debris: `git clean -fd` to remove materialized files from merge attempt
- Exit 1 with conflict list: "Merge aborted: conflicts in <file1>, <file2>"
- Exit code 1 (conflicts require manual resolution, not fatal error)

**Expected failure:** AssertionError: merge proceeds with unresolved conflicts, or no abort/cleanup

**Why it fails:** Source file conflict handling not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_source_files -v`

---

**GREEN Phase:**

**Implementation:** Add source file conflict abort logic

**Behavior:**
- After 7.8-7.10 auto-resolutions: check if conflict list still non-empty
- Run `git diff --name-only --diff-filter=U` again to get remaining conflicts
- If conflicts remain:
  - Run `git merge --abort`
  - Run `git clean -fd` to remove debris
  - Exit 1 with message listing conflicted files
- If no conflicts remain (all auto-resolved): proceed to commit

**Approach:** Final conflict check, abort and cleanup if any remain, exit with message

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add final conflict check in `merge` command
  Location hint: After all auto-resolutions (7.8-7.10)
- File: `src/claudeutils/worktree/cli.py`
  Action: Recheck conflict list with git diff
  Location hint: Run same command as 7.7
- File: `src/claudeutils/worktree/cli.py`
  Action: If conflicts remain: abort merge and clean
  Location hint: `git merge --abort && git clean -fd`
- File: `src/claudeutils/worktree/cli.py`
  Action: Exit 1 with conflict list
  Location hint: Print message and sys.exit(1)

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_source_files -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 conflict handling tests still pass

---
