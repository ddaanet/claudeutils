# Task Prioritization — 2026-02-24

**Formula:** `Priority = Cost_of_Delay / Job_Size`
**CoD** = Workflow Friction + Decay Pressure + Compound Risk Reduction
**Size** = Marginal Effort + Context Recovery Cost

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Orchestrate evolution | 8 | 5 | 8 | 21 | 2 | 2 | 4 | 5.3 | sonnet, self-ref ⚠️ |
| 2 | Session CLI tool | 8 | 3 | 5 | 16 | 2 | 2 | 4 | 4.0 | sonnet, **BLOCKED [!]** |
| 3 | Planstate delivered status | 5 | 5 | 5 | 15 | 2 | 2 | 4 | 3.8 | sonnet |
| 4 | Session.md validator | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | sonnet, self-ref ⚠️ |
| 5 | WT merge session loss dx | 3 | 5 | 5 | 13 | 3 | 2 | 5 | 2.6 | sonnet |
| 6 | Parallel orchestration | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet, blocked on #1 |
| 7 | Merge learnings delta | 3 | 5 | 3 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 8 | Test diagnostic helper | 5 | 2 | 5 | 12 | 5 | 1 | 6 | 2.0 | sonnet |
| 9 | UserPromptSubmit topic hook | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 10 | Handoff wt awareness | 5 | 3 | 3 | 11 | 5 | 1 | 6 | 1.8 | sonnet, self-ref ⚠️ |
| 11 | Codebase sweep | 3 | 3 | 3 | 9 | 3 | 2 | 5 | 1.8 | sonnet |
| 12 | Tweakcc | 3 | 3 | 3 | 9 | 3 | 2 | 5 | 1.8 | sonnet |
| 13 | Precommit python3 redirect | 5 | 2 | 5 | 12 | 5 | 2 | 7 | 1.7 | sonnet |
| 14 | Handoff insertion policy | 5 | 2 | 3 | 10 | 5 | 1 | 6 | 1.7 | sonnet |
| 15 | Fix task-context.sh bloat | 5 | 1 | 3 | 9 | 5 | 1 | 6 | 1.5 | sonnet |
| 16 | Execute plugin migration | 2 | 8 | 5 | 15 | 5 | 5 | 10 | 1.5 | opus, stale |
| 17 | Model directive pipeline | 5 | 3 | 3 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 18 | Explore Anthropic plugins | 2 | 3 | 5 | 10 | 5 | 2 | 7 | 1.4 | sonnet, restart |
| 19 | Consolidate recall tooling | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 20 | Agent rule injection | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 21 | Worktree merge from main | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 22 | Cross-tree req transport | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 23 | TDD cycle test optimization | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 24 | Deslop remaining skills | 3 | 2 | 1 | 6 | 5 | 1 | 6 | 1.0 | sonnet |
| 25 | Continuation prepend | 2 | 2 | 1 | 5 | 3 | 2 | 5 | 1.0 | sonnet |
| 26 | Design-to-deliverable | 3 | 3 | 5 | 11 | 8 | 3 | 11 | 1.0 | opus, restart |
| 27 | Feature prototypes | 2 | 2 | 1 | 5 | 3 | 2 | 5 | 1.0 | sonnet |
| 28 | Diagnose compression loss | 2 | 1 | 3 | 6 | 5 | 3 | 8 | 0.8 | sonnet |
| 29 | Migrate test suite diamond | 3 | 3 | 3 | 9 | 8 | 3 | 11 | 0.8 | sonnet, depends on runbook evolution |
| 30 | Behavioral design | 2 | 2 | 3 | 7 | 8 | 3 | 11 | 0.6 | opus |
| 31 | Diagnostic opus review | 2 | 2 | 3 | 7 | 8 | 3 | 11 | 0.6 | opus |
| 32 | Ground state-machine review | 2 | 2 | 3 | 7 | 8 | 3 | 11 | 0.6 | opus |
| 33 | Cache expiration prototype | 2 | 1 | 1 | 4 | 5 | 2 | 7 | 0.6 | sonnet |
| 34 | Infrastructure scripts | 2 | 1 | 1 | 4 | 5 | 2 | 7 | 0.6 | sonnet |
| 35 | Safety review expansion | 1 | 2 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus, blocked on #18 |
| 36 | Workflow formal analysis | 1 | 2 | 3 | 6 | 8 | 3 | 11 | 0.5 | opus |
| 37 | Upstream skills field | 1 | 1 | 1 | 3 | 5 | 2 | 7 | 0.4 | sonnet |

