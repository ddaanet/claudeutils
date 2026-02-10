# Cycle 0.8

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 0
**Report Path**: `plans/worktree-skill/reports/cycle-0-8-notes.md`

---

## Cycle 0.8: clean-tree with non-session dirt

**Objective:** Verify `clean-tree` detects and reports non-session dirty files.

**RED Phase:**
**Test:** `test_clean_tree_dirty_source`
**Assertions:**
- With modified `src/claudeutils/cli.py`, `_worktree clean-tree` exits 1
- Stdout contains porcelain format line: ` M src/claudeutils/cli.py`
**Expected failure:** Current implementation may not print remaining files after filtering
**Why it fails:** Cycle 0.7 may filter and exit, but not print remaining dirty files to stdout before exit 1.
**Verify RED:** `pytest tests/test_worktree_cli.py::test_clean_tree_dirty_source -v`

---

**GREEN Phase:**
**Implementation:** Add output of remaining dirty files after session file filtering.
**Behavior:**
- After filtering session files, checks if remaining porcelain lines exist
- If remaining lines exist: prints all to stdout (one line per file, porcelain format preserved)
- Exits 1 with dirty file list printed
- If no remaining lines: exits 0 silently (already implemented in 0.7)
**Approach:** Output format matches `git status --porcelain` for script parsing. User sees exactly which files block merge ceremony. Submodule files printed with `agent-core/` prefix.
**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add print statement before exit 1 in `clean_tree()`
  Location hint: After filtering, before exit decision
**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_clean_tree_dirty_source -v`
**Verify no regression:** `just test`

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-0-8-notes.md

---
