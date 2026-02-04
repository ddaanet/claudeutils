# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| claude-tools-recovery | complete | Account/provider/model CLI wired |
| claude-tools-rewrite | planned | Paused (stubs) |
| commit-unification | designed | May be superseded by commit-rca-fixes |
| continuation-passing | requirements | Opus design needed |
| handoff-lite-issue | requirements | Issue investigation |
| handoff-validation | requirements | Requires continuation-passing |
| majestic-herding-rain | complete | Gitmoji integration |
| markdown | requirements | Markdown cleanup test corpus |
| prompt-composer | designed | Oldest plan, at risk |
| requirements-skill | requirements | New skill |
| review-requirements-consistency | complete | Requirements review |
| robust-waddling-bunny | complete | Memory index D-3 RCA |
| runbook-identifiers | complete | Cycle numbering gaps relaxed |
| statusline-wiring | planned | 28 cycles, 6 phases |
| validator-consolidation | requirements | Move to claudeutils package |

## Complete (Archived)

*18 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --oneline -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `claude-tools-recovery` — Account/provider/model CLI wiring
- `design-workflow-enhancement` — Outline-first design workflow
- `feedback-fixes` — Handoff quality, tdd-task restructure
