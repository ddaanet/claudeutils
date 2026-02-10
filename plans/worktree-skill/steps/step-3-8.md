# Cycle 3.8

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-6-notes.md`

---

## Cycle 3.8: Phase 3 post-merge precommit gate

**RED — Behavioral Verification:**

Verify mandatory precommit validation after merge commit. Create worktree merge that produces merge commit passing unit tests but failing precommit check (e.g., line length violation in merged file). Assert merge creates commit successfully, then runs `just precommit`, detects failure, reports to stderr which checks failed, exits 1. Verify merge commit is NOT rolled back (remains in history). Test user fix flow: amend commit, re-run merge (idempotent — already merged, skips to verification).

Expected: Precommit runs after commit, failures reported, exit 1, commit persists (no rollback), re-run succeeds after fix.

**GREEN — Behavioral Description:**

Implement post-merge precommit gate as mandatory correctness check. After merge commit created, run `just precommit` (shell out to just recipe). Capture exit code and output. If exit 0, output merge commit SHA to stdout and exit 0 (success). If non-zero, report failure to stderr: "Precommit checks failed:" followed by just output, exit 1. Do NOT roll back merge commit — user fixes issues and amends commit or re-runs merge (idempotent flow handles already-merged state). This validates take-ours conflict resolution strategy mechanically.

Design decisions: D-4 (precommit as oracle), NFR-4 (mandatory gate), D-8 (idempotent — no rollback, safe to re-run). Approach: precommit is external validation, not merge logic, failure is expected path requiring user intervention.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-6-notes.md

---
