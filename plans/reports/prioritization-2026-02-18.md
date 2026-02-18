# Task Prioritization — 2026-02-18

Post-merge (design-workwoods) re-prioritization. 42 tasks scored, 2 worktree tasks excluded from ranking (active work).

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Orchestrate evolution | 5 | 5 | 5 | 15 | 2 | 2 | 4 | 3.8 | sonnet, **BLOCKED** (runbook evolution) |
| 2 | Worktree merge resilience | 3 | 5 | 5 | 13 | 3 | 2 | 5 | 2.6 | opus |
| 3 | Quality infrastructure reform | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | opus |
| 4 | Design runbook evolution | 5 | 5 | 5 | 15 | 3 | 3 | 6 | 2.5 | opus, restart |
| 5 | Execute plugin migration | 2 | 8 | 3 | 13 | 3 | 3 | 6 | 2.2 | opus |
| 6 | Remember skill update | 3 | 5 | 5 | 13 | 3 | 3 | 6 | 2.2 | opus |
| 7 | Script commit vet gate | 8 | 2 | 5 | 15 | 5 | 2 | 7 | 2.1 | sonnet |
| 8 | Commit CLI tool | 8 | 3 | 3 | 14 | 5 | 2 | 7 | 2.0 | sonnet |
| 9 | Vet delegation routing | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 10 | Memory-index auto-sync | 3 | 3 | 5 | 11 | 5 | 1 | 6 | 1.8 | sonnet |
| 11 | Test diagnostic helper | 3 | 2 | 5 | 10 | 5 | 1 | 6 | 1.7 | sonnet |
| 12 | Pre-merge untracked file fix | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 13 | Runbook model assignment | 5 | 3 | 3 | 11 | 5 | 2 | 7 | 1.6 | sonnet (partial WT overlap) |
| 14 | RED pass protocol | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | sonnet, **BLOCKED** |
| 15 | Handoff insertion policy | 5 | 2 | 3 | 10 | 5 | 2 | 7 | 1.4 | sonnet |
| 16 | Agent rule injection | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | sonnet |
| 17 | Fix worktree rm dirty check | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 18 | Handoff wt awareness | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 19 | Codebase quality sweep | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 20 | Explore Anthropic plugins | 1 | 3 | 3 | 7 | 5 | 1 | 6 | 1.2 | sonnet, restart |
| 21 | Model tier awareness hook | 3 | 1 | 3 | 7 | 5 | 1 | 6 | 1.2 | sonnet, restart |
| 22 | Runbook quality gates Phase B | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet, **BLOCKED** (Phase A in WT) |
| 23 | Continuation prepend | 2 | 2 | 1 | 5 | 3 | 2 | 5 | 1.0 | sonnet |
| 24 | Diagnostic opus review | 3 | 2 | 5 | 10 | 5 | 5 | 10 | 1.0 | opus |
| 25 | Feature prototypes | 2 | 2 | 1 | 5 | 3 | 2 | 5 | 1.0 | sonnet |
| 26 | Cross-tree requirements transport | 2 | 2 | 3 | 7 | 5 | 2 | 7 | 1.0 | sonnet |
| 27 | Migrate test suite to diamond | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | **BLOCKED** (runbook evolution) |
| 28 | Remember agent routing | 2 | 2 | 3 | 7 | 5 | 2 | 7 | 1.0 | sonnet, **BLOCKED** |
| 29 | Worktree skill adhoc mode | 2 | 2 | 1 | 5 | 5 | 1 | 6 | 0.8 | sonnet |
| 30 | Debug failed merge | 1 | 2 | 3 | 6 | 5 | 3 | 8 | 0.8 | sonnet |
| 31 | Safety review expansion | 1 | 2 | 3 | 6 | 5 | 3 | 8 | 0.8 | opus, **BLOCKED** |
| 32 | Learning ages consol | 1 | 1 | 3 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 33 | Simplify when-resolve CLI | 2 | 1 | 1 | 4 | 5 | 1 | 6 | 0.7 | sonnet |
| 34 | Rename remember skill | 1 | 2 | 1 | 4 | 5 | 1 | 6 | 0.7 | sonnet, restart |
| 35 | Revert cross-tree sandbox access | 1 | 2 | 1 | 4 | 5 | 1 | 6 | 0.7 | sonnet |
| 36 | Infrastructure scripts | 2 | 1 | 1 | 4 | 5 | 2 | 7 | 0.6 | sonnet |
| 37 | Behavioral design | 2 | 2 | 3 | 7 | 8 | 5 | 13 | 0.5 | opus |
| 38 | Ground state-machine review criteria | 2 | 1 | 3 | 6 | 8 | 3 | 11 | 0.5 | opus |
| 39 | Design-to-deliverable | 2 | 1 | 3 | 6 | 8 | 3 | 11 | 0.5 | opus, restart |
| 40 | Upstream skills field | 1 | 1 | 1 | 3 | 5 | 1 | 6 | 0.5 | sonnet |
| 41 | Workflow formal analysis | 1 | 1 | 3 | 5 | 8 | 5 | 13 | 0.4 | opus |

