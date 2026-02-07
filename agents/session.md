# Session: Worktree — Plugin migration design

**Status:** Plugin name chosen (`edify`). Design document next.

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

**Naming:**
- Plugin name chosen: **`edify`** — Latin *aedificare* = "to build" + "to instruct"
- 11 rounds, 70+ candidates evaluated across 4 Opus brainstorm sessions
- Key concepts: prose, iterative expansion with corrective feedback, construction, continuous memory
- Marketplace research: official plugins use kebab-case compounds; our plugin is methodology (product-like naming)
- Runner-up `rubric` (13/15) killed by Rubric Labs collision in AI space
- Full research: `plans/plugin-migration/reports/naming-research.md`

## Pending Tasks

- [ ] **Generate design document** — `/design` Phase C: expand outline to full `plans/plugin-migration/design.md`
- [ ] **Plan plugin migration** — `/plan-adhoc plans/plugin-migration/design.md` after design complete

## Blockers / Gotchas

**Platform gaps:**
- Plugins cannot contribute to CLAUDE.md always-loaded context — fragments require migration command + `@` references
- No PostUpgrade hook — UserPromptSubmit version check is workaround
- SessionStart hook output discarded for new sessions (known limitation)

## Reference Files

- **plans/plugin-migration/outline.md** — Reviewed outline with requirements and validation
- **plans/plugin-migration/reports/outline-review.md** — Opus review report (4 major, 8 minor fixes)
- **plans/plugin-migration/reports/naming-research.md** — Full naming research with decision
- **tmp/marketplace-naming-research.md** — Plugin ecosystem naming patterns
- **.claude/settings.json** — Current hook/plugin configuration
