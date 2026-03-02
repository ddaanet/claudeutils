# Prioritization Report — 2026-03-02

**Methodology:** WSJF-adapted (CoD/Size). Fibonacci scale (1-8). User directive: recall/when-resolve first → workflow prose → workflow non-prose → rest. Supersedes 2026-02-28 report.

**Delta from 2026-02-28:** 8 tasks removed (6 delivered, 1 absorbed, 1 canceled), 10 new tasks added. Arithmetic via `tmp/score.py`.

**Column key:** WF=Workflow Friction, DP=Decay Pressure, CRR=Compound Risk Reduction, ME=Marginal Effort, CRC=Context Recovery Cost. Tasks marked `*` are new.

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Orchestrate evolution | 5 | 5 | 8 | 18 | 1 | 2 | 3 | 6.0 | sonnet, restart |
| 2 | Merge completed filter * | 3 | 2 | 3 | 8 | 1 | 1 | 2 | 4.0 | sonnet, inline |
| 3 | Execute flag lint | 5 | 2 | 5 | 12 | 3 | 1 | 4 | 3.0 | haiku |
| 4 | Skill disclosure | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | opus |
| 5 | Session.md validator | 5 | 2 | 5 | 12 | 3 | 2 | 5 | 2.4 | sonnet |
| 6 | Session scraping | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 6 | Worktree merge from main | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 6 | Handoff --commit removal | 5 | 3 | 3 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 9 | Explore Anthropic plugins | 2 | 3 | 3 | 8 | 3 | 1 | 4 | 2.0 | sonnet, restart |
| 9 | Wt ls session ordering | 5 | 2 | 1 | 8 | 3 | 1 | 4 | 2.0 | sonnet |
| 11 | Tool deviation hook | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 11 | Artifact staleness gate | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 11 | Lint-gated recall | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 11 | Lint recall gate | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 11 | Recall tool consolidation | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | sonnet |
| 11 | Ground workflow skills | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 11 | Markdown migration | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 18 | Merge lifecycle audit * | 3 | 3 | 5 | 11 | 3 | 3 | 6 | 1.8 | sonnet |
| 18 | Codebase sweep | 2 | 2 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 18 | Block cd-chaining | 3 | 1 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 21 | Fix task-context bloat | 5 | 2 | 3 | 10 | 5 | 1 | 6 | 1.7 | sonnet |
| 22 | Skill-dev skill | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 22 | Entry gate propagation | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 22 | Retrofit skill pre-work | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 22 | Wt rm task cleanup * | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 22 | Worktree ad-hoc task * | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 22 | Tweakcc | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 22 | Plugin migration | 2 | 8 | 3 | 13 | 3 | 5 | 8 | 1.6 | opus |
| 29 | Remove wt rm --force | 2 | 1 | 3 | 6 | 3 | 1 | 4 | 1.5 | sonnet |
| 29 | Design context gate * | 3 | 3 | 3 | 9 | 3 | 3 | 6 | 1.5 | sonnet |
| 31 | Generate memory index | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 31 | Agent rule injection | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | sonnet |
| 31 | Tier threshold grounding | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 34 | Handoff insertion policy | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 34 | Test diagnostic helper | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 34 | Cross-tree requirements | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 34 | Agentic prose terminology | 2 | 1 | 1 | 4 | 2 | 1 | 3 | 1.3 | sonnet |
| 38 | Corrector removal audit * | 3 | 2 | 5 | 10 | 5 | 3 | 8 | 1.2 | sonnet |
| 38 | Wt merge-rm shorthand * | 3 | 1 | 1 | 5 | 3 | 1 | 4 | 1.2 | sonnet |
| 38 | Memory-index loading docs | 2 | 2 | 1 | 5 | 3 | 1 | 4 | 1.2 | sonnet |
| 41 | Runbook outline review | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 41 | TDD test optimization | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 41 | Review auto-commit | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 41 | Moderate outline gate | 3 | 3 | 3 | 9 | 5 | 3 | 8 | 1.1 | opus, self-ref |
| 41 | Dev integration branch | 3 | 3 | 3 | 9 | 5 | 3 | 8 | 1.1 | opus |
| 46 | Worktree CLI UX * | 3 | 1 | 3 | 7 | 5 | 2 | 7 | 1.0 | sonnet |
| 46 | Recall deduplication | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 46 | Recall pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 46 | Compensate-continue skill | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 46 | Skill prompt-composer | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 46 | Model directive pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 46 | Decision drift audit | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 46 | Recall usage scoring | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 46 | Delivery supercession | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 46 | Upstream skills field | 1 | 1 | 1 | 3 | 2 | 1 | 3 | 1.0 | sonnet |
| 46 | Registry cache to tmp | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet, inline |
| 46 | Update prioritize skill | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet |
| 58 | Merge lock retry * | 2 | 1 | 3 | 6 | 5 | 2 | 7 | 0.9 | sonnet |
| 58 | Diagnose compression loss | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 58 | Test diamond migration | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 58 | Safety review expansion | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 58 | Recall learnings design | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 58 | Feature prototypes | 2 | 2 | 2 | 6 | 5 | 2 | 7 | 0.9 | sonnet |
| 64 | Diagnostic opus review | 2 | 1 | 3 | 6 | 5 | 3 | 8 | 0.8 | opus |
| 64 | Task notation migration * | 1 | 1 | 1 | 3 | 3 | 1 | 4 | 0.8 | sonnet |
| 66 | Infrastructure scripts | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 66 | Cache expiration | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 66 | Prioritize script | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 69 | Design-to-deliverable | 3 | 2 | 3 | 8 | 8 | 5 | 13 | 0.6 | opus, restart |
| 70 | Ground state coverage | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 70 | Workflow formal analysis | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 70 | Prose gate terminology | 2 | 1 | 1 | 4 | 5 | 3 | 8 | 0.5 | opus |
| 73 | Behavioral design | 2 | 1 | 2 | 5 | 8 | 5 | 13 | 0.4 | opus |

