# Task Prioritization — 2026-03-12

42 tasks scored, post-/proof session. Supersedes `prioritization-2026-03-06b.md` (65 tasks). Many tasks absorbed/killed during proof cycle.

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Session CLI tool | 3 | 3 | 5 | 11 | 1 | 2 | 3 | 3.7 | sonnet |
| 2 | Plugin migration | 2 | 8 | 3 | 13 | 1 | 3 | 4 | 3.2 | opus |
| 3 | Worktree merge lifecycle | 3 | 3 | 5 | 11 | 2 | 2 | 4 | 2.8 | sonnet |
| 4 | Active Recall | 5 | 3 | 5 | 13 | 2 | 3 | 5 | 2.6 | opus |
| 5 | Directive skill promotion | 5 | 3 | 5 | 13 | 3 | 3 | 6 | 2.2 | opus |
| 6 | Parallel orchestration | 2 | 2 | 5 | 9 | 3 | 2 | 5 | 1.8 | sonnet |
| 7 | System property tracing | 2 | 3 | 5 | 10 | 3 | 3 | 6 | 1.7 | opus |
| 8 | Skill-gated session edits | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | opus |
| 9 | Gate batch | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 10 | Worktree lifecycle CLI | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 11 | Hook batch | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 12 | Design review protocol | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | opus, restart |
| 13 | Design context gate | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 14 | Decision drift audit | 2 | 3 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 15 | Design pipeline evolution | 2 | 3 | 3 | 8 | 3 | 2 | 5 | 1.6 | opus |
| 16 | Markdown migration | 1 | 1 | 1 | 3 | 1 | 1 | 2 | 1.5 | sonnet |
| 17 | Merge any parent | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 18 | Skill agent bootstrap | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | opus |
| 19 | Code quality | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 20 | Quality grounding | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | opus |
| 21 | Cross-tree operations | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 22 | Review agent quality | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 23 | Design JIT expansion | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 24 | Fix TDD context scoping | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 25 | Review gate | 2 | 2 | 3 | 7 | 3 | 2 | 5 | 1.4 | sonnet |
| 26 | Threshold token migration | 2 | 3 | 3 | 8 | 3 | 3 | 6 | 1.3 | sonnet |
| 27 | Update prioritize skill | 2 | 2 | 1 | 5 | 3 | 1 | 4 | 1.2 | sonnet |
| 28 | Diagnose compression loss | 1 | 2 | 3 | 6 | 3 | 3 | 6 | 1.0 | sonnet |
| 29 | Recall pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 30 | Markdown AST parser | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 31 | Planstate brief inference | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet |
| 32 | Skill exit commit | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet |
| 33 | Tweakcc | 2 | 2 | 1 | 5 | 3 | 2 | 5 | 1.0 | sonnet |
| 34 | Small fixes batch | 2 | 2 | 1 | 5 | 3 | 2 | 5 | 1.0 | sonnet |
| 35 | Research backlog | 1 | 1 | 3 | 5 | 3 | 3 | 6 | 0.8 | opus |
| 36 | Update tokens CLI | 1 | 1 | 1 | 3 | 3 | 1 | 4 | 0.8 | haiku |
| 37 | Python hook ordering fix | 1 | 1 | 1 | 3 | 3 | 1 | 4 | 0.8 | haiku, restart |
| 38 | Retro repo expansion | 1 | 2 | 1 | 4 | 3 | 3 | 6 | 0.7 | sonnet |
| 39 | Health check UPS fallback | 1 | 1 | 1 | 3 | 3 | 2 | 5 | 0.6 | sonnet |
| 40 | Feature prototypes | 1 | 1 | 1 | 3 | 3 | 2 | 5 | 0.6 | sonnet |
| 41 | Incident counting | 1 | 1 | 1 | 3 | 3 | 2 | 5 | 0.6 | opus |
| 42 | Verb form AB test | 1 | 1 | 1 | 3 | 3 | 3 | 6 | 0.5 | sonnet, blocked |

Column key: WF=Workflow Friction, DP=Decay Pressure, CRR=Compound Risk Reduction, ME=Marginal Effort, CRC=Context Recovery Cost.

## Consolidation

