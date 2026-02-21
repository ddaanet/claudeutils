# Session: Worktree — Tokens user config

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Tokens user config** — User config (`~/.config/claudeutils/`) for ANTHROPIC_API_KEY so `tokens` command works without env var | sonnet
  - Problem: setting ANTHROPIC_API_KEY in .envrc interferes with `claude` CLI auth
  - API token counting is free — only need key routing, not a local tokenizer
