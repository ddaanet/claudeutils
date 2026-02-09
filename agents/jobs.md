# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| continuation-passing | requirements | Opus design needed |
| continuation-prepend | requirements | Problem statement only |
| feature-requests | requirements | GH issue research (sandbox, tool overrides) |
| domain-validation | complete | Domain-specific validation infrastructure |
| handoff-validation | requirements | Requires continuation-passing |
| markdown | requirements | Markdown cleanup test corpus |
| memory-index-recall | complete | Memory index recall analysis tool (7 modules, 50 tests) |
| orchestrate-evolution | requirements | Absorb planning, finalize phase pattern |
| plugin-migration | planned | All 7 phases vetted (44 issues fixed). Ready for runbook assembly |
| reflect-rca-parity-iterations | complete | Parity test quality gap fixes (11 steps, 8 design decisions) |
| reflect-rca-sequential-task-launch | requirements | RCA on Task parallelization + vet context issues |
| requirements-skill | requirements | Evaluate with opus |
| tweakcc | requirements | Local instances research |
| validator-consolidation | complete | Validators consolidated to claudeutils package |
| when-recall | requirements | `/when` memory recall system — active retrieval replacing passive index |
| workflow-skills-audit | designed | plan-adhoc alignment + design skill audit, 12 items |
| wt-merge-skill | requirements | Blocked on continuation-passing |

## Complete (Archived)

*35 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --online -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `reflect-rca-parity-iterations` — Parity test quality gap fixes (11 steps, 8 design decisions)
- `domain-validation` — Domain-specific validation infrastructure (validation skill, rules file, plan skill updates)
- `validator-consolidation` — Validators consolidated to claudeutils package
- `commit-unification` — Unified commit skills, inlined gitmoji, decoupled handoff
- `position-bias` — Fragment reordering by position bias + token budget script
- `prompt-composer` — Superseded by fragment system; research distilled
- `reflect-rca-prose-gates` — D+B hybrid fix implemented
- `statusline-wiring` — Statusline CLI with TDD (28 cycles, 6 phases)
- `statusline-parity` — All 14 cycles, 5 phases executed and validated
- `learnings-consolidation` — Learnings consolidation infrastructure (7 steps, 4 phases)
- `workflow-feedback-loops` — Feedback loop infrastructure (12 steps, 4 phases)
- `claude-tools-rewrite` — Infrastructure complete, recovery and parity followups
- `claude-tools-recovery` — Account/provider/model CLI wired
- `runbook-identifiers` — Cycle numbering gaps relaxed
- `robust-waddling-bunny` — Memory index D-3 RCA
- `review-requirements-consistency` — Requirements review
- `majestic-herding-rain` — Gitmoji integration
- `handoff-lite-issue` — RCA transcript for handoff-lite misuse
