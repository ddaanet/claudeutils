# Cycle 3.4

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-5-notes.md`

---

## Cycle 3.4: Phase 2 submodule resolution - diverged commits

**RED — Behavioral Verification:**

Verify merge with diverged submodule commits. Create worktree, make distinct submodule commit in worktree (file A), make different commit in parent submodule (file B), invoke merge, assert submodule merge executes (fetch from worktree path, merge via `--no-edit`, stage, commit). Verify both files A and B present in final submodule state. Verify merge commit message follows pattern `🔀 Merge agent-core from <slug>`.

Expected: Submodule merge commit created, both diverged changes integrated, commit message matches pattern, submodule staged in parent index.

**GREEN — Behavioral Description:**

Implement diverged submodule merge flow. Fetch worktree submodule commits into local object store: `git -C agent-core fetch <project-root>/wt/<slug>/agent-core HEAD` (uses absolute path to worktree submodule directory). Merge fetched commit: `git -C agent-core merge --no-edit <wt-commit>` (no-edit prevents editor prompt). Stage submodule pointer: `git add agent-core`. Create merge commit if staged: `git diff --quiet --cached || git commit -m "🔀 Merge agent-core from <slug>"` (idempotent — no-op if already committed).

Design decisions: D-7 (submodule before parent), D-10 (idempotent commit), NFR-3 (direct git plumbing). Approach: fetch from worktree path not remote (worktree-only commits), hardcoded gitmoji for submodule merges.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-5-notes.md

---
