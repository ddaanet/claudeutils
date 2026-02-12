# Cycle 7.8

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 7

---

## Cycle 7.8: Phase 3 conflict handling — agent-core auto-resolve

**Objective:** Auto-resolve agent-core submodule conflicts (already merged in Phase 2).

**RED Phase:**

**Test:** `test_merge_conflict_agent_core`
**Assertions:**
- When `agent-core` in conflict list: run `git checkout --ours agent-core && git add agent-core`
- After resolution: `agent-core` removed from conflict list
- Rationale: submodule already merged in Phase 2, Phase 3 conflict is stale
- No manual intervention required (automatic resolution)

**Expected failure:** AssertionError: agent-core conflict not resolved, or wrong resolution strategy

**Why it fails:** agent-core auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_agent_core -v`

---

**GREEN Phase:**

**Implementation:** Add agent-core conflict auto-resolution

**Behavior:**
- From 7.7: have conflict list
- Check if `"agent-core"` in conflict list
- If present: run `git checkout --ours agent-core` then `git add agent-core`
- Use `--ours` because Phase 2 already resolved submodule (local state is correct)
- Remove from conflict list after resolution

**Approach:** Conditional resolution based on conflict list membership, subprocess commands

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add agent-core conflict check in `merge` command
  Location hint: After merge initiation from 7.7, in conflict handling section
- File: `src/claudeutils/worktree/cli.py`
  Action: Run checkout --ours and git add for agent-core
  Location hint: Conditional on conflict list membership

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_agent_core -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_merge_parent_initiate -v`
- Cycle 7.7 test still passes

---
