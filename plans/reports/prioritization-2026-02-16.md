# Task Prioritization — 2026-02-16

**Formula:** `Priority = Cost_of_Delay / Job_Size`
**Scope:** 26 pending tasks from session.md (excludes Worktree merge data loss — in worktree)

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Precommit improvements | 8 | 2 | 5 | 15 | 5 | 1 | 6 | 2.5 | sonnet |
| 2 | Vet proportionality | 8 | 2 | 5 | 15 | 5 | 1 | 6 | 2.5 | sonnet |
| 3 | Remaining workflow items | 5 | 5 | 5 | 15 | 3 | 3 | 6 | 2.5 | sonnet |
| 4 | Error handling design | 5 | 5 | 5 | 15 | 3 | 3 | 6 | 2.5 | opus |
| 5 | Design workwoods | 3 | 5 | 5 | 13 | 3 | 3 | 6 | 2.2 | opus |
| 6 | Execute plugin migration | 2 | 8 | 3 | 13 | 3 | 3 | 6 | 2.2 | sonnet |
| 7 | Commit CLI tool | 8 | 3 | 3 | 14 | 5 | 2 | 7 | 2.0 | sonnet |
| 8 | Vet delegation routing | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 9 | Model tier awareness hook | 5 | 1 | 5 | 11 | 5 | 1 | 6 | 1.8 | sonnet, restart |
| 10 | Remember skill update | 3 | 3 | 3 | 9 | 3 | 2 | 5 | 1.8 | sonnet |
| 11 | Continuation prepend | 3 | 3 | 3 | 9 | 3 | 2 | 5 | 1.8 | sonnet |
| 12 | RED pass protocol | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | sonnet |
| 13 | Memory-index auto-sync | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 14 | Agent rule injection | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | sonnet |
| 15 | Diagnostic opus review | 3 | 3 | 5 | 11 | 3 | 5 | 8 | 1.4 | opus |
| 16 | Pretool hook cd pattern | 3 | 1 | 5 | 9 | 5 | 2 | 7 | 1.3 | sonnet, restart |
| 17 | Handoff wt awareness | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 18 | Learning ages consol | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 19 | Codebase quality sweep | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 20 | Remember agent routing | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet, blocked |
| 21 | Infrastructure scripts | 2 | 1 | 1 | 4 | 5 | 2 | 7 | 0.6 | sonnet |
| 22 | Behavioral design | 3 | 2 | 3 | 8 | 8 | 5 | 13 | 0.6 | opus |
| 23 | Upstream skills field | 1 | 1 | 1 | 3 | 5 | 1 | 6 | 0.5 | sonnet |
| 24 | Feature prototypes | 1 | 2 | 1 | 4 | 5 | 3 | 8 | 0.5 | sonnet |
| 25 | Rename remember skill | 1 | 1 | 1 | 3 | 5 | 2 | 7 | 0.4 | sonnet, restart |
| 26 | Workflow formal analysis | 1 | 1 | 3 | 5 | 8 | 5 | 13 | 0.4 | opus |

## Parallel Batches

**Batch A (sonnet, no restart) — 4 tasks, independent targets:**
- Precommit improvements (2.5) — validators, precommit scripts
- Vet proportionality (2.5) — vet-requirement.md fragment
- Commit CLI tool (2.0) — CLI commands, commit workflow
- Memory-index auto-sync (1.6) — memory consolidation hooks

**Batch B (opus) — 3 tasks, independent:**
- Error handling design (2.5) — error handling outline/design
- Design workwoods (2.2) — workwoods requirements/design
- Diagnostic opus review (1.4) — RCA methodology requirements

**Batch C (sonnet, no restart) — 3 tasks, workflow improvements:**
- Vet delegation routing (1.9) — vet routing rules
- Agent rule injection (1.6) — agent templates
- RED pass protocol (1.6) — orchestrate skill

## Top 5 Recommendations

- **Precommit improvements** — WF=8 (every commit). tmp/ reference validation prevents a recurring RCA finding. No design needed, clear scope.
- **Vet proportionality** — WF=8 (every vet). 1-line edits triggering full vet-fix-agent delegation is measurable waste. Threshold rule in vet-requirement.md + Gate B review.
- **Remaining workflow items** — Contains orchestrate-evolution (designed, ready for `/runbook`). Highest compound value: 6 sub-items touching orchestration, commit, and agent output.
- **Error handling design** — Outline complete, Phase B ready. DP=5 reflects codebase evolution around error paths. Opus session for Phase C design generation.
- **Plugin migration** — DP=8 (stale since Feb 9, significant drift in skill/agent counts and justfile). Drift increases with every session. Outline refresh + orchestrate.

## Scoring Assumptions

- **Remaining workflow items** scored as aggregate — orchestrate-evolution (designed) drives ME=3; sub-items vary but batch amortizes context setup
- **Plugin migration** ME=3 despite `planned` status in jobs.md because session notes flag staleness requiring outline refresh
- **Remember agent routing** marked blocked per session.md (blocked on memory redesign)
- **Remember skill update** CRC=2 despite 3 reports because requirements.md and outline.md are the primary recovery files
- **Model tier awareness hook** CRR=5 based on `/when no model tier introspection available` memory-index entry (observed failure pattern)
- All tasks without explicit model annotation default to sonnet per session.md conventions
