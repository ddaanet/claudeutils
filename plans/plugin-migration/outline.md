# Plugin Migration — Outline

**Requirements source:** Design conversation (no formal requirements.md)

## Problem

agent-core distributes skills, agents, and hooks to projects via git submodule + symlinks.
Pain: `just sync-to-parent` ceremony, symlink breakage in worktrees, redirect hook overhead, non-trivial adoption for new projects.

Current state: 16 skill symlinks, 12 agent symlinks, 4 hook symlinks in `.claude/` pointing to `../../agent-core/`. Each `just sync-to-parent` run recreates these after any structural change. Worktree creation requires `--reference` and submodule init ceremony.

**Note:** Some agent-core agents are missing from sync-to-parent (e.g., `remember-task.md`, `memory-refactor.md`) — omission, not intentional exclusion. Plugin auto-discovery eliminates this class of bug.

## Approach

Convert agent-core into a dual-purpose package:
- **Plugin** for skills/agents/hooks (auto-discovered, no symlinks)
- **Submodule** for fragments/bin/templates (unchanged for dev, copied for consumers)

Two installation modes:
- **Dev mode:** Submodule + `--plugin-dir ./agent-core` (instant edit feedback)
- **Consumer mode:** Plugin install from marketplace (managed fragments via migration command)

## Key Decisions

- **Plugin name:** Meaningful name (TBD — not `ac`). Skill trigger words in descriptions handle discoverability. UserPromptSubmit hook maps shortcut commands (e.g., `ci` → `/plugin:commit`), same as current shortcuts pattern
- **Fragment distribution:** Migration command copies fragments to project tree; CLAUDE.md `@` references point to local copies
- **Version sync:** UserPromptSubmit hook checks fragment version on first prompt, warns on mismatch
- **Launch wrapper:** `just claude` recipe passes `--plugin-dir ./agent-core`; `just claude0` for empty system prompt
- **Justfile modularization:** Portable recipes (claude, wt-*, precommit-base) in agent-core importable justfile; project justfile imports and adds language-specific recipes
- **Hook migration:** ALL hooks move to plugin — `pretooluse-block-tmp.sh` (sandbox smoothing), `submodule-safety.py`, `userpromptsubmit-shortcuts.py`, `pretooluse-symlink-redirect.sh` (deleted). The `/tmp` blocking is part of the agent-core package, not project-specific policy
- **Symlink-redirect hook:** Delete (purpose eliminated)
- **Plan-specific agents coexistence:** Generated `*-task.md` agents (from `prepare-runbook.py`) stay in `.claude/agents/` as regular files; they coexist with plugin-provided agents via different discovery paths

## Requirements

- FR-1: Skills, agents, and hooks load via plugin auto-discovery (no symlinks)
- FR-2: `just claude` and `just claude0` launch with `--plugin-dir ./agent-core`
- FR-3: `/ac:init` scaffolds CLAUDE.md + fragments for new projects (idempotent)
- FR-4: `/ac:update` syncs fragments when plugin version changes
- FR-5: UserPromptSubmit hook detects stale fragments, warns via additionalContext
- FR-6: Portable justfile recipes (claude, wt-*, precommit-base) importable by any project
- FR-7: Existing projects migrate by removing symlinks (no other structural changes)
- FR-8: Plan-specific agents (`*-task.md`) coexist with plugin-provided agents
- FR-9: All hooks migrate to plugin; settings.json hooks section emptied
- NFR-1: Dev mode edit→restart cycle no slower than current symlink approach
- NFR-2: No token overhead increase from plugin vs symlink loading

## Validation

| Requirement | Validation |
|-------------|------------|
| FR-1 | `claude --plugin-dir ./agent-core` → `/help` lists plugin skills; agents appear in Task tool |
| FR-2 | `just claude` and `just claude0` launch correctly, skills available |
| FR-3 | Clean project + `/ac:init` → functional CLAUDE.md with `@` refs, fragments copied |
| FR-4 | Bump `.version`, restart → `/ac:update` copies new fragments, `.ac-version` matches |
| FR-5 | Stale `.ac-version` → first prompt shows additionalContext warning |
| FR-6 | New project with `import 'agent-core/just/portable.just'` → `just claude`, `just wt-new` work |
| FR-7 | Remove symlinks from `.claude/` → all functionality preserved via plugin |
| FR-8 | Plugin agents and `*-task.md` agents both discoverable, no conflicts |
| FR-9 | All hooks fire from plugin; settings.json hooks section empty; `pretooluse-block-tmp.sh` still blocks `/tmp` writes |
| NFR-1 | Edit skill → restart → change visible (same cycle as symlinks) |
| NFR-2 | Compare context size before/after migration (no regression) |

## Components

### 1. Plugin Manifest
- `agent-core/.claude-plugin/plugin.json` with name `ac` (required location per Claude Code plugin spec)
- Existing `skills/`, `agents/` directories already in correct layout for plugin discovery
- Hook definitions embedded in `plugin.json` (see Component 2)

### 2. Hook Migration
- Move agent-core hook definitions into `plugin.json` hooks section
- Paths use `$CLAUDE_PLUGIN_ROOT` for plugin-owned scripts (e.g., `submodule-safety.py`, `userpromptsubmit-shortcuts.py`)
- **All hooks move to plugin:**
  - `pretooluse-block-tmp.sh` (PreToolUse Write|Edit) — sandbox `/tmp` blocking
  - `submodule-safety.py` (Pre/PostToolUse Bash) — cwd enforcement
  - `userpromptsubmit-shortcuts.py` (UserPromptSubmit) — shortcut expansion
  - **Deleted:** `pretooluse-symlink-redirect.sh` (purpose eliminated)
