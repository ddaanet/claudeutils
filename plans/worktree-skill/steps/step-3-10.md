# Cycle 3.10

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-10-notes.md`

---

## Cycle 3.10: Merge debris cleanup

**RED — Behavioral Verification:**

Verify cleanup of untracked files materialized during merge. Create merge scenario with source code conflict that cannot be auto-resolved (both --ours and --theirs fail precommit). Invoke merge, assert abort executes (`git merge --abort`), verify merge materialized new untracked files from source branch (check with `git status --porcelain` for `??` entries). Assert cleanup logic identifies and removes these files via `git clean -fd -- <affected-dirs>`. Verify existing untracked files NOT removed (only merge-materialized debris). Re-invoke merge after cleanup, assert clean starting state.

Expected: Aborted merge leaves debris, cleanup removes only merge-materialized files, existing untracked files preserved, retry succeeds.

**GREEN — Behavioral Description:**

Implement merge debris cleanup after abort. Before aborting merge, capture list of untracked files: `git status --porcelain | grep '^??'`. Execute `git merge --abort`. Check for NEW untracked files (present after abort but not before). Identify affected directories from conflict file list. Clean debris: `git clean -fd -- <affected-dirs>` targeting only paths that contained conflicts. Log cleanup actions to stderr for traceability. This prevents "untracked files would be overwritten" errors on merge retry. Only invoke cleanup if merge was aborted due to unresolvable conflicts.

Design decisions: D-8 (idempotent — cleanup enables safe retry). Approach: pre-abort snapshot for diff, targeted clean by affected directories not blanket clean, defensive check to avoid removing user files.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-10-notes.md

---