## Blocked Tasks

| Task | Blocked By | Unblocked Priority |
|------|-----------|-------------------|
| Orchestrate evolution | Design runbook evolution | 3.8 |
| RED pass protocol | Error handling design (WT) | 1.6 |
| Runbook quality gates Phase B | Runbook skill fixes Phase A (WT) | 2.2 |
| Remember agent routing | Memory redesign | 1.0 |
| Safety review expansion | Explore Anthropic plugins | 0.8 |
| Migrate test suite to diamond | Design runbook evolution | 1.0 |

## Worktree Tasks (Active, Not Ranked)

- **Error handling design** → `error-handling-design` — Resume Phase B (outline review) then Phase C
- **Runbook skill fixes** → `runbook-skill-fixes` — Model assignment + design quality gates

## Parallel Batches

**Batch A — Opus design sessions (no restart, independent plans):**
- Worktree merge resilience (2.6) — `plans/worktree-merge-resilience/`
- Quality infrastructure reform (2.6) — `plans/quality-infrastructure/`
- Remember skill update (2.2) — `plans/remember-skill-update/`

**Batch B — Sonnet inner-loop improvements (no restart, independent targets):**
- Script commit vet gate (2.1) — commit skill, vet-requirement.md
- Memory-index auto-sync (1.8) — memory-index.md, SKILL.md
- Test diagnostic helper (1.7) — test utilities
- Pre-merge untracked file fix (1.6) — `new --session` codepath

**Batch C — Sonnet workflow improvements (no restart):**
- Vet delegation routing (1.9) — pipeline-contracts, vet-requirement
- Handoff insertion policy (1.4) — handoff skill
- Handoff wt awareness (1.3) — handoff skill

Note: Batch C items 2-3 share the handoff skill — execute sequentially within batch.

**Batch D — Sonnet small fixes (no restart):**
- Fix worktree rm dirty check (1.3) — worktree CLI
- Codebase quality sweep (1.3) — scattered targets
- Worktree skill adhoc mode (0.8) — worktree skill

## Top 5 Recommendations

1. **Design runbook evolution** (2.5) — Critical path. Blocks orchestrate evolution (3.8) and migrate test suite (1.0). Outline exists at Phase A.6, resume from outline review. 5 FRs for fundamental runbook quality. Requires restart + opus.

2. **Worktree merge resilience** (2.6) — Highest actionable score. Merge difficulties are active pain (observed this session). Requirements exist. 5 FRs address root causes of merge data loss.

3. **Quality infrastructure reform** (2.6) — Tied with #2. Subsumes vet rename and quality sweep. Requirements exist. Prefer merge resilience first (higher DP, more recent pain).

4. **Execute plugin migration** (2.2) — Highest DP (8) of any task — drift accelerating since Feb 9. Ready plan but Phase 4 needs rewrite. Recovery work front-loaded.

5. **Script commit vet gate** (2.1) — Highest-frequency workflow friction (every commit). Replaces ambient prose Gate B with mechanical enforcement. Actionable at sonnet tier while opus handles #1-4.

## Scoring Assumptions

- **Plugin migration ME=3** (not 1 despite "ready" status): Plan flagged stale Feb 9 with significant drift. Phase 4 needs rewrite, expanded phases need regeneration. Recovery effort comparable to requirements-stage.
- **Orchestrate evolution BLOCKED**: Can't run `/runbook` to generate its execution plan until runbook skill is fixed (design runbook evolution). Score 3.8 is the unblocked priority — actual execution depends on runbook evolution completing first.
- **Orchestrate evolution DP=5**: Design refreshed Feb 13 but orchestrate skill is the core execution path — every orchestration run exercises it. No recent commits to skill directory, but that increases staleness risk if design references shift.
- **CRR scoring**: Used max(defect, downstream, reliability) per methodology. Multiple learnings about merge data loss, vet skipping, and orchestration failures drove CRR=5 for several tasks.
- **Worktree tasks excluded**: Error handling design and runbook skill fixes are active worktree work. Their priority is moot — they execute when the worktree session runs.
- **Runbook model assignment**: Partially overlaps with runbook-skill-fixes worktree task. Ranked here for the non-worktree remainder.
