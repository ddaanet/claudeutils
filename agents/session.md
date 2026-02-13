# Session: Worktree — Worktree fixes

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree fixes** — `/design plans/worktree-fixes/` | opus
  - Plan: worktree-fixes | Status: requirements
  - 5 FRs: task name constraints, precommit validation, migration, session merge blocks, merge commit fix

## Blockers / Gotchas

- Session merge loses continuation lines (single-line set diff) → worktree-fixes FR-4
- No-op merge skips commit → orphan branch → worktree-fixes FR-5
**All tasks with documentation must have in-tree file references.**

## Reference Files

- `plans/worktree-fixes/requirements.md` — Worktree fixes requirements (5 FRs, task naming + merge fixes)
