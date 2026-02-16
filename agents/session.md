# Session: Worktree — Worktree merge errors

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Worktree merge errors** — Catch exceptions in merge CLI, report errors without stack traces; surface failed command output | sonnet
  - Stack traces on merge errors are user-hostile; report cause and recovery steps instead
  - `_git()` CalledProcessError swallows stderr — surface the actual git error message (thought this was already done in merge-data-loss work)
  - Reproduce: `git add agents/session.md` returned exit 128 during `_resolve_session_md_conflict` in `_phase3_merge_parent`. Merge of `remaining-workflow-items` worktree, 2026-02-16. Branch had 1 post-merge commit (683fc7d). Conflict on both `agent-core` (submodule) and `agents/session.md`. Main at 9bb45d0, merge result at 5e024c2.
