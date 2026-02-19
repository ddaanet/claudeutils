# Session: Worktree — Handoff CLI tool

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Handoff CLI tool** — Mechanical handoff+commit pipeline in CLI | `/design` | sonnet
  - Same pattern as worktree CLI: mechanical ops in CLI, judgment stays in agent
  - Inputs: status line, completed text, optional files, optional commit message with gitmoji
  - Outputs (conditional): learnings age status, precommit result, git status+diff, worktree ls
  - Cache on failure: inputs to state file, rerun without re-entering skill
  - Gitmoji: embeddings + cosine similarity over 78 pre-computed vectors