**Blocked tasks** (scored but not actionable):
- Parallel orchestration — blocked on Orchestrate evolution
- Session CLI tool — blocked [!]
- Python hook ordering fix — blocked [!]
- Calibrate topic params — UPS topic injection delivered, but task needs production data accumulation
- Test diamond migration — depends on runbook evolution (delivered, but task not updated)
- Safety review expansion — depends on Explore Anthropic plugins

## Delivered Since Last Report (removed)

- Recall skill path fix (was rank 2, priority 4.5) — delivered
- UPS topic injection (was rank 3, priority 3.2) — delivered, worktree merged
- Task classification (was rank 5, priority 2.8) — delivered
- Fix planstate detector (was rank 6, priority 2.6) — superseded (all FRs implemented)
- Runbook recall expansion (was rank 9, priority 2.2) — delivered

## Disappeared (absorbed or canceled)

- Continuation prepend (was rank 25, priority 1.6) — not in session.md
- Pushback grounding (was rank 25, priority 1.6) — plan exists, no task entry
- Worktree fuzzy matching (was rank 36, priority 1.3) — canceled [–]

## Recommended Execution Order

User directive preserved: recall → workflow prose → workflow non-prose → rest.

### Quick wins (ME=1, immediate)

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 1 | Merge completed filter | 4.0 | Single-line fix in resolve.py. Prevents completed tasks leaking on merge. |

### Tier 1: Recall (foundational)

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 2 | Recall tool consolidation | 1.9 | Foundational rename + consolidation. Absorbs stale recall artifact. Grounding report available. |
| 3 | Artifact staleness gate | 1.9 | Mechanical checkpoint at skill exit points. Depends on recall consolidation semantics. |
| 4 | Lint-gated recall | 1.9 | PostToolUse injection on lint state transition. |
| 5 | Lint recall gate | 1.9 | PreToolUse scan before fix attempt. Complements lint-gated recall. |

### Tier 2: Workflow prose

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 6 | Skill disclosure | 2.6 | Progressive disclosure at gate boundaries. Requirements exist. |
| 7 | Ground workflow skills | 1.9 | Per audit: /runbook → review agents → /orchestrate → /handoff. |

