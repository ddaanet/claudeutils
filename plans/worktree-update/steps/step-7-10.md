# Cycle 7.10

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.10: Phase 3 conflict handling — learnings.md auto-resolve (append theirs-only)

**Objective:** Auto-resolve learnings.md conflicts by keeping both (append theirs-only content to ours).

**RED Phase:**

**Test:** `test_merge_conflict_learnings_md`
**Assertions:**
- When `agents/learnings.md` in conflict list: append theirs-only content to ours
- Extract ours: `git show :2:agents/learnings.md`
- Extract theirs: `git show :3:agents/learnings.md`
- Find theirs-only lines (in theirs, not in ours)
- Result: ours content + separator + theirs-only content
- Write merged result and stage: `git add agents/learnings.md`

**Expected failure:** AssertionError: learnings.md conflict not resolved, or wrong merge strategy (not both-sides)

**Why it fails:** learnings.md auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_learnings_md -v`

---

**GREEN Phase:**

**Implementation:** Add learnings.md conflict auto-resolution (append theirs-only)

**Behavior:**
- From 7.7: have conflict list
- Check if `"agents/learnings.md"` in conflict list
- If present:
  - Extract ours: `git show :2:agents/learnings.md`
  - Extract theirs: `git show :3:agents/learnings.md`
  - Find theirs-only lines (line-by-line comparison)
  - Compose result: ours + theirs-only lines
  - Write to `agents/learnings.md`
  - Run `git add agents/learnings.md`
- Remove from conflict list after resolution

**Approach:** git show for stage extraction, line-by-line diff, file write and stage

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add learnings.md conflict check in `merge` command
  Location hint: After session.md resolution from 7.9
- File: `src/claudeutils/worktree/cli.py`
  Action: Extract both sides using git show
  Location hint: Use subprocess to get `:2:` and `:3:` content
- File: `src/claudeutils/worktree/cli.py`
  Action: Find theirs-only lines (set difference on lines)
  Location hint: Split into lines, compare
- File: `src/claudeutils/worktree/cli.py`
  Action: Write merged result and stage
  Location hint: Write to file, git add

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_learnings_md -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 tests still pass

---
