# Session Handoff: 2026-02-01

**Status:** Shortcut documentation and help shortcut added.

## Completed This Session

**`?` help shortcut and shortcut documentation:**
- Added `?` as Tier 1 command in `agent-core/hooks/userpromptsubmit-shortcuts.py` — lists shortcuts, keywords, and entry point skills
- Added `?` to vocabulary table in `agent-core/fragments/execute-rule.md`
- Created `agent-core/docs/shortcuts.md` — human-readable reference for all shortcuts, directives, workflow keywords, and entry skills

**SessionStart hook research and decision:**
- Researched SessionStart hook for auto-status on session start
- Found [#10373](https://github.com/anthropics/claude-code/issues/10373): SessionStart output discarded for new sessions, only works after `/clear`
- Decision: Drop SessionStart hook — broken for primary use case (`claude` restart). `@agents/session.md` already loaded via CLAUDE.md provides task context
- Dropped AskUserQuestion-after-STATUS idea — only useful with autostart, harmful when session clear needed

## Pending Tasks

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

**SessionStart hook broken ([#10373](https://github.com/anthropics/claude-code/issues/10373)):**
- Output discarded for new sessions (`claude` command)
- Only works after `/clear`, `/compact`, or `--resume`
- Don't build features depending on SessionStart until fixed upstream

**Learnings file at 161/80 lines** — needs `/remember` consolidation urgently.

## Next Steps

Run `/remember` to consolidate learnings before next session.

---
*Handoff by Sonnet. Help shortcut and shortcut docs added.*
