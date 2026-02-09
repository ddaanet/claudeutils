# Session Handoff: 2026-02-09

**Status:** Merged tools-rewrite branch, RCA on lock file deletion behavior.

## Completed This Session

**Branch merge:**
- Merged `tools-rewrite` (99 commits) into `wt/memory-index-recall` (0079920)
- Agent-core submodule updated to origin/main in same merge commit
- Resolved 3 conflicts: jobs.md (examined plan files), learnings.md (kept both), session.md (kept ours)
- Failed merge left ~140 untracked files as debris — first attempt hit index.lock error, git materialized files then aborted without cleanup. Cleaned with `git clean -fd` on affected directories

**RCA — lock file deletion:**
- Agent attempted `rm .git/worktrees/.../index.lock` instead of stopping per "Stop on unexpected results"
- Root cause: 3 project directives encourage over-generalization of lock removal beyond commit context
- System prompts checked (`/Users/david/code/claude-code-system-prompts`) — no conflict found, issue entirely project-level
- User feedback captured in pending task: lock removal never agent-initiated, wait+retry universal for all git commands

## Pending Tasks

- [ ] **Continue `/when` design** — Phase B (user validates outline) → Phase C (full design.md) | `/design plans/when-recall/outline.md`
- [ ] **Fix lock file directive scope** — RCA: agent deleted git index.lock instead of stopping; three project directives encourage over-generalization of lock removal | sonnet
  - **Lock removal is never agent-initiated** — always defer to user
  - `rules-commit.md:175` + `commit.semantic.md:75`: broaden scope from commit-only to all git commands; add "do not remove lockfile" — wait 2s and retry is the universal pattern
  - `learnings.md:110`: replace "remove stale lock" example with non-lockfile example
  - RCA context: system prompts checked — no conflict found, issue is entirely project-level directives

## Blockers / Gotchas

- `/design` skill has no resume logic — invoke manually from Phase B when continuing, don't re-invoke `/design` (would restart from Phase A)
- Learnings file at 212/80 lines (soft limit exceeded, 0 entries ≥7 days — consolidation blocked by age gate)

## Reference Files

- `plans/when-recall/outline.md` — Design outline (updated, ready for Phase B)
- `plans/when-recall/reports/corpus-analysis.md` — Corpus analysis
- `plans/when-recall/reports/fzf-research.md` — fzf algorithm research
- `plans/memory-index-recall/reports/final-summary.md` — Recall analysis (0% baseline)

## Next Steps

Fix lock file directive scope (sonnet, quick edit task), then continue `/when` design Phase B.

---
*Handoff by Opus. tools-rewrite merged, lock file RCA complete.*
