# Cycle 3.1

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/worktree-skill/reports/cycle-3-1-notes.md`

---

## Cycle 3.1: Phase 1 pre-checks (clean tree gate)

**RED — Behavioral Verification:**

Verify merge enforcement of clean working tree. Create test scenario with dirty repository state (modified source file `src/claudeutils/__init__.py`), invoke `_worktree merge <slug>`, assert exit code 1 and error message to stderr indicating dirty tree prevents merge. Verify session context files (agents/session.md) do NOT trigger dirty tree rejection (exempt from gate).

Expected: Exit 1, stderr contains "dirty" or "uncommitted changes", merge does NOT proceed.

**GREEN — Behavioral Description:**

Implement `merge` subcommand entry point and Phase 1 pre-check logic. Reuse clean-tree validation logic from clean-tree subcommand (filter session context files, check parent + submodule status). Add branch validation (`git rev-parse --verify <slug>`), worktree directory check (warn if `wt/<slug>/` missing but continue — branch-only merge valid). Exit 1 with descriptive error if dirty tree detected. Return early from merge if pre-checks fail.

Design decisions: D-4 (precommit oracle), NFR-4 (mandatory precommit). Approach: extract shared validation logic into helper function, invoke from both clean-tree subcommand and merge Phase 1.

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-3-1-notes.md

---