### Tier 3: Workflow non-prose

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 8 | Orchestrate evolution | 6.0 | Highest WSJF. Ready for orchestration. Restart required. |
| 9 | Execute flag lint | 3.0 | Precommit lint gate for /inline execute in session.md. |
| 10 | Session.md validator | 2.4 | Scripted precommit check. Requirements exist. |

## Parallel Batches

**Batch A — sonnet, inline/mechanical, no restart:**
- Merge completed filter (4.0) — target: resolve.py
- Agentic prose terminology (1.3) — target: codebase-wide search/replace
- Memory-index loading docs (1.2) — target: docs referencing memory-index loading
- Task notation migration (0.8) — target: 23 files, regex update

**Batch B — sonnet, worktree infrastructure, no restart:**
- Wt rm task cleanup (1.6) — target: worktree rm, session.md handling
- Worktree ad-hoc task (1.6) — target: worktree new, session.md handling
- Wt merge-rm shorthand (1.2) — target: worktree skill

**Batch C — sonnet, merge infrastructure:**
- Merge lifecycle audit (1.8) — target: merge.py, resolve.py, integration tests
- Worktree merge from main (2.2) — target: merge flow

**Batch D — sonnet, precommit/validation:**
- Execute flag lint (3.0) — target: precommit validators
- Session.md validator (2.4) — target: precommit validators
- Block cd-chaining (1.8) — target: PreToolUse hook

**Batch E — opus, workflow design:**
- Skill disclosure (2.6) — target: /design, /runbook skill loading
- Ground workflow skills (1.9) — target: skills per audit
- Entry gate propagation (1.6) — target: /orchestrate, /deliverable-review, corrector

**Batch F — sonnet, restart cohort:**
- Orchestrate evolution (6.0) — 14 steps, restart required
- Explore Anthropic plugins (2.0) — install 28 plugins, restart required

## Scoring Assumptions

- **Merge completed filter ME=1:** Session.md says "Single-line fix: exclude blocks whose first line matches completed/canceled markers." Target file and change known.
- **Merge lifecycle audit CRR=5:** Multiple merge failure modes documented in Blockers/Gotchas. Absorbs merge-submodule-ordering.
- **Task notation migration WF=1, CRR=1:** Cosmetic notation change (✗ → †). No workflow friction or defect reduction — purely readability.
- **Corrector removal audit CRR=5:** Pattern appeared twice (task-classification incident + composite tasks learning). Defect compounding in review flow.
- **Design context gate DP=3:** References UPS hook infrastructure which is still evolving. ME=3 because requirements exist at `plans/design-context-gate/requirements.md`.
- **Worktree CLI UX ME=5:** No design artifact. Multiple independent improvements (stdout cleanup, exit status, error messages).
- **Calibrate topic params:** UPS topic injection delivered, formally unblocking this task. But the task needs production data to accumulate — practically still waiting.

## Unscheduled Plans (no associated task)

Plans with artifacts but no pending task in session.md:
- complexity-routing [requirements]
- discuss-to-pending [requirements]
- fix-wt-parallel-restart [requirements]
- inline-execute [rework]
- phase-scoped-agents [ready]
- pushback-grounding [requirements]
- runbook-generation-fixes [ready]
- task-lifecycle [outlined]
- update-grounding-skill [outlined]
- worktree-merge-resilience [outlined]
- worktree-rm-error-ux [outlined]
- wt-exit-ceremony [requirements]

## Tension: WSJF vs User Directive

Orchestrate evolution (6.0) still scores highest but falls in tier 3 (workflow non-prose). Merge completed filter (4.0) is the highest-priority quick win — ME=1, single-line fix. The recall tier lost its highest-priority members (skill path fix delivered at 4.5, UPS at 3.2) — remaining recall tasks cluster at 1.9.

Pragmatic ordering: Merge completed filter (inline) → Recall tool consolidation → Skill disclosure → Orchestrate evolution → rest of tiers.