## Parallel Batches

**Batch A — Top tier (sonnet, no restart):**
- Orchestrate evolution (5.3) — plan: orchestrate-evolution
- Planstate delivered status (3.8) — plan: planstate-delivered
- WT merge session loss dx (2.6) — plan: worktree-merge-resilience
- Session.md validator (2.6) — plan: session-validator

No shared plans, no shared target files, no dependency. All sonnet. 4 concurrent worktrees.

**Batch B — Mid tier (sonnet, no restart):**
- Merge learnings delta (2.2) — plan: merge-learnings-delta
- Test diagnostic helper (2.0) — target: subprocess patterns
- Codebase sweep (1.8) — plan: codebase-sweep

Independent plans, different target files.

**Batch C — Opus cohort:**
- Model directive pipeline (1.4)
- Behavioral design (0.6)
- Diagnostic opus review (0.6)
- Ground state-machine review criteria (0.6)

All opus, all research-heavy. Low urgency — batch when opus session is already active.

**Restart cohort:**
- Explore Anthropic plugins (1.4) — sonnet, restart
- Design-to-deliverable (1.0) — opus, restart

## Top 5 Recommendations

**1. Orchestrate evolution (5.3)** — Highest priority by wide margin. Every orchestrated execution uses the orchestrator (WF=8), design complete and ready for runbook (ME=2), and addresses 3+ observed agent reliability patterns (CRR=8: escalation, context management, guardrails). Self-referential: modifies the infrastructure it runs on — needs manual verification after delivery.

**2. Planstate delivered status (3.8)** — Unblocks accurate plan status reporting across session display, validator, and handoff. Design reviewed with 7 decisions resolved. Low effort to execute (ME=2). High decay pressure (DP=5) as more plans accumulate on the current ad-hoc state tracking.

**3. Session.md validator (2.6) / WT merge session loss dx (2.6)** — Tied. Both address observed session data integrity failures. Tiebreak: validator has WF=5 (every handoff) vs dx WF=3 (per merge). However, session.md Next Steps names the dx task first — suggests context is warm. Run both in parallel batch A.

**4. Merge learnings delta (2.2)** — Decay pressure is the driver (DP=5): each session with diverged learnings.md compounds the reconciliation difficulty. Strategy already identified (main base + branch delta), making execution straightforward.

**5. Test diagnostic helper (2.0)** — Opaque subprocess failures (WF=5) hit every test session. No plan needed — scope is clear (replace subprocess.run check=True with stderr surfacing). Small, high-value fix.

## Scoring Assumptions

- **Session CLI tool** scored high (4.0) but excluded from actionable recommendations due to [!] blocked status. Unblocking signal unknown from current session context.
- **Parallel orchestration** depends on orchestrate evolution completing — cannot start until #1 delivers.
- **Execute plugin migration** penalized heavily on Size (ME=5, CRC=5) due to Feb 9 staleness requiring outline rewrite despite [ready] status.
- **Planstate delivered status** CLI reports `[requirements]` but session.md notes "designed" with reviewed outline. Scored ME=2 based on session.md evidence of completed design work. Plan state markers likely not updated on disk.
- Self-referential tasks (orchestrate evolution, session.md validator, handoff wt awareness) flagged — changes to these modify the infrastructure that validates/executes them.
- Tasks with no plan artifact scored ME=5 even when scope is small (e.g., fix task-context.sh). The scoring table measures readiness-to-execute, not absolute work size.
