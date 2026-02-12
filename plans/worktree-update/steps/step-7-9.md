# Cycle 7.9

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.9: Phase 3 conflict handling — session.md auto-resolve (task extraction)

**Objective:** Auto-resolve session.md conflicts by keeping ours and printing new worktree tasks for manual extraction.

**Prerequisite:** Read design lines 150-154 — understand session.md conflict handling (keep ours, extract new tasks from theirs).

**RED Phase:**

**Test:** `test_merge_conflict_session_md`
**Assertions:**
- When `agents/session.md` in conflict list: extract new tasks from `:3:agents/session.md` (theirs)
- New tasks: lines matching `- [ ] **<name>**` pattern that don't exist in `:2:agents/session.md` (ours)
- Resolution: run `git checkout --ours agents/session.md && git add agents/session.md`
- Warning printed with list of new tasks for manual extraction
- Warning message actionable (helps user transfer tasks manually)

**Expected failure:** AssertionError: session.md conflict not resolved, or no task extraction warning

**Why it fails:** session.md auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_session_md -v`

---

**GREEN Phase:**

**Implementation:** Add session.md conflict auto-resolution with task extraction

**Behavior:**
- From 7.7: have conflict list
- Check if `"agents/session.md"` in conflict list
- If present:
  - Extract ours tasks: `git show :2:agents/session.md | grep "- [ ] \*\*.*\*\*"`
  - Extract theirs tasks: `git show :3:agents/session.md | grep "- [ ] \*\*.*\*\*"`
  - Find new tasks (in theirs, not in ours)
  - Run `git checkout --ours agents/session.md && git add agents/session.md`
  - Print warning with new task list
- Remove from conflict list after resolution

**Approach:** git show for stage extraction, grep/parsing for task detection, warning output

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add session.md conflict check in `merge` command
  Location hint: After agent-core resolution from 7.8
- File: `src/claudeutils/worktree/cli.py`
  Action: Extract tasks from both sides using git show
  Location hint: Use subprocess to get `:2:` and `:3:` content
- File: `src/claudeutils/worktree/cli.py`
  Action: Find new tasks (set difference)
  Location hint: Compare task lists
- File: `src/claudeutils/worktree/cli.py`
  Action: Resolve with --ours and print warning
  Location hint: Checkout ours, add, print new tasks

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_session_md -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 tests still pass

---
