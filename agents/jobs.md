# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| continuation-prepend | requirements | Problem statement only |
| feature-requests | requirements | GH issue research (sandbox, tool overrides) |
| orchestrate-evolution | designed | Design.md complete, vet in progress, planning next |
| parallel-orchestration | requirements | Deferred from orchestrate-evolution (worktree isolation needed) |
| plugin-migration | planned | Runbook assembled: 15 steps, haiku execution ready |
| reports | — | Shared reports directory (not a plan) |
| tweakcc | requirements | Local instances research |
| when-recall | complete | `/when` memory recall system — 42/42 TDD cycles, 8 phases, all checkpoints passed |
| workflow-rca-fixes | designed | 18 FRs: RCA prose fixes + agent composition + pipeline integration |
| worktree-fixes | requirements | Task name constraints, session merge blocks, merge commit fix (5 FRs) |
| workwoods | requirements | Cross-tree worktree awareness, vet tracking, plan state inference, bidirectional merge |
| pushback | requirements | Prevent yes-manning in design discussions |
| process-review | complete | RCA recovered to disk for workflow-improvements reference |
| workflow-fixes | complete | Unified /runbook skill, plan-reviewer agent, review-plan skill, pipeline-contracts |
| worktree-skill | complete | Design.md retained on disk for reference |
| worktree-update | complete | 40 TDD cycles, recovery (C2-C5), merged to main |

## Complete (Archived)

*41 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --online -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `memory-index-recall` — Bug fixes + reanalysis (M-1, M-2 fixed, 0.2% recall confirmed)
- `process-review` — RCA: 5 plans examined, root cause in planning skill, 5 recommendations
- `workflow-skills-audit` — Superseded by runbook unification (all 12 items landed)
- `reflect-rca-sequential-task-launch` — Subsumed into process-review worktree
- `requirements-skill` — Dual-mode extract/elicit requirements skill, empirical grounding
- `worktree-skill` — Worktree skill implementation (42/42 cycles, merged to dev)
- `worktree-skill-fixes` — Worktree skill findings (27 fixes across 7 phases, merged to dev)
- `handoff-validation` — Killed: problems resolved by existing tooling
- `continuation-passing` — Continuation passing protocol (15 steps, hook implementation, skill updates, 0% FP rate)
- `markdown` — Test corpus implementation (16 fixtures, 3 parametrized tests, all 5 FRs satisfied)
- `memory-index-recall` — Memory index recall analysis tool (7 modules, 50 tests)
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
