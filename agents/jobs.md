# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Complete (Archived)

*12 plans completed and deleted 2026-02-04. Git history preserves all designs/reports.*

Use `git log --all --oneline -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**One-off documents (complete):**
- `majestic-herding-rain.md` — Gitmoji integration (implemented in commit skill)
- `robust-waddling-bunny.md` — Memory index D-3 RCA (fix applied)
- `review-requirements-consistency.md` — Requirements review (one-time)

## In Progress

| Plan | Status | Current Step | Task Key |
|------|--------|--------------|----------|
| design-workflow-enhancement | planned | Steps 4-7 pending | — |
| claude-tools-recovery | planned | Re-testing phase | — |
| claude-tools-rewrite | planned | Paused (stubs) | — |

## Designed

| Plan | Notes |
|------|-------|
| commit-unification | May be superseded by commit-rca-fixes |
| feedback-fixes | Awaiting runbook |
| prompt-composer | Oldest plan, at risk |

## Requirements

| Plan | Task Key | Notes |
|------|----------|-------|
| continuation-passing | #wW6G2 | Opus design needed |
| handoff-lite-issue | — | Issue investigation |
| handoff-validation | #JZWhk | Requires continuation-passing |
| markdown | — | Markdown cleanup test corpus |
| requirements-skill | — | New skill |
| runbook-identifiers | — | Purpose unclear |
| task-prose-keys | #POn2Z | Replace hash tokens |
| validator-consolidation | #pEmoW | Move to claudeutils package |

