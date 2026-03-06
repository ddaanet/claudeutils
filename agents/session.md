# Session: Worktree — Update prioritize skill

**Status:** Focused worktree for parallel execution.

## In-tree Tasks

- [ ] **Update prioritize skill** — use `claudeutils _worktree ls` instead of `list_plans()` ad-hoc Python; use prototype script for scoring arithmetic | sonnet | 1.0
  - Phase 1: optimize skill to use `plans/prototypes/score.py` for computation
  - Phase 2: integrate as `claudeutils _prioritize score` CLI command (replace prototype)
  - JSON input for scores (agent-produced, unambiguous parsing), markdown output for reports
