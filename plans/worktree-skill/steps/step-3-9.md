# Cycle 3.9

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-9-notes.md`

---

## Cycle 3.9: Idempotent merge - resume after conflict resolution

**RED — Behavioral Verification:**

Verify merge resumes safely after manual conflict resolution. Create scenario with source code conflict (non-session file), invoke merge, assert automatic resolution fails (both --ours and --theirs fail precommit in cycle 3.12), merge exits 1 with conflict list. User manually resolves conflict and stages file. Re-invoke merge command, assert merge detects staged resolution (no re-merge attempt), creates commit, runs precommit, succeeds. Test all three phases for idempotency: Phase 1 re-checks (pass if clean), Phase 2 re-checks submodule state (skip if already merged), Phase 3 detects in-progress merge and completes.

Expected: First run exits 1 with conflicts. Second run after manual staging succeeds, no duplicate operations, commit created, exit 0.

**GREEN — Behavioral Description:**

Implement idempotent merge state detection across all phases. Phase 1: clean-tree check passes if tree clean (manual staging allowed). Phase 2: submodule resolution checks current state (ancestry checks work on manually merged state). Phase 3: detect merge in progress using `git rev-parse --verify MERGE_HEAD` (exits 0 if merge active) — skip `git merge` command if MERGE_HEAD exists, proceed directly to conflict resolution checks. After conflict resolution (manual or automatic), detect if conflicts remain, commit if resolved. This allows merge to be interrupted at any point and resumed by re-running command.

Design decisions: D-8 (idempotent is architectural requirement), NFR-1 (resume after conflicts). Approach: state detection before each phase, MERGE_HEAD detection for in-progress merge, no assumptions about starting state.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-9-notes.md

---
