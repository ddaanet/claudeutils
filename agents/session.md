# Session Handoff: 2026-01-31

**Status:** Workflow controls runbook prepared (artifacts created). Sandbox exemption fragment validated with upstream issue links. Ready for orchestration.

## Completed This Session

**Workflow controls runbook — `plans/workflow-controls/runbook.md`:**
- 7-step runbook: hook script, fragment rewrite, 4 skill updates, settings registration
- Sonnet vet review: all critical/major fixes applied
- Artifacts created via `prepare-runbook.py`: agent, 7 step files, orchestrator plan

**Sandbox exemption RCA — `agent-core/fragments/sandbox-exemptions.md`:**
- Deviation: sonnet used `python3` prefix on exempt command, breaking `permissions.allow` match
- Deep investigation via claude-code-guide + web search revealed `excludedCommands` is buggy upstream
- Validated model: `permissions.allow` (no prompt) + `dangerouslyDisableSandbox` (reliable bypass) is the correct combo
- Fragment now documents the two-layer model with links to 3 upstream issues (#10767, #14162, #19135)
- Learning updated in `agents/learnings.md`

**Workflow skill updates (pending task recorded):**
- Post-commit STATUS display should pbcopy next command for clipboard paste
- "pending + apply now" shortcut concept identified for future skill

## Pending Tasks

- [ ] **Execute workflow controls runbook** — `/orchestrate workflow-controls` | sonnet | restart
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Create /reflect skill** — deviation detection → RCA → fix → handoff/commit automation. Load plugin-dev skills first. Name TBD: /reflect, /autocorrect, or other | opus
- [ ] **Insert skill loading in design docs** — design skill should load relevant plugin-dev skills when topic involves hooks/agents/skills | sonnet
- [ ] **Update workflow skills: pbcopy next command** — commit/handoff STATUS display copies next command to clipboard | sonnet
- [ ] **Add "go read the docs" checkpoints** — partially addressed by design-work.md rule | sonnet
- [ ] **Design runbook identifier solution** — `/design plans/runbook-identifiers/problem.md` | opus
- [ ] **Create design-vet-agent** — dedicated opus agent for design review, artifact-return pattern | opus
- [ ] **Add execution metadata to step files** — step files declare dependencies and execution mode | sonnet
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases in orchestrate skill | sonnet

## Blockers / Gotchas

**Hook changes require session restart:**
- UserPromptSubmit hook (Step 7 of runbook) won't activate until Claude Code restarts
- Test all shortcuts after restart: `s`, `x`, `xc`, `r`, `h`, `hc`, `ci`, `d:`, `p:`

**UserPromptSubmit hook input field name unverified:**
- Design doc says `prompt`, hook-dev skill docs say `user_prompt`
- Runbook currently uses `prompt` (from design) — may need correction during execution
- Verify by testing hook after implementation or checking Claude Code source

**excludedCommands upstream bugs may get fixed:**
- Track issues #10767, #14162, #19135 — if resolved, `excludedCommands` becomes reliable again
- Links in `agent-core/fragments/sandbox-exemptions.md` for easy checking

## Next Steps

Restart session, switch to sonnet, paste `/orchestrate workflow-controls` from clipboard.

---
*Handoff by Opus. Sandbox RCA validated, runbook artifacts prepared, ready for orchestration.*
