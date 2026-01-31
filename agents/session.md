# Session Handoff: 2026-01-31

**Status:** Oneshot skill removed, `/design` is now the universal implementation entry point.

## Completed This Session

**Oneshot handoff template refactoring (d76235f):**
- Replaced `## Current Work` / `## Key Context` / `### Workflow:` subsections with flat pending tasks using standard handoff sections
- Aligned shelve template with handoff template structure
- Added communication rule 5: use AskUserQuestion for choices, not prose yes/no

**Oneshot skill evaluation and removal:**
- Evaluated oneshot skill — found redundant: complexity triage duplicated by plan skills' tier assessment, methodology detection duplicated by design skill
- Only unique function (shelve check) absorbed into design skill Step 0
- Added complexity triage (Step 0) to `/design` skill: simple → execute directly, moderate → skip to /plan-adhoc, complex → full design
- Removed `agent-core/skills/oneshot/` directory and `.claude/skills/oneshot` symlink
- Renamed "oneshot workflow" → "general workflow" across all active documentation
- Renamed `agent-core/agents/oneshot-workflow.md` → `agent-core/docs/general-workflow.md`
- Updated entry point in `workflows-terminology.md`: implementation tasks → `/design` (was `/oneshot`)
- Updated references in: orchestrate, vet, plan-adhoc, tdd-workflow, README files, templates
- Reverted `plans/README.md` — historical plan docs must not be modified
- Vet review caught: plans/README.md modification, orphaned `/oneshot` references in tdd-workflow.md, inconsistent terminology in 6 files — all fixed

## Pending Tasks

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

**Commit-rca-fixes active:**
- Fix 3 (orchestrator stop rule) prevents dirty-state rationalization
- Fix 2 (artifact staging) ensures prepare-runbook.py artifacts are staged
- Fix 1 (submodule awareness) prevents submodule pointer drift

**Learnings file at 151/80 lines** — needs `/remember` consolidation urgently.

**Historical plans/ directory has accumulated stale artifacts** — orchestration lacks proper continuation with cleanup and testing. Don't modify historical plan files.

## Next Steps

Run `/remember` to consolidate learnings before next session.

---
*Handoff by Opus. Oneshot skill removed, /design is universal entry point.*
