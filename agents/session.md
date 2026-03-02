# Session: Worktree — Worktree merge from main

**Status:** Focused worktree for parallel execution.

## In-tree Tasks

- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/requirements.md` | sonnet | 2.2
  - Plan: worktree-merge-from-main | Status: requirements
  - Branch self-updates before merge to main; main rollbacks on failure instead of fixing on main
  - Prerequisite for merge resilience — eliminates most merge failures at source
