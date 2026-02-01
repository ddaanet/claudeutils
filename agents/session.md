# Session Handoff: 2026-02-01

**Status:** Memory index location fix designed — moves from agent-core (shared) to project-level.

## Completed This Session

**Design: Memory index location fix + seeding** (`plans/remember-update/design.md`):
- Identified architectural issue: memory-index.md in agent-core (shared submodule) but catalogs project-specific learnings
- Designed move from `agent-core/fragments/memory-index.md` → `agents/memory-index.md`
- Specified seeding heuristic: index non-`@`-imported knowledge (decisions, rules, skill references)
- Vet review by opus: 3 medium fixes applied (seeding scope, path-change clarity, consumer migration status)
- Confirmed pytest-md/tuick don't import memory-index yet — no breakage from deletion
- Design routes to `/plan-adhoc` (Tier 1 or 2)

**Files changed:**
- `plans/remember-update/design.md` (new — design document)

## Pending Tasks

- [ ] **Implement memory index move** — `/plan-adhoc plans/remember-update/design.md` | sonnet
- [ ] **Run /remember** — learnings file at 180/80 lines, needs consolidation urgently | sonnet
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
- Don't build features depending on SessionStart until fixed upstream

**Learnings file at 180/80 lines** — needs `/remember` consolidation urgently.

## Next Steps

Implement memory index move: `/plan-adhoc plans/remember-update/design.md`

---
*Handoff by Opus. Memory index location fix designed and vetted.*
