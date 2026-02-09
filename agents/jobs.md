# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| continuation-passing | requirements | Opus design needed |
| feature-requests | complete | Claude Code feature requests + fragment redundancy analysis |
| handoff-validation | requirements | Requires continuation-passing |
| markdown | requirements | Markdown cleanup test corpus |
| requirements-skill | requirements | Evaluate with opus |
| reflect-rca-parity-iterations | requirements | Spec-to-execution fidelity, 5 root causes |
| tweakcc | requirements | Drive tweakcc from claudeutils, custom system + tool prompts |
| workflow-skills-audit | designed | plan-adhoc alignment + design skill audit, 12 items |
| validator-consolidation | complete | Validators consolidated to claudeutils package |

## Complete (Archived)

*35 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --online -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
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
