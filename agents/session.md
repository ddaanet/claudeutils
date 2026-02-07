# Session: Plugin Migration — Design Update

**Status:** Design updated. Runbook invalidated — replanning needed.

## Completed This Session

**Design update (naming + format fixes):**
- Established naming hierarchy: edify = product, edify-plugin = git repo (was agent-core), edify = marketplace plugin name
- Opus brainstormed repo names — edify-plugin ranked #1 (self-documenting, doesn't foreclose "edify-core" for Python package)
- Resolved hooks.json format conflict via claude-code-guide: `hooks/hooks.json` uses direct format (`{"PreToolUse": [...]}`), wrapper format only for inline in `plugin.json`
- Bulk renamed all `agent-core/` → `edify-plugin/` in design.md
- Added D-7: future Python package dependency (dual venv strategy, dual memory)
- Renumbered D-8: consumer mode deferred (was D-7)
- Updated D-1: full naming hierarchy table
- Updated D-4: format note clarifying direct vs wrapper hooks.json

**Previous session (planning — now invalidated):**
- 16-step runbook across 6 phases was created but references stale `agent-core/` paths
- Step files at `plans/plugin-migration/steps/step-*.md` — all need path updates
- Plan-specific agent at `.claude/agents/plugin-migration-task.md` — stale

## Pending Tasks

- [ ] **Replan plugin migration runbook** — `/plan-adhoc plans/plugin-migration/design.md` | sonnet
  - Previous runbook invalidated: agent-core → edify-plugin rename, hooks.json format change, new D-7/D-8
  - Directory rename (agent-core → edify-plugin) must be a runbook step
  - Load `plugin-dev:plugin-structure` and `plugin-dev:hook-development` before planning

## Blockers / Gotchas

**Runbook invalidation scope:**
- All 16 step files reference `agent-core/` paths — cannot just patch, need full replan
- hooks.json format changed (wrapper → direct) — affects Phase 3 steps
- New design decisions D-7 (Python dep) and D-8 (consumer mode) may affect step ordering

**hooks.json format — authoritative source:**
- `hooks/hooks.json` (standalone file) = direct format: `{"PreToolUse": [...]}`
- Inline in `plugin.json` = wrapper format: `{"name": "...", "hooks": {"PreToolUse": [...]}}`
- plugin-dev:hook-development skill is WRONG on this — use claude-code-guide as fallback

**Phase 2 skill content gaps (carried forward):**
- Steps 2.3 and 2.4 specify skill structure but lack procedural content
- Pattern reference: `/token-efficient-bash` skill shows good procedural format

## Reference Files

- **plans/plugin-migration/design.md** — Updated design with 8 components, 8 decisions (D-1 through D-8)
- **plans/plugin-migration/runbook.md** — STALE: 16-step runbook with old agent-core paths
- **plans/plugin-migration/outline.md** — Original outline (uses pre-decision naming)
- **plans/plugin-migration/reports/** — Exploration and review reports from planning
