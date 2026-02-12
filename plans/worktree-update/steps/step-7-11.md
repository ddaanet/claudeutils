# Cycle 7.11

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.11: Phase 3 conflict handling — jobs.md auto-resolve

**Objective:** Auto-resolve jobs.md conflicts by keeping ours with warning (plan status is local state).

**RED Phase:**

**Test:** `test_merge_conflict_jobs_md`
**Assertions:**
- When `agents/jobs.md` in conflict list: run `git checkout --ours agents/jobs.md && git add agents/jobs.md`
- After resolution: `agents/jobs.md` removed from conflict list
- Warning printed: "jobs.md conflict: kept ours (local plan status)"
- No manual intervention required

**Expected failure:** AssertionError: jobs.md conflict not resolved, or no warning

**Why it fails:** jobs.md auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_jobs_md -v`

---

**GREEN Phase:**

**Implementation:** Add jobs.md conflict auto-resolution

**Behavior:**
- From 7.7: have conflict list
- Check if `"agents/jobs.md"` in conflict list
- If present: run `git checkout --ours agents/jobs.md` then `git add agents/jobs.md`
- Print warning: "jobs.md conflict: kept ours (local plan status)"
- Remove from conflict list after resolution

**Approach:** Same pattern as agent-core resolution (7.8) — known-file auto-resolve with warning

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add jobs.md conflict check in `merge` command
  Location hint: After learnings.md resolution from 7.10, before source file abort
- File: `src/claudeutils/worktree/cli.py`
  Action: Run checkout --ours and git add for jobs.md
  Location hint: Conditional on conflict list membership

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_jobs_md -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 conflict handling tests still pass

---
