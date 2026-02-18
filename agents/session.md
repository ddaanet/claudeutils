# Session: Worktree — Design runbook evolution

**Status:** Focused worktree for parallel execution.

## Completed This Session

**Design skill complexity gates:**
- Entry gate: artifact-aware triage reads plan directory before classification — existing outline can skip ceremony
- Mid-stream gate: post-outline re-check downgrades complexity when outline reveals simpler work
- File: `agent-core/skills/design/SKILL.md` (+21 lines)

**Outline review (A.6) + user discussion (B):**
- Outline-review-agent found FR-2a anti-pattern gap, FR-3c "mocked I/O" contradiction — fixes applied to outline
- User decisions: rewrite existing anti-pattern entry (not append), leave xfail checkpoint unchanged
- Report: `plans/runbook-evolution/reports/outline-review.md`

**Prototype:** `plans/prototypes/recover-agent-writes.py` — extracts Write calls from agent session logs

## Pending Tasks

- [ ] **Design runbook evolution** — `/design plans/runbook-evolution/` | opus
  - Requirements at `plans/runbook-evolution/requirements.md`
  - Outline reviewed, user decisions captured — re-run `/design` to validate new entry gate, then execute
  - Entry gate should see sufficient outline → skip to Phase B → sufficiency gate → execute directly
  - Scope: runbook SKILL.md generation directives only (2 files, prose edits)
  - 5 FRs: prose atomicity, self-modification discipline, testing diamond, deferred enforcement, test migration

## Blockers / Gotchas

**learnings.md at 196 lines (soft limit 80):**
- No entries ≥7 active days — consolidation batch insufficient
- Size trigger fires but nothing eligible for `/remember`

## Next Steps

Re-run `/design plans/runbook-evolution/` in clean opus session. Validates entry gate: existing outline should skip ceremony and route to execution.
