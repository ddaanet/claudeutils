# Session: Worktree — Plugin migration design

**Status:** Outline complete, pending user approval on plugin name. Design document next.

## Completed This Session

**Evaluation & Research:**
- Audited current symlink setup: 16 skills, 12+ agents, 4 hooks symlinked via `just sync-to-parent`
- Evaluated plugin capabilities: skills/agents/hooks → auto-discovery ✓, fragments → no plugin equivalent ✗
- Researched plugin dev story: `--plugin-dir` gives live editing, marketplace install uses content-addressed cache
- Confirmed `$CLAUDE_PLUGIN_ROOT` available (official plugins use it)
- Identified platform gap: plugins cannot inject CLAUDE.md context

**Outline:**
- Produced `plans/plugin-migration/outline.md` with 8 components, requirements (FR-1–FR-9, NFR-1/2), validation table
- Opus outline-review-agent reviewed: 4 major + 8 minor issues found and fixed
- Added implementation order, rollback strategy, scope boundaries

**Resolved decisions:**
- Fragment directory: `agents/rules/` (Opus brainstorm — clear, short, unambiguous)
- Hook ownership: ALL hooks move to plugin (including `/tmp` blocking — it's part of the package)
- Init idempotency: Always idempotent, never destroy CLAUDE.md
- Bash prolog: Imported via justfile `import`
- Agent namespace: Plugin agents prefixed, no collision with local `*-task.md`
- Settings.json residual: Keeps permissions/sandbox config, hooks section removed

**Naming research:**
- 7 rounds of Opus brainstorming, 60+ candidates evaluated
- Research persisted to `plans/plugin-migration/reports/naming-research.md`
- Frontrunners: `tenet` (opinionated beliefs), `lathe` (production system), `rebar` (structural reinforcement)
- Identity dimensions: opinionated, automated production, corrective feedback, quality at cost, institutional memory
- No name chosen yet — user wants more iteration

## Pending Tasks

- [ ] **Choose plugin name** — Continue brainstorming with constraints in `plans/plugin-migration/reports/naming-research.md`
- [ ] **Generate design document** — `/design` Phase C: expand outline to full `plans/plugin-migration/design.md`
- [ ] **Plan plugin migration** — `/plan-adhoc plans/plugin-migration/design.md` after design complete

## Blockers / Gotchas

**Plugin name undecided:** Blocks design.md finalization (name appears throughout). Can start design with placeholder.

**Platform gaps:**
- Plugins cannot contribute to CLAUDE.md always-loaded context — fragments require migration command + `@` references
- No PostUpgrade hook — UserPromptSubmit version check is workaround
- SessionStart hook output discarded for new sessions (known limitation)

## Reference Files

- **plans/plugin-migration/outline.md** — Reviewed outline with requirements and validation
- **plans/plugin-migration/reports/outline-review.md** — Opus review report (4 major, 8 minor fixes)
- **plans/plugin-migration/reports/naming-research.md** — Full naming constraints, rejected names, scoring matrix
- **.claude/settings.json** — Current hook/plugin configuration
