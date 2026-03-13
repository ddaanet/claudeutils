# Plugin Migration — Runbook Outline

**Design source:** `plans/plugin-migration/outline.md` (proofed, authoritative — supersedes design.md)
**Recall artifact:** `plans/plugin-migration/recall-artifact.md`

## Requirements Mapping

| Requirement | Phase | Item(s) |
|-------------|-------|---------|
| FR-1 (plugin auto-discovery) | 1 | 1.1, 1.2 |
| FR-2 (just claude launcher) | 4 | 4.1 |
| FR-3 (/edify:init scaffolding) | 3 | 3.1 |
| FR-4 (/edify:update sync) | 3 | 3.2 |
| FR-5 (stale version nag) | 2 | 2.3 |
| FR-6 (portable justfile) | 4 | 4.2 |
| FR-7 (symlink removal migration) | 6 | 6.1 |
| FR-8 (plan-specific agent coexistence) | 1 | 1.2 (verified during plugin validation) |
| FR-9 (hooks migrate to plugin) | 2 | 2.1, 2.2 |
| FR-10 (version provenance) | 2 | 2.3 |
| FR-11 (edify CLI install) | 2 | 2.3 |
| FR-12 (version consistency check) | 5 | 5.2 |
| NFR-1 (dev mode cycle time) | 1 | 1.3 (validation) |
| NFR-2 (no token overhead) | 6 | 6.2 (validation) |

## Key Decisions Reference

- D-1 (naming): outline.md §Key Decisions
- D-2 (hook scripts unchanged): outline.md §Component 2, hook script changes table
- D-3 (fragment distribution via skill): outline.md §Component 4
- D-4 (hooks.json wrapper format): outline.md §Key Decisions, Design Corrections §1
- D-5 (justfile modularization): outline.md §Key Decisions, §Component 5
- D-6 (version marker .edify.yaml): outline.md §Key Decisions
- D-7 (python deps in scope): outline.md §Key Decisions

## Expansion Guidance

- Phase 2 hook migration: outline Component 2 has complete hook inventory table and script-change table — use literally, do not re-audit
- Phase 2 edify-setup.sh: consolidated setup hook is new code with env var export, venv install, version comparison — needs careful specification
- Phase 3 skills are agentic prose artifacts — opus model, prose review cycles
- Phase 6 symlink cleanup: mechanical but must preserve handoff-cli-tool-*.md regular files
- Bootstrap constraint throughout: agent-core/ must remain functional, plugin verified before symlink removal

---

### Phase 1: Plugin manifest and structure (type: general)

Create the plugin structure inside existing `agent-core/` directory.

- Step 1.1: Create `.claude-plugin/plugin.json`
  - Name: `edify`, version matching `pyproject.toml` current version
  - Target: `agent-core/.claude-plugin/plugin.json`
  - Verify: `cat agent-core/.claude-plugin/plugin.json` shows valid JSON with name and version
  - Files: `agent-core/.claude-plugin/plugin.json` (create), `pyproject.toml` (read for version)

- Step 1.2: Create plugin `hooks/hooks.json` in wrapper format
  - Migrate all hook definitions from `.claude/settings.json` hooks section into `agent-core/hooks/hooks.json`
  - Wrapper format: `{"hooks": {"PreToolUse": [...], ...}}` per D-4
  - All commands use `$CLAUDE_PLUGIN_ROOT/hooks/` prefix (not `$CLAUDE_PROJECT_DIR`)
  - Omit `pretooluse-symlink-redirect.sh` (deleted in Phase 2)
  - Verify: JSON validates, all 9 surviving hooks present with correct matchers
  - Files: `agent-core/hooks/hooks.json` (rewrite from current subset), `.claude/settings.json` (read for current bindings)

- Step 1.3: Validate plugin loading
  - Test with `claude --plugin-dir ./agent-core` that skills/agents/hooks are discoverable
  - Verify FR-1 (auto-discovery), FR-8 (plan-specific agent coexistence), NFR-1 (dev mode cycle)
  - This is a manual validation checkpoint — STOP and report results before proceeding

### Phase 2: Hook migration and setup hook (type: general)

Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage.

- Step 2.1: Audit hook scripts for env var usage
  - Scripts needing audit (from outline Component 2 table): `pretooluse-recipe-redirect.py`, `pretooluse-recall-check.py`, `sessionstart-health.sh`, `stop-health-fallback.sh`
  - Check each for `$CLAUDE_PROJECT_DIR` usage — must resolve correctly under plugin context
  - Check for hardcoded `agent-core/` paths that need `$CLAUDE_PLUGIN_ROOT` substitution
  - Record findings per script: no-change-needed or specific edits required
  - Files: 4 scripts in `agent-core/hooks/`