- Remove ALL hook entries from settings.json (hooks section becomes empty or removed)
- `$CLAUDE_PLUGIN_ROOT` confirmed available (used by plugin-dev and other official plugins)

### 3. Fragment Versioning System
- `agent-core/.version` — source version marker (bumped on fragment changes)
- Migration command writes `.ac-version` in project root alongside copied fragments
- UserPromptSubmit hook (Component 7): compares project `.ac-version` against plugin `agent-core/.version`, injects warning via `additionalContext` on mismatch
- `/ac:update` skill to re-sync fragments (copies updated fragments, bumps `.ac-version`)

### 4. Migration Command (`/ac:init`)
- Analyze existing CLAUDE.md for redundant rules
- Copy fragments to project tree at `agents/rules/` (behavioral rule files)
- Edit CLAUDE.md: add `@` references for session.md, learnings.md, ambient rules
- Scaffold agents/session.md, agents/learnings.md, agents/jobs.md if missing
- Write `.ac-version` marker
- Detect submodule vs consumer install, adapt paths accordingly
- **Idempotency:** Must be safe to re-run — never destroy existing CLAUDE.md content. Detect existing state, apply only missing pieces. `/ac:update` is an alias for re-running init

### 5. Justfile Modularization
- Extract portable recipes into `agent-core/just/portable.just`:
  - `claude` — `claude --plugin-dir ./agent-core` (primary dev workflow)
  - `claude0` — `claude --plugin-dir ./agent-core` with empty system prompt (primary clean-slate workflow)
  - `wt-new`, `wt-ls`, `wt-rm`, `wt-merge` — worktree recipes
  - `precommit-base` — agent-core validators (validate-tasks, validate-learnings, etc.)
  - Bash prolog (shared helper functions)
- Project justfile: `import 'agent-core/just/portable.just'` + language-specific recipes (test, lint, format, release)
- Consumer projects get portable recipes via import without copy-paste

### 6. Symlink Cleanup
- Remove all symlinks from `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`
- Preserve non-symlink files in `.claude/agents/` (plan-specific `*-task.md` agents generated by `prepare-runbook.py`)
- Remove `just sync-to-parent` recipe from agent-core justfile
- Update documentation (claude-config-layout.md, sandbox-exemptions.md sync-to-parent references)

### 7. Post-Upgrade Version Check
- No native plugin PostUpgrade hook exists (R-5)
- UserPromptSubmit hook handles this: check project `.ac-version` vs plugin `agent-core/.version` on each session's first prompt
- On mismatch: inject `additionalContext` with "Fragments outdated. Run `/ac:update`."
- State tracking: temp file or env var to fire only once per session
- Cross-reference: Version file defined in Component 3

### 8. Script Path Updates
- `agent-core/bin/` scripts (e.g., `prepare-runbook.py`, `batch-edit.py`) are referenced by absolute or relative path in skills, agents, and settings.json
- In dev mode (submodule): paths unchanged (`agent-core/bin/...`)
- In consumer mode (marketplace plugin): paths must resolve via `$CLAUDE_PLUGIN_ROOT/bin/...` or be wrapped in plugin skills
- **TODO:** Audit all `agent-core/bin/` references in skills and settings.json for path portability

## Scope

**In:**
- Plugin manifest and structure
- Hook migration to plugin.json (all hooks)
- Fragment copy + version sync mechanism
- Migration command (`/ac:init`)
- Justfile modularization
- Symlink removal
- Documentation updates
- Script path portability audit

**Out:**
- Fragment content changes (behavioral rules stay as-is)
- Workflow skill redesign
- Marketplace publishing (future)
- Breaking changes to skill interfaces
- New hook logic (existing hooks migrate as-is)

## Implementation Order

Suggested dependency-aware ordering:
1. **Plugin Manifest** (Component 1) — foundation; enables all other components
2. **Hook Migration** (Component 2) — moves hooks into plugin.json, depends on manifest
3. **Fragment Versioning** (Component 3) — version infrastructure for init/update
4. **Migration Command** (Component 4) — depends on versioning system
5. **Justfile Modularization** (Component 5) — independent; can parallel with 3-4
6. **Symlink Cleanup** (Component 6) — depends on 1+2 being verified working
7. **Post-Upgrade Version Check** (Component 7) — depends on 3
8. **Script Path Updates** (Component 8) — can parallel after manifest exists

## Rollback Strategy

- Each component is independently revertible via git
- Symlink cleanup (Component 6) is the point of no return for the old workflow — execute last after all other components are verified
- If plugin discovery fails: re-run `just sync-to-parent` to restore symlinks (recipe removed only in Component 6)
- Fragment copies are additive (don't delete submodule originals until consumer mode is validated)

## Open Questions

- **Plugin name:** Opus brainstorm top 3: `steward` (manages quality, enforces discipline), `rigging` (control infrastructure), `forge` (raw → refined). User to decide.
- **Settings.json residual:** With hooks moved to plugin, settings.json retains: permissions (allow/deny), sandbox config (including `prepare-runbook.py` exemption for `.claude/` writes), plansDirectory, attribution. File stays, hooks section removed.

### Resolved

- ~~Fragment directory name~~ → `agents/rules/` (Opus brainstorm: clear, short, unambiguous)
- ~~Init idempotency~~ → Idempotent always, `/ac:update` is alias for re-run
- ~~Bash prolog~~ → Imported via justfile `import`
- ~~Hook ownership~~ → All hooks are portable, all move to plugin
- ~~`$CLAUDE_PLUGIN_ROOT`~~ → Confirmed available (official plugins use it)
- ~~Agent namespace collision~~ → Plugin agents are prefixed (`plugin:agent-name`), no collision with local `*-task.md` files
