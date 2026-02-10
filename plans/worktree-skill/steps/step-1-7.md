# Cycle 1.7

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 1
**Report Path**: `plans/worktree-skill/reports/cycle-1-7-notes.md`

---

## Cycle 1.7: rm with branch-only cleanup

**RED: Test behavior before implementation**

Create test `test_worktree_cli.py::test_rm_branch_only`:
- Given: Worktree created via `_worktree new test-feature`, then worktree manually removed via `rm -rf wt/test-feature` (simulating external cleanup)
- Given: Branch `test-feature` still exists (verify with `git branch --list`)
- When: Run `_worktree rm test-feature`
- Then: Exit 0
- Then: Branch `test-feature` removed
- Then: No error about missing worktree directory

**Expected failure:** Command exits 1 when worktree directory missing (fails to handle branch-only scenario).

**GREEN: Implement minimal behavior**

Make `rm` subcommand handle branch-only cleanup (worktree already removed externally).

**Behavior:**
- Skip worktree removal step if directory doesn't exist (no error)
- Always attempt branch removal (works whether worktree exists or not)
- Success message reflects actual cleanup performed
- Exit 0 in all cases (idempotent)

**Approach:**
- Check directory existence before worktree removal
- Branch removal is independent of worktree state
- Adjust output message based on what was actually cleaned

**Why:** Makes `rm` idempotent and resilient to partial cleanup states (e.g., user manually deleted worktree directory but branch remains).

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-1-7-notes.md

### Phase 2: Conflict Resolution Utilities (~4 cycles)

**Model:** sonnet (implementation)
**Checkpoint:** light
**Files:** `src/claudeutils/worktree/conflicts.py`, `tests/test_worktree_conflicts.py`
**Parallel:** Can run parallel to Phases 0-1 (no CLI dependencies, pure functions)

**Requirements mapping:** FR-3 (session conflict resolution), NFR-2 (deterministic resolution)

**Phase notes:**
- Four pure functions for deterministic merge conflict resolution
- No git operations, no agent judgment — testable with string inputs
- Session conflict: critical fix for FR-3 (extract worktree-created tasks before resolution)
- Learnings: keep-both append strategy (append-only file)
- Jobs: status advancement via ordering (requirements < designed < outlined < planned < complete)
- This phase forms parallel group B (independent of CLI implementation)

---
