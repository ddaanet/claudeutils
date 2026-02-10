# Cycle 3.5

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-4-notes.md`

---

## Cycle 3.5: Phase 2 post-verification

**RED — Behavioral Verification:**

Verify merge correctness via ancestry verification. After diverged submodule merge (cycle 3.4), extract both original commit SHAs (worktree pointer and pre-merge local HEAD), assert both are ancestors of final submodule HEAD using `git merge-base --is-ancestor`. Create negative test case with corrupted merge (manually reset submodule to wrong commit before verification), assert post-verification catches error.

Expected: Both original commits pass ancestry check after successful merge. Corrupted merge fails verification with descriptive error.

**GREEN — Behavioral Description:**

Implement post-merge verification for submodule merge correctness. After merge commit (or skip), extract final submodule HEAD: `git -C agent-core rev-parse HEAD`. Verify both original commits are ancestors: `git -C agent-core merge-base --is-ancestor <wt-commit> HEAD` and same for `<local-commit>`. If either check fails, exit 2 with error message listing commits and ancestry failure. This catches merge corruption or logic errors.

Design decisions: D-8 (idempotent — verification enables safe re-run), FR-2 (submodule resolution correctness). Approach: defensive verification, fail-fast on unexpected state.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-4-notes.md

---
