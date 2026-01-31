# Session Handoff: 2026-01-31

**Status:** Reflect workflow complete — handoff skill fix for `--commit` tail-call semantics.

## Completed This Session

**Reflect: handoff `--commit` pending-commit RCA:**
- Previous opus session wrote "Ready to commit" status and "pending commit" footer despite `--commit` tail-call
- Root cause: handoff skill rule against commit tasks only named "Pending Tasks or Next Steps" sections — agent put equivalent language in Status/footer
- Fix: broadened rule in `agent-core/skills/handoff/SKILL.md:75-78` to cover all sections, explicitly named the anti-patterns, explained tail-call atomicity
- Learning added to `agents/learnings.md`

## Pending Tasks

- [ ] **Fix all `/vet` skill references → vet agent** — codebase-wide replacement of `/vet` invocations with vet agent delegation. Includes plan-adhoc Tier 3 Point 3, workflows-terminology route descriptions, oneshot-workflow stages | sonnet
- [ ] **Orchestrate: integrate vet agent** — vet changes and apply high/medium fixes during orchestration, not postponed to next session | sonnet
- [ ] **Orchestrate: integrate review-tdd-process** — rename review-analysis, use custom sonnet sub-agent, runs during orchestration | sonnet
- [ ] **Refactor oneshot handoff template** — integrate into current handoff/pending/execute framework | sonnet
- [ ] **Evaluate oneshot skill** — workflow now always starts with /design, may be redundant | opus
- [ ] **Update heredoc references** — sandboxed heredoc fix landed. Remove workarounds, restore vendor default heredoc behavior for commit messages | sonnet
- [ ] **Resume workflow-controls orchestration (steps 2-7)** — `/orchestrate workflow-controls` | sonnet | restart
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Create /reflect skill** — deviation detection → RCA → fix → handoff/commit automation. Load plugin-dev skills first | opus
- [ ] **Insert skill loading in design docs** — design skill should load relevant plugin-dev skills when topic involves hooks/agents/skills | sonnet
- [ ] **Update workflow skills: pbcopy next command** — commit/handoff STATUS display copies next command to clipboard | sonnet
- [ ] **Add "go read the docs" checkpoints** — partially addressed by design-work.md rule | sonnet
- [ ] **Design runbook identifier solution** — `/design plans/runbook-identifiers/problem.md` | opus
- [ ] **Create design-vet-agent** — dedicated opus agent for design review, artifact-return pattern | opus
- [ ] **Add execution metadata to step files** — step files declare dependencies and execution mode | sonnet
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases in orchestrate skill | sonnet

## Blockers / Gotchas

**Commit-rca-fixes active (from previous session):**
- Fix 3 (orchestrator stop rule) prevents dirty-state rationalization
- Fix 2 (artifact staging) ensures prepare-runbook.py artifacts are staged
- Fix 1 (submodule awareness) prevents submodule pointer drift

## Next Steps

First batch of pending work: fix `/vet` references codebase-wide, then integrate vet agent and review-tdd-process into orchestrate skill. These form a cohesive group around the vet-as-agent pattern.

---
*Handoff by Opus. Reflect fix applied.*
