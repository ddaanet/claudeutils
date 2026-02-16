# Task Prioritization — 2026-02-16 (rev 2)

**Formula:** `Priority = Cost_of_Delay / Job_Size`
**Scope:** 27 pending tasks from session.md. 3 worktree tasks excluded (separate execution context).
**Delta from rev 1:** Precommit improvements and Vet proportionality completed; 5 new tasks scored (Expand runbook, Handoff insertion policy, Rename vet agents, Design-to-deliverable, Worktree skill adhoc mode).

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Expand runbook | 3 | 5 | 5 | 13 | 2 | 3 | 5 | 2.6 | sonnet |
| 2 | Remaining workflow items | 5 | 5 | 5 | 15 | 3 | 3 | 6 | 2.5 | sonnet |
| 3 | Execute plugin migration | 2 | 8 | 3 | 13 | 3 | 3 | 6 | 2.2 | opus |
| 4 | Commit CLI tool | 8 | 3 | 3 | 14 | 5 | 2 | 7 | 2.0 | sonnet |
| 5 | Vet delegation routing | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 6 | Model tier awareness hook | 5 | 1 | 5 | 11 | 5 | 1 | 6 | 1.8 | sonnet, restart |
| 7 | Remember skill update | 3 | 3 | 3 | 9 | 3 | 2 | 5 | 1.8 | opus |
| 8 | Continuation prepend | 3 | 3 | 3 | 9 | 3 | 2 | 5 | 1.8 | sonnet |
| 9 | Memory-index auto-sync | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 10 | RED pass protocol | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | sonnet |
| 11 | Agent rule injection | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | sonnet |
| 12 | Diagnostic opus review | 3 | 3 | 5 | 11 | 3 | 5 | 8 | 1.4 | opus |
| 13 | Handoff insertion policy | 5 | 2 | 3 | 10 | 5 | 2 | 7 | 1.4 | sonnet |
| 14 | Pretool hook cd pattern | 3 | 1 | 5 | 9 | 5 | 2 | 7 | 1.3 | sonnet, restart |
| 15 | Handoff wt awareness | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 16 | Learning ages consol | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 17 | Codebase quality sweep | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 18 | Remember agent routing | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet, blocked |
| 19 | Design-to-deliverable | 3 | 2 | 3 | 8 | 8 | 3 | 11 | 0.7 | opus, restart |
| 20 | Feature prototypes | 1 | 2 | 1 | 4 | 3 | 3 | 6 | 0.7 | sonnet |
| 21 | Behavioral design | 3 | 2 | 3 | 8 | 8 | 5 | 13 | 0.6 | opus |
| 22 | Infrastructure scripts | 2 | 1 | 1 | 4 | 5 | 2 | 7 | 0.6 | sonnet |
| 23 | Worktree skill adhoc mode | 2 | 1 | 1 | 4 | 5 | 2 | 7 | 0.6 | sonnet |
| 24 | Upstream skills field | 1 | 1 | 1 | 3 | 5 | 1 | 6 | 0.5 | sonnet |
| 25 | Workflow formal analysis | 1 | 1 | 3 | 5 | 8 | 5 | 13 | 0.4 | opus |
| 26 | Rename remember skill | 1 | 1 | 1 | 3 | 5 | 2 | 7 | 0.4 | sonnet, restart |
| 27 | Rename vet agents | 1 | 1 | 1 | 3 | 5 | 2 | 7 | 0.4 | sonnet, restart |

## Parallel Batches

**Batch A (sonnet, no restart) — 4 tasks, independent targets:**
- Expand runbook (2.6) — worktree-merge-data-loss phase expansion
- Commit CLI tool (2.0) — CLI commands, commit workflow
- Vet delegation routing (1.9) — vet routing rules
- Memory-index auto-sync (1.6) — memory consolidation hooks

**Batch B (opus) — 3 tasks, independent:**
- Execute plugin migration (2.2) — plugin outline refresh + orchestrate
- Remember skill update (1.8) — `/design` Phase B discussion
- Diagnostic opus review (1.4) — RCA methodology requirements

**Batch C (sonnet, no restart) — workflow improvements:**
- RED pass protocol (1.6) — orchestrate skill
- Agent rule injection (1.6) — agent templates
- Handoff insertion policy (1.4) — handoff skill

**Batch D (sonnet, restart) — hook tasks:**
- Model tier awareness hook (1.8) — model injection hook
- Pretool hook cd pattern (1.3) — cd bypass in pretool hook

## Top 5 Recommendations

- **Expand runbook** (2.6) — Highest priority. Data loss bug in worktree merge is high-impact defect (CRR=5). Outline reviewed, opus findings ready to incorporate. ME=2 because expansion is the only remaining step. Lint debt blocks eventual merge but not expansion.
- **Remaining workflow items** (2.5) — Contains orchestrate evolution (designed, ready for `/runbook`) plus 5 other sub-items touching orchestration, commit, and agent output. DP=5: orchestrate design from Feb 13 references evolving structures.
- **Execute plugin migration** (2.2) — DP=8 is the highest decay pressure in the backlog. Stale since Feb 9 with measurable drift (19 skills vs 16, 14 agents vs 12, justfile rewritten). Every session increases refresh cost.
- **Commit CLI tool** (2.0) — WF=8 (every commit, inner loop). Modeled on worktree CLI pattern which provides a template, reducing design risk. Needs `/design` but scope is clear.
- **Vet delegation routing** (1.9) — CRR=5: wrong reviewer receiving wrong artifacts is a measured failure mode. Routing table exists in pipeline-contracts.md but not enforced in vet-requirement.md.

## Scoring Assumptions

- **Expand runbook** ME=2: `planned` in jobs.md with reviewed outline and opus review on disk. Higher than 1 because phase expansion is a non-trivial step.
- **Remaining workflow items** scored as aggregate: orchestrate-evolution (designed) drives ME=3. Sub-items vary but batch amortizes context recovery.
- **Execute plugin migration** ME=3 despite `planned` in jobs.md: session notes flag staleness requiring outline refresh before orchestration.
- **Remember skill update** model corrected to opus per session.md task metadata.
- **Handoff insertion policy** WF=5: fires every handoff despite agents compensating. Agents spend inference budget overriding the "append" instruction. CRR=3 because compensation works — correctness impact is low.
- **Feature prototypes** ME=3: requirements.md exists (jobs.md status: requirements).
- **Remember agent routing** marked blocked per session.md (blocked on memory redesign).
- **Design-to-deliverable** ME=8: greenfield + tmux-like automation research required.
