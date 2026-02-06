# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| claude-tools-recovery | complete | Account/provider/model CLI wired |
| claude-tools-rewrite | complete | Infrastructure complete, recovery and parity are followups |
| workflow-feedback-loops | complete | Feedback loop infrastructure (12 steps, 4 phases) |
| commit-unification | designed | May be superseded by commit-rca-fixes |
| continuation-passing | requirements | Opus design needed |
| handoff-lite-issue | requirements | Issue investigation |
| handoff-validation | requirements | Requires continuation-passing |
| learnings-consolidation | complete | Learnings consolidation infrastructure (7 steps, 4 phases) |
| majestic-herding-rain | complete | Gitmoji integration |
| markdown | requirements | Markdown cleanup test corpus |
| prompt-composer | designed | Oldest plan, at risk |
| requirements-skill | requirements | New skill |
| review-requirements-consistency | complete | Requirements review |
| robust-waddling-bunny | complete | Memory index D-3 RCA |
| runbook-identifiers | complete | Cycle numbering gaps relaxed |
| statusline-parity | complete | All 14 cycles, 5 phases executed and validated |
| statusline-wiring | complete | 28 cycles executed, functionally conformant |
| reflect-rca-prose-gates | requirements | Structural fix for skill gate skipping |
| validator-consolidation | requirements | Move to claudeutils package |

## Complete (Archived)

*18 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --oneline -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `workflow-feedback-loops` — Feedback loop infrastructure (12 steps, 4 phases)
- `statusline-wiring` — Statusline CLI with TDD (28 cycles, 6 phases)
- `claude-tools-recovery` — Account/provider/model CLI wiring
