# Session: Worktree — Wt rm amend safety

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Wt rm amend safety** — `/design` | sonnet
  - `_worktree rm` amends HEAD without verifying it's the merge commit for that worktree
  - `--force` path (never merged) should never amend
  - Absorbed by worktree-cli-default if that runs first
