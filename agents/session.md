# Session: Worktree — Hook batch

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Hook batch** — `/runbook plans/hook-batch/outline.md` | sonnet | restart
  - Absorbs: PostToolUse auto-format hook, SessionStart status hook
  - 5 phases: UserPromptSubmit (9 changes), PreToolUse recipe-redirect, PostToolUse auto-format, Session health (SessionStart + Stop fallback), Hook infrastructure (hooks.json + sync-to-parent merge)
  - Plan: hook-batch | Status: designed (outline complete)

## Blockers / Gotchas

- Platform limitation — skill matching is pure LLM reasoning with no algorithmic routing. UserPromptSubmit hook with targeted patterns is the structural fix (hook batch Phase 1 items 8-9).
**SessionStart hook #10373 still open:**
- Output discarded for new interactive sessions. Stop hook fallback designed in hook batch Phase 4.

## Reference Files

- `plans/hook-batch/outline.md` — Hook batch outline (5 phases, 9 files, 8 decisions)
- `plans/hook-batch/brief.md` — Original brief (pre-design)