- Step 2.2: Apply hook script fixes from audit
  - Apply any env var fixes identified in Step 2.1
  - Delete `pretooluse-symlink-redirect.sh` (purpose eliminated by plugin migration)
  - Verify remaining scripts have no relative path references (recall: hook commands must use absolute paths)
  - Files: affected scripts from audit + `agent-core/hooks/pretooluse-symlink-redirect.sh` (delete)
  - Depends on: Step 2.1

- Step 2.3: Create consolidated `edify-setup.sh`
  - New file: `agent-core/hooks/edify-setup.sh`
  - Handles (per outline Component 2):
    - Export `EDIFY_PLUGIN_ROOT` via `$CLAUDE_ENV_FILE` (grounded: official mechanism)
    - `uv pip install edify==X.Y.Z` into `$CLAUDE_PLUGIN_ROOT/.venv` (FR-11) — with `uv` availability check, pip fallback (R-3)
    - Write current plugin version to `.edify.yaml` (FR-10)
    - Compare `.edify.yaml` version against plugin version, nag if stale (FR-5)
  - UPS fallback: transcript scraping for setup marker (if SessionStart discarded — recall: #10373)
  - Script must be idempotent
  - Verify: script runs without error, `.edify.yaml` updated, env var available in subsequent commands
  - Files: `agent-core/hooks/edify-setup.sh` (create)

- Step 2.4: Wire setup hook into hooks.json
  - Add SessionStart entry for `edify-setup.sh` in `agent-core/hooks/hooks.json`
  - Ensure it runs before `sessionstart-health.sh` (setup provides env vars health check may need)
  - Verify: restart session → setup hook fires → env vars available
  - Files: `agent-core/hooks/hooks.json` (edit)
  - Depends on: Steps 2.2, 2.3

### Phase 3: Migration skills (type: general, model: opus)

Create `/edify:init` and `/edify:update` skills — agentic prose artifacts requiring opus.

- Step 3.1: Create `/edify:init` skill
  - New skill at `agent-core/skills/init/SKILL.md`
  - Behavior (from outline Component 4):
    - Consumer mode only (marketplace install)
    - Copy fragments to `agents/rules/`
    - Rewrite CLAUDE.md `@` refs to local copies
    - Scaffold `agents/` structure (session.md, learnings.md, jobs.md)
    - CLAUDE.md from `templates/CLAUDE.template.md`
    - Write `.edify.yaml` with version + sync policy (nag default)
    - Idempotent: check before acting, never destroy existing content
  - Need to create template: `agent-core/templates/CLAUDE.template.md`
  - Files: `agent-core/skills/init/SKILL.md` (create), `agent-core/templates/CLAUDE.template.md` (create)

- Step 3.2: Create `/edify:update` skill
  - New skill at `agent-core/skills/update/SKILL.md`
  - Behavior: sync fragments + `portable.just`, update `.edify.yaml` version
  - Separate from init — update is sync-only, not scaffolding
  - Files: `agent-core/skills/update/SKILL.md` (create)

### Phase 4: Justfile modularization (type: general)

Extract portable recipes and create launch wrapper.

- Step 4.1: Create `just claude` launch wrapper
  - Add `claude` and `claude0` recipes to portable justfile
  - Opinionated launch: system prompt replacement, plugin config
  - FR-2 validation: `just claude` launches with system prompt, skills available
  - Files: portable justfile (create/edit)

- Step 4.2: Create `portable.just`
  - Extract portable recipe stack from current `justfile` (per D-5 list):
    - `claude` / `claude0` — launch wrapper
    - `lint` / `format` / `check` — ruff, mypy, docformatter
    - `red` — permissive TDD variant
    - `precommit` — full lint with complexity
    - `precommit-base` — edify-plugin validators only
    - `test` — pytest with framework flags
  - Do NOT include `wt-*` recipes (manual fallbacks, stay in project justfile)
  - Do NOT include `release` (project-specific)
  - Target: `agent-core/portable.just`
  - Verify: new project with `import 'portable.just'` + `set allow-duplicate-recipes` → recipes work
  - Files: `agent-core/portable.just` (create), `justfile` (edit — add import, keep project-specific recipes)

### Phase 5: Version coordination and precommit (type: general)

Wire version consistency and release coordination.

- Step 5.1: Create `.edify.yaml` schema and initial file
  - YAML format with: `version`, `sync_policy` (default: nag)
  - Initial version from current `pyproject.toml`
  - Target: `.edify.yaml` in project root (for this project as dogfood)
  - Files: `.edify.yaml` (create)

- Step 5.2: Add version consistency precommit check (FR-12)
  - Check: `plugin.json` version == `pyproject.toml` version
  - Add to `just precommit` or as standalone check script
  - Wire into `just release` to bump both together
  - Files: precommit script or justfile recipe (create/edit), `justfile` (edit for release)

### Phase 6: Symlink cleanup and settings migration (type: general)

Execute LAST — only after plugin verified working. Irreversible within session.

- Step 6.1: Remove symlinks and clean settings.json
  - Remove 33 skill symlinks from `.claude/skills/`
  - Remove 13 agent symlinks from `.claude/agents/` (PRESERVE 6 `handoff-cli-tool-*.md` regular files)
  - Remove 4 hook symlinks from `.claude/hooks/`
  - Remove ALL hook entries from `.claude/settings.json` hooks section
  - Remove `sync-to-parent` recipe from justfile
  - Update `.gitignore` if needed
  - Verify: `claude --plugin-dir ./agent-core` still discovers all skills/agents/hooks
  - Files: `.claude/skills/*` (delete symlinks), `.claude/agents/*` (delete symlinks only), `.claude/hooks/*` (delete symlinks), `.claude/settings.json` (edit), `justfile` (edit)

- Step 6.2: Validate migration completeness
  - FR-1: plugin auto-discovery works without symlinks
  - FR-7: all functionality preserved
  - FR-9: all hooks fire from plugin, settings.json hooks empty
  - NFR-2: context size comparison (no regression)
  - Run `just precommit` — full validation gate
  - STOP and report results

### Phase 7: Script path updates and documentation (type: inline)

Mechanical path updates and doc cleanup. All decisions pre-resolved, no feedback loop needed.

- `settings.json` `permissions.allow`: update `agent-core/bin/` references
  - `agent-core/bin/prepare-runbook.py` → keep (rename happens later)
  - `agent-core/bin/recall-*` → keep (rename happens later)
  - `agent-core/bin/validate-memory-index.py` → keep
  - `agent-core/bin/learning-ages.py` → keep
  - `agent-core/bin/triage-feedback.sh` → keep
  - `agent-core/bin/magic-query-log` → keep
  - Note: actual `agent-core/` → `edify-plugin/` rename is cosmetic last step, not in this runbook
- `settings.json` `sandbox.excludedCommands`: update `agent-core/bin/prepare-runbook.py`
- `fragments/project-tooling.md`: remove `sync-to-parent` references
- `fragments/claude-config-layout.md`: remove symlink section
- `fragments/sandbox-exemptions.md`: remove `sync-to-parent` subsection
- `fragments/delegation.md`: update examples referencing `sync-to-parent`
- Remove deny rules from `settings.json` that guard symlink targets:
  - `Write(.claude/skills/*)`, `Write(.claude/agents/*)`, `Write(.claude/hooks/*)` — no longer symlinks
  - `Bash(ln:*)` — symlink creation no longer needed

| Fragment | Change | Rationale |
|----------|--------|-----------|
| `project-tooling.md` | Remove `sync-to-parent` references | Recipe deleted in Phase 6 |
| `claude-config-layout.md` | Remove symlink section | No more symlinks |
| `sandbox-exemptions.md` | Remove `sync-to-parent` subsection | Recipe deleted |
| `delegation.md` | Update `sync-to-parent` examples | Reference obsolete |

---

## Phase Dependencies

```
Phase 1 (manifest) → Phase 2 (hooks) → Phase 6 (cleanup)
Phase 3 (skills) — independent after Phase 1
Phase 4 (justfile) — independent after Phase 1
Phase 5 (versioning) — depends on Phase 1 (plugin.json exists)
Phase 6 (cleanup) — depends on Phases 1, 2 (plugin verified)
Phase 7 (docs) — depends on Phase 6 (symlinks removed)
```

Parallelizable after Phase 1: Phases 2, 3, 4, 5 are independent.

## Complexity Per Phase

| Phase | Items | Complexity | Model |
|-------|-------|------------|-------|
| 1: Plugin manifest | 3 | Medium (new structure + validation) | Sonnet |
| 2: Hook migration | 4 | High (audit + new setup hook) | Sonnet (2.3 may need opus for setup script design) |
| 3: Migration skills | 2 | High (agentic prose) | Opus |
| 4: Justfile modularization | 2 | Medium (extraction + refactor) | Sonnet |
| 5: Version coordination | 2 | Low-Medium (wiring) | Sonnet |
| 6: Symlink cleanup | 2 | Medium (careful deletion + validation) | Sonnet |
| 7: Docs and paths | inline | Low (mechanical) | Sonnet |
