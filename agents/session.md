# Session: Worktree — Worktree merge resilience

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree merge resilience** — `/design plans/worktree-merge-resilience/requirements.md` | opus
  - Plan: worktree-merge-resilience | Status: requirements
  - 5 FRs: submodule conflict pass-through, leave merge in progress, untracked file handling, conflict context output, idempotent resume
  - Addresses root cause of merge difficulties observed this session

## Blockers / Gotchas

- Requirements for remaining FRs: `plans/worktree-merge-resilience/requirements.md`
**Never run `git merge` without sandbox bypass:**

## Reference Files

- `plans/worktree-merge-resilience/requirements.md` — 5 FRs for merge conflict handling
