# Cycle 3.2

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-2-notes.md`

---

## Cycle 3.2: Phase 2 submodule resolution - no divergence

**RED — Behavioral Verification:**

Verify merge optimization when submodule pointers match. Create worktree with submodule at same commit as parent (no divergence), invoke merge, assert submodule merge phase skipped (no fetch, no merge commands executed). Trace execution to confirm skip path taken. Verify merge proceeds to Phase 3 (parent merge).

Expected: Merge succeeds, no submodule operations in trace, submodule pointer unchanged after merge.

**GREEN — Behavioral Description:**

Implement Phase 2 submodule resolution with no-divergence optimization. Extract worktree submodule commit pointer using `git ls-tree <slug> -- agent-core` (parse 160000 mode line, extract SHA). Extract local submodule commit using `git -C agent-core rev-parse HEAD`. Compare commits — if equal, skip to Phase 3. Log skip reason to stderr for traceability.

Design decisions: D-7 (submodule before parent), D-8 (idempotent). Approach: early return pattern for optimization, git plumbing for pointer extraction.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-2-notes.md

---
