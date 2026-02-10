# Cycle 3.3

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-3-notes.md`

---

## Cycle 3.3: Phase 2 submodule resolution - fast-forward

**RED — Behavioral Verification:**

Verify merge optimization when local submodule includes worktree changes (ancestry check passes). Create worktree, make submodule commits in worktree, merge those commits to parent submodule manually (local ahead of worktree), invoke merge, assert submodule merge skipped via ancestry check. Verify `git merge-base --is-ancestor <wt-commit> <local-commit>` detected inclusion.

Expected: Merge succeeds, ancestry check passes, no fetch or merge executed, submodule pointer unchanged.

**GREEN — Behavioral Description:**

Extend Phase 2 with ancestry check optimization. After extracting both commits, run `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`. If exit 0 (ancestor check passes), local already includes worktree changes — skip merge. Log skip reason with commit SHAs. Handle command failure (commit not found) as divergence indicator — proceed to fetch+merge path.

Design decisions: D-8 (idempotent — safe to re-run). Approach: ancestry check as second optimization gate after equality check.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-3-notes.md

---
