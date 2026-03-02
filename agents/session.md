# Session: Worktree — Handoff --commit removal

**Status:** Focused worktree for parallel execution.

## In-tree Tasks

- [ ] **Handoff --commit removal** — remove --commit from /handoff, expand standalone to chain, deduplicate [handoff, commit] | sonnet | 2.2
  - ~60 occurrences: skills, fragments, tests, continuation infrastructure, decision files
  - Motivation: decouple handoff from commit-ready state (handoff should work on dirty tree)