**Absorptions:**
- **Markdown migration** (1.5) — closure action only (`_planstate close`). All sub-problems killed/absorbed during /proof. Not a real work item.
- **Research backlog** (0.8) — SP-1/2/3 absorbed into System property tracing. Remaining SP-4/SP-5 are thin research items.

**Merge candidates:**
- **Gate batch** (1.6) + **Review gate** (1.4) → "Gate infrastructure" — both target gate mechanisms, same design session
- **Design context gate** (1.6) + **Design JIT expansion** (1.4) → "Design skill improvements" — both modify /design behavior
- **Update prioritize skill** (1.2) + **Planstate brief inference** (1.0) + **Small fixes batch** (1.0) + **Skill exit commit** (1.0) → "Maintenance batch" — low-priority, small-scope improvements
- **Update tokens CLI** (0.8) + **Python hook ordering fix** (0.8) → "Haiku batch" — trivial, batch for restart cohort

**No change:** Worktree lifecycle CLI already absorbs merge-lifecycle-audit, plan-completion-ceremony per session.md.

## Parallel Batches

**Batch A — top priority, ready plans (3.7–3.2):**
- Session CLI tool (3.7, sonnet) — plan ready, no overlap
- Plugin migration (3.2, opus) — plan ready, needs outline refresh

**Batch B — outlined plans (2.8–2.6):**
- Worktree merge lifecycle (2.8, sonnet) — worktree merge code
- Active Recall (2.6, opus) — recall subsystem, no overlap with merge

**Batch C — design-stage, independent (2.2–1.8):**
- Directive skill promotion (2.2, opus) — skill/fragment targets
- Parallel orchestration (1.8, sonnet) — orchestration mechanics
- System property tracing (1.7, opus) — requirements/traceability

**Batch D — sonnet mid-tier cluster (1.6, parallelizable):**
- Gate batch + Review gate (merged) — gate infrastructure
- Worktree lifecycle CLI — worktree CLI behavior
- Hook batch — hook infrastructure
- Design context gate + Design JIT expansion (merged) — /design skill

## Top 5 Recommendations

1. **Session CLI tool (3.7)** — Highest priority. Plan `ready`, step files generated, blocker resolved (Bootstrap tag support). ME=1 makes this the best CoD/Size ratio. New #1 (previously not scored separately from fix-task-context-bloat).

2. **Plugin migration (3.2)** — Extreme decay pressure (DP=8, stale since Feb 9, now 5+ weeks). Plan `ready` but outline needs refresh before orchestration. Parallel with Session CLI tool — no overlap.

3. **Worktree merge lifecycle (2.8)** — High CRR from documented merge failures (permanent blocker in session.md). Outlined status keeps size low. Absorbs merge-lifecycle-audit and plan-completion-ceremony.

4. **Active Recall (2.6)** — Highest CoD (13) driven by session-boundary friction (WF=5) and downstream unblock (CRR=5). Outline Rev 2 reviewed. Next: Phase B user discussion → design or runbook.

5. **Directive skill promotion (2.2)** — High WF (5) from session-boundary directives, absorbs 5 sub-tasks. Opus design session. Can parallel with Parallel orchestration and System property tracing.

## Scoring Assumptions

- **Session CLI tool ME=1:** Plan status `ready`, step files generated. Blocker (Bootstrap tag support) resolved per session.md note.
- **Plugin migration DP=8:** `ready` since Feb 9 (~5 weeks). Strongest decay signal. Session.md note says "refresh outline first."
- **Markdown migration ME=1, Priority=1.5:** Anomalously high for a closure action. Same formula artifact as Registry cache to tmp in prior scoring — tiny Size inflates ratio. Actual priority is trivial (one command).
- **Reviewed plans (skill-agent-bootstrap, quality-grounding, review-agent-quality, design-pipeline-evolution, diagnose-compression-loss, research-backlog):** Post-/proof status. Next action is `/design`. Scored as ME=3 (same as briefed — brief exists, design needed).
- **Active Recall sub-tasks (AR S-B through S-L):** Not scored individually — blocked on parent design decisions. Scored via parent task's CRR.
- **Verb form AB test:** Blocked on human curation, scored but excluded from scheduling.
