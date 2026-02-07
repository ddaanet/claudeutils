# Session: Worktree — Plugin migration design

**Status:** Design complete. Ready for planning.

## Completed This Session

**Evaluation & Research (prior sessions):**
- Audited current symlink setup: 16 skills, 12+ agents, 4 hooks symlinked via `just sync-to-parent`
- Evaluated plugin capabilities: skills/agents/hooks → auto-discovery ✓, fragments → no plugin equivalent ✗
- Confirmed `$CLAUDE_PLUGIN_ROOT` available (official plugins use it)
- Identified platform gap: plugins cannot inject CLAUDE.md context

**Outline (prior sessions):**
- Produced `plans/plugin-migration/outline.md` with 8 components, requirements (FR-1–FR-9, NFR-1/2), validation table
- Opus outline-review-agent reviewed: 4 major + 8 minor issues found and fixed

**Naming (prior sessions):**
- Plugin name chosen: **`edify`** — Latin *aedificare* = "to build" + "to instruct"

**Design (this session):**
- Delegated 3 quiet-explore agents in parallel: structure, hooks, justfiles
- Loaded `plugin-dev:plugin-structure` and `plugin-dev:hook-development` skills for plugin format knowledge
- Read all hook scripts — identified critical `$CLAUDE_PROJECT_DIR` vs `$CLAUDE_PLUGIN_ROOT` distinction
- Corrected explore report's incorrect recommendation to replace `$CLAUDE_PROJECT_DIR` in `submodule-safety.py`
- Produced `plans/plugin-migration/design.md`: 8 components, 7 design decisions (D-1 through D-7)
- Opus design-vet-agent reviewed: 0 critical, 6 major, 5 minor issues — all fixed
  - Key fixes: symlink/fragment count corrections, `/edify:update` skill spec, fragment doc updates in affected files, bash_prolog variable scoping across `import` boundaries, cache regeneration tracking

## Pending Tasks

- [ ] **Plan plugin migration** — `/plan-adhoc plans/plugin-migration/design.md`

## Blockers / Gotchas

**Platform gaps:**
- Plugins cannot contribute to CLAUDE.md always-loaded context — fragments require migration command + `@` references
- No PostUpgrade hook — UserPromptSubmit version check is workaround
- SessionStart hook output discarded for new sessions (known limitation)

**Design notes:**
- `$CLAUDE_PROJECT_DIR` ≠ `$CLAUDE_PLUGIN_ROOT` — hook *config* uses plugin root for script paths, hook *scripts* use project dir for project logic. Do not conflate.
- justfile `import` does NOT share variables across boundaries — `portable.just` needs its own minimal bash prolog
- Consumer mode deferred (D-7) — only dev mode (submodule + `--plugin-dir`) implemented in this migration

## Reference Files

- **plans/plugin-migration/design.md** — Full design with 8 components, 7 decisions
- **plans/plugin-migration/outline.md** — Reviewed outline with requirements and validation
- **plans/plugin-migration/reports/design-review.md** — Opus design review (6 major, 5 minor fixes applied)
- **plans/plugin-migration/reports/explore-structure.md** — Full agent-core directory tree
- **plans/plugin-migration/reports/explore-hooks.md** — Hook script analysis with migration assessment
- **plans/plugin-migration/reports/explore-justfiles.md** — Justfile structure and recipe portability analysis
- **plans/plugin-migration/reports/naming-research.md** — Full naming research with decision
