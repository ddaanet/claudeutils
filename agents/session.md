# Session: Worktree — Commit CLI tool

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Absorbs: Script commit vet gate (Gate B → scripted check)
  - Single command: precommit → gate → stage → commit in main + agent-core submodule
