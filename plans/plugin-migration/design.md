# Plugin Migration — Design

## Problem

agent-core distributes skills, agents, and hooks to projects via git submodule + symlinks (`just sync-to-parent`). This causes:

- **Ceremony:** Every structural change requires `just sync-to-parent` + restart
- **Fragility:** Symlink breakage in worktrees, missed agents in sync recipe (e.g., `remember-task.md`, `memory-refactor.md`)
- **Adoption friction:** New projects must set up submodule + run sync + configure settings.json hooks
- **Hook indirection:** settings.json → symlink → agent-core/hooks (two redirects)

Claude Code plugins solve all of these via auto-discovery of skills/agents and native hook registration.

## Requirements

**Source:** `plans/plugin-migration/outline.md` + design conversation

**Naming note:** The outline uses pre-decision naming (`/ac:init`, `.ac-version`). This design supersedes those with the chosen plugin name: `/edify:init`, `/edify:update`, `.edify-version`. All `ac` references in the outline should be read as `edify`.

**Functional:**
- FR-1: Skills, agents, hooks load via plugin auto-discovery (no symlinks) — addressed by Components 1-2
- FR-2: `just claude` and `just claude0` launch with `--plugin-dir ./agent-core` — addressed by Component 5
- FR-3: `/edify:init` scaffolds CLAUDE.md + fragments for new projects (idempotent) — addressed by Component 4
- FR-4: `/edify:update` syncs fragments when plugin version changes — addressed by Components 3-4
- FR-5: UserPromptSubmit hook detects stale fragments, warns via additionalContext — addressed by Component 7
- FR-6: Portable justfile recipes (claude, wt-*, precommit-base) importable by any project — addressed by Component 5
- FR-7: Existing projects migrate by removing symlinks (no other structural changes) — addressed by Component 6
- FR-8: Plan-specific agents (`*-task.md`) coexist with plugin agents — addressed by Component 1 (auto-discovery vs `.claude/agents/`)
- FR-9: All hooks migrate to plugin; settings.json hooks section emptied — addressed by Component 2

**Non-functional:**
- NFR-1: Dev mode edit→restart cycle no slower than current symlink approach — addressed by `--plugin-dir` live loading
- NFR-2: No token overhead increase from plugin vs symlink loading — validated post-migration

**Out of scope:**
- Fragment content changes (behavioral rules stay as-is)
- Workflow skill redesign
- Marketplace publishing (future)
- Breaking changes to skill interfaces
- New hook logic (existing hooks migrate as-is)

## Architecture

### Dual-Purpose Package

agent-core becomes both:
1. **Plugin** — `.claude-plugin/plugin.json` enables auto-discovery of `skills/`, `agents/`, `hooks/`
2. **Submodule** — `fragments/`, `bin/`, `templates/`, `configs/` remain available via submodule path

### Installation Modes

| Mode | Plugin Loading | Fragment Access | Justfile |
|------|---------------|-----------------|----------|
| **Dev** (submodule) | `--plugin-dir ./agent-core` | `@agent-core/fragments/*.md` direct | `import 'agent-core/just/portable.just'` |
| **Consumer** (marketplace) | Plugin install | `/edify:init` copies to `agents/rules/` | Manual or template |

### Directory Layout (agent-core)

```
agent-core/
├── .claude/                # UNCHANGED: agent-core local dev config
├── .claude-plugin/
│   └── plugin.json         # NEW: Plugin manifest (name: "edify")
├── hooks/
│   ├── hooks.json          # NEW: Plugin hook configuration
│   ├── pretooluse-block-tmp.sh
│   ├── submodule-safety.py
│   ├── userpromptsubmit-shortcuts.py
│   └── userpromptsubmit-version-check.py  # NEW: Fragment staleness detector
├── skills/                 # UNCHANGED: 16 skill directories
├── agents/                 # UNCHANGED: 14 agent .md files
├── fragments/              # UNCHANGED: 20 instruction fragments
├── bin/                    # UNCHANGED: 11 utility scripts
├── just/
│   └── portable.just       # NEW: Extracted portable recipes
├── docs/                   # UNCHANGED: workflow and pattern documentation
├── scripts/                # UNCHANGED: create-plan-agent.sh, split-execution-plan.py
├── migrations/             # UNCHANGED: schema migration documentation
├── templates/              # UNCHANGED
├── configs/                # UNCHANGED
├── .version                # NEW: Fragment version marker
├── Makefile                # UNCHANGED: cache management
├── README.md               # UNCHANGED
└── justfile                # MODIFIED: sync-to-parent removed
```

**Deleted:**
- `hooks/pretooluse-symlink-redirect.sh` — purpose eliminated (no more symlinks to edit)

## Components

### 1. Plugin Manifest

**File:** `agent-core/.claude-plugin/plugin.json`

```json
{
  "name": "edify",
  "version": "1.0.0",
  "description": "Workflow infrastructure for Claude Code projects"
}
```

**Why minimal:** Auto-discovery handles skills, agents, and hooks from conventional directory locations. No custom path overrides needed — agent-core already uses the standard layout (`skills/*/SKILL.md`, `agents/*.md`, `hooks/hooks.json`).

**Coexistence with plan-specific agents:** Plugin agents are discovered from `agent-core/agents/`. Plan-specific agents (`*-task.md`) live in `.claude/agents/` as regular files. Both are visible to the Task tool. No namespace collision — plugin agents are internally qualified as `edify:agent-name`.

### 2. Hook Migration

**File:** `agent-core/hooks/hooks.json`

Plugin hooks use the wrapper format required by Claude Code:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/pretooluse-block-tmp.sh"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-shortcuts.py",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-version-check.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

**Hook script changes:**

| Script | Change Required | Rationale |
|--------|----------------|-----------|
| `pretooluse-block-tmp.sh` | **None** | No env vars used; checks file paths from stdin only |
| `submodule-safety.py` | **None** | Uses `$CLAUDE_PROJECT_DIR` correctly — it checks the *project's* cwd, not the plugin's location |
| `userpromptsubmit-shortcuts.py` | **None** | No env vars used; stateless stdin→stdout |
| `pretooluse-symlink-redirect.sh` | **Delete** | Purpose eliminated — no symlinks to protect |

**Critical insight:** The explore report incorrectly suggested replacing `$CLAUDE_PROJECT_DIR` with `$CLAUDE_PLUGIN_ROOT` in `submodule-safety.py`. This is wrong. The script needs to know the *project root* (where the user's code lives), not the *plugin root* (where edify is installed). `$CLAUDE_PROJECT_DIR` is the correct variable and remains unchanged.

**hooks.json path resolution:** `$CLAUDE_PLUGIN_ROOT` in `hooks.json` commands resolves to the plugin directory at runtime. In dev mode (`--plugin-dir ./agent-core`), it resolves to the agent-core directory. In consumer mode (marketplace install), it resolves to the cached plugin directory.

### 3. Fragment Versioning System

**Purpose:** Detect when plugin fragments are newer than project-local copies.

**Files:**
- `agent-core/.version` — source version marker (plain text, e.g., `1.0.0`)
- `<project>/.edify-version` — project's installed fragment version

**Version bump protocol:**
- Bump `agent-core/.version` whenever fragments change
- Semantic: major = breaking CLAUDE.md structure, minor = new fragment, patch = fragment content fix

**Comparison logic (in version-check hook):**
- Read `$CLAUDE_PROJECT_DIR/.edify-version`
- Read `$CLAUDE_PLUGIN_ROOT/.version`
- If mismatch: inject additionalContext warning
- If `.edify-version` missing: no warning (project may not use managed fragments)

### 4. Migration Command (`/edify:init`)

**Type:** Skill (not command) — needs access to reasoning, file operations, and conditional logic.

**Location:** `agent-core/skills/init/SKILL.md`

**Behavior:**

1. **Detect installation mode:**
   - Submodule: `agent-core/` exists as directory → dev mode (fragment `@` refs point to `agent-core/fragments/`)
   - Plugin only: no `agent-core/` → consumer mode (copy fragments to `agents/rules/`)

2. **Scaffold structure:**
   - Create `agents/` directory if missing
   - Create `agents/session.md` from template if missing
   - Create `agents/learnings.md` from template if missing
   - Create `agents/jobs.md` from template if missing

3. **Fragment handling (consumer mode only):**
   - Copy fragments from plugin to `agents/rules/`
   - Rewrite `@agent-core/fragments/` references to `@agents/rules/` in CLAUDE.md

4. **CLAUDE.md scaffolding:**
   - If no CLAUDE.md exists: copy `templates/CLAUDE.template.md`, adjust `@` references per mode
   - If CLAUDE.md exists: no modification (idempotent — don't risk destroying user content)

5. **Version marker:**
   - Write `.edify-version` with current `agent-core/.version` value

**Idempotency guarantee:** Every operation checks before acting. Re-running `/edify:init` applies only missing pieces.

**`/edify:update` skill:** Separate skill at `agent-core/skills/update/SKILL.md`. Behavior: re-copies fragments from plugin source to project target (overwriting existing), then updates `.edify-version` marker. Unlike `/edify:init`, it skips scaffolding (CLAUDE.md, session.md, etc.) and only handles fragment sync. In dev mode, this is a no-op (fragments are read directly from `agent-core/fragments/` via `@` references). In consumer mode, it copies updated fragments to `agents/rules/`.

### 5. Justfile Modularization

**New file:** `agent-core/just/portable.just`

**Extracted recipes (portable, no Python dependency):**

| Recipe | Purpose | Notes |
|--------|---------|-------|
| `claude` | `claude --plugin-dir ./agent-core` | Primary dev workflow |
| `claude0` | `claude --plugin-dir ./agent-core --system-prompt ""` | Clean-slate workflow |
| `wt-new name base="HEAD"` | Create worktree | Submodule-aware, `--reference` pattern |
| `wt-ls` | List worktrees | Delegates to `git worktree list` |
| `wt-rm name` | Remove worktree | Force-remove for submodules |
| `wt-merge name` | Merge worktree | Auto-resolves session.md conflicts |
| `precommit-base` | Run agent-core validators | validate-tasks, validate-learnings, validate-memory-index, etc. |

**Recipe extraction rules:**
- Portable recipes use only git + bash (no Python tools)
- `precommit-base` calls validators via relative `agent-core/bin/` paths (dev mode only; consumer mode path resolution via `$CLAUDE_PLUGIN_ROOT/bin/` is deferred per D-7)
- Bash prolog (`bash_prolog` template variable) stays in root justfile (project-specific helpers)
- `precommit-base` is a *subset* of precommit — it runs agent-core validators only. Project justfile adds language-specific checks on top.

**Project justfile consumption:**

```just
import 'agent-core/just/portable.just'

# Project-specific recipes below
test *ARGS:
    pytest {{ ARGS }}

precommit: precommit-base
    # Add language-specific checks after base validators
    ruff check
    mypy
```

**justfile `import` support:** Just supports `import` natively (since v1.19.0). Imported files can define their own variables and recipes. However, variables are NOT shared across import boundaries — `portable.just` must define its own `bash_prolog` (or equivalent helper functions) for the `wt-*` and other recipes that currently depend on the root justfile's `bash_prolog`. The portable prolog should be minimal (only `fail`, `visible`, color variables) compared to the root's full prolog (which includes `sync`, `run-checks`, `pytest-quiet`, etc.).

**Root justfile changes:**
- Remove recipes that move to `portable.just` (claude, wt-*, precommit-base subset)
- Add `import 'agent-core/just/portable.just'`
- Keep project-specific recipes (test, format, check, lint, release, line-limits)
- Keep `bash_prolog` for project-specific helper functions
- Rebuild `.cache/just-help.txt` after import change (imported recipes appear in `just --list` output, affecting CLAUDE.md `@` reference)

### 6. Symlink Cleanup

**Execution order:** Last component — only after all others verified working.

**Steps:**
1. Remove all symlinks from `.claude/skills/` (16 symlinks)
2. Remove all symlinks from `.claude/agents/` (12 symlinks, preserve `*-task.md` regular files)
3. Remove all symlinks from `.claude/hooks/` (4 symlinks)
4. Remove `pretooluse-symlink-redirect.sh` from `agent-core/hooks/` (script deleted)
5. Remove hook entries from `.claude/settings.json` (hooks section becomes `{}`)
6. Remove `sync-to-parent` recipe from `agent-core/justfile`
7. Update `.gitignore` if needed (symlink tracking no longer necessary)

**settings.json after cleanup:**

```json
{
  "permissions": { ... },
  "attribution": { ... },
  "plansDirectory": "plans/claude/",
  "sandbox": { ... }
}
```

The `hooks` key is removed entirely. All hook behavior now comes from `agent-core/hooks/hooks.json` via plugin auto-discovery.

**Validation before cleanup:**
- `claude --plugin-dir ./agent-core` → verify skills load (`/help` lists plugin skills)
- Verify agents appear in Task tool
- Verify hooks fire (test each hook event)
- Only then proceed with symlink removal

### 7. Post-Upgrade Version Check

**File:** `agent-core/hooks/userpromptsubmit-version-check.py`

**Behavior:**
- Fires on every UserPromptSubmit (no matcher — same as shortcuts hook)
- Reads `$CLAUDE_PROJECT_DIR/.edify-version` and `$CLAUDE_PLUGIN_ROOT/.version`
- On version mismatch: inject additionalContext `"⚠️ Fragments outdated (project: X, plugin: Y). Run /edify:update."`
- On match or missing `.edify-version`: silent pass-through (exit 0)
- **Once-per-session:** Use a temp file (`$CLAUDE_PROJECT_DIR/tmp/.edify-version-checked`) to fire only on first prompt. Note: Do NOT use system `/tmp/` — the `pretooluse-block-tmp.sh` hook blocks it, and the hook script itself should follow the same convention

**Design rationale:** No PostUpgrade hook exists in Claude Code. UserPromptSubmit is the earliest reliable hook point. Once-per-session gating prevents noise on subsequent prompts.

**Performance:** File existence check + two small file reads. Well under the 5s timeout.

### 8. Script Path Updates

**Audit of `agent-core/bin/` references:**

Scripts are referenced from three contexts:
1. **Skills/agents:** `agent-core/bin/prepare-runbook.py` — used in skill procedures
2. **settings.json:** `permissions.allow` pattern `Bash(agent-core/bin/prepare-runbook.py:*)`
3. **Justfile precommit:** `agent-core/bin/validate-*.py` validators

**Dev mode (submodule):** All paths remain `agent-core/bin/...` — no change needed. The submodule directory is the plugin directory.

**Consumer mode (marketplace):** Scripts are inside the plugin at `$CLAUDE_PLUGIN_ROOT/bin/...`. Skills and agents would reference `$CLAUDE_PLUGIN_ROOT/bin/` instead of `agent-core/bin/`.

**Decision:** For this migration, only dev mode paths matter. Consumer mode path resolution is deferred to marketplace publishing work. Skills can use `agent-core/bin/` paths for dev mode; consumer mode will need a path resolution layer (future work, out of scope).

**Minimal changes:**
- `permissions.allow` entry stays as `Bash(agent-core/bin/prepare-runbook.py:*)` (dev mode only)
- Validators in precommit stay as `agent-core/bin/validate-*.py`
- No script content changes needed

## Key Design Decisions

### D-1: Plugin Name → `edify`

**Rationale:** Latin *aedificare* = "to build" + "to instruct". Product-like naming (not descriptive compound). Full research in `plans/plugin-migration/reports/naming-research.md`.

### D-2: Hook Scripts Stay Unchanged (Except Deletion)

The `$CLAUDE_PROJECT_DIR` vs `$CLAUDE_PLUGIN_ROOT` distinction is critical:
- `$CLAUDE_PROJECT_DIR` = where the user's project lives (for cwd enforcement, tmp blocking)
- `$CLAUDE_PLUGIN_ROOT` = where the plugin is installed (for locating hook scripts in hooks.json)

Hook *configuration* (hooks.json) uses `$CLAUDE_PLUGIN_ROOT` to locate scripts.
Hook *scripts* use `$CLAUDE_PROJECT_DIR` when they need the project path.
These are orthogonal and both correct.

### D-3: Fragment Distribution via Skill, Not Script

`/edify:init` is a skill (SKILL.md) not a standalone script because:
- Needs conditional logic based on installation mode
- Needs to reason about existing CLAUDE.md content
- Needs idempotency guarantees that are hard to script
- Skills have access to Read/Write/Edit tools with error handling

### D-4: `hooks.json` Over Inline in `plugin.json`

Plugin hooks go in `hooks/hooks.json` (separate file) rather than inline in `plugin.json` because:
- hooks.json is auto-discovered from `hooks/` directory
- Keeps plugin.json minimal (just name + version)
- Matches the convention shown in Claude Code plugin documentation
- Easier to edit hooks independently of manifest

### D-5: Justfile `import` Over Bash Prolog for Portable Recipes

Portable recipes use Just's native `import` mechanism:
- Clean separation: portable recipes in one file, project recipes in another
- No bash prolog injection needed for shared recipes
- Project-specific helpers stay in root justfile's `bash_prolog`

### D-6: `.edify-version` Over `.ac-version`

Version marker named after plugin (`edify`) not old acronym (`ac`):
- Consistent with plugin name
- Clear provenance — "this version marker belongs to the edify plugin"
- `.edify-version` in project root (not nested in `agents/`)

### D-7: Consumer Mode Deferred

Consumer mode (marketplace install, fragment copying, path resolution) is designed but not implemented in this migration. The focus is dev mode: submodule + `--plugin-dir`. Consumer mode adds complexity (path resolution layer, fragment copying logic) that blocks the core migration without adding immediate value.

`/edify:init` skill is created with consumer mode *design* but only dev mode *implementation*. Consumer mode code paths are stubbed with clear TODO markers.

## Implementation Notes

### Affected Files (Create)

| File | Purpose |
|------|---------|
| `agent-core/.claude-plugin/plugin.json` | Plugin manifest |
| `agent-core/hooks/hooks.json` | Plugin hook configuration |
| `agent-core/hooks/userpromptsubmit-version-check.py` | Fragment version check hook |
| `agent-core/.version` | Fragment version marker |
| `agent-core/just/portable.just` | Portable justfile recipes |
| `agent-core/skills/init/SKILL.md` | `/edify:init` skill |
| `agent-core/skills/update/SKILL.md` | `/edify:update` skill |

### Affected Files (Modify)

| File | Change |
|------|--------|
| `.claude/settings.json` | Remove `hooks` section entirely |
| `agent-core/justfile` | Remove `sync-to-parent` recipe |
| Root `justfile` | Add `import`, remove migrated recipes |
| `.cache/just-help.txt` | Regenerate (imported recipes change `just --list` output) |
| `.cache/just-help-agent-core.txt` | Regenerate (sync-to-parent removed from agent-core justfile) |
| `agent-core/fragments/claude-config-layout.md` | Remove symlink section referencing `just sync-to-parent` |
| `agent-core/fragments/sandbox-exemptions.md` | Remove `just sync-to-parent` subsection |
| `agent-core/fragments/project-tooling.md` | Remove `sync-to-parent` references |
| `agent-core/fragments/delegation.md` | Update examples referencing `sync-to-parent` |

### Affected Files (Delete)

| File | Reason |
|------|--------|
| `agent-core/hooks/pretooluse-symlink-redirect.sh` | Purpose eliminated |
| `.claude/skills/*` (symlinks) | Replaced by plugin auto-discovery |
| `.claude/agents/*` (symlinks only) | Replaced by plugin auto-discovery |
| `.claude/hooks/*` (symlinks) | Replaced by plugin hooks.json |

### Testing Strategy

| Component | Test Method |
|-----------|-------------|
| Plugin manifest | `claude --plugin-dir ./agent-core` → skills appear in `/help` |
| Hook migration | Manual hook testing: trigger each hook event, verify behavior matches current |
| Version check | Create `.edify-version` with old version, verify warning on first prompt |
| Init skill | Run on clean directory, verify scaffolding; run on existing project, verify idempotency |
| Justfile import | `just claude` works, `just wt-new test` works from imported recipe |
| Symlink cleanup | Remove symlinks, verify all functionality preserved |
| Coexistence | Create plan-specific agent, verify both plugin and local agents visible |

### Rollback

Each component is independently revertible via git. Symlink cleanup (Component 6) is the point of no return for the old workflow — execute last.

If plugin discovery fails at any point before Component 6: re-run `just sync-to-parent` to restore symlinks (recipe still exists until Component 6).

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/implementation-notes.md` — @ references limitation, hook behavior patterns
- `agent-core/fragments/claude-config-layout.md` — hook configuration patterns (already loaded via CLAUDE.md)
- `agent-core/fragments/sandbox-exemptions.md` — permission patterns (already loaded via CLAUDE.md)
- `plans/plugin-migration/reports/explore-structure.md` — full agent-core directory tree
- `plans/plugin-migration/reports/explore-hooks.md` — hook script analysis
- `plans/plugin-migration/reports/explore-justfiles.md` — justfile structure analysis

**Skills to load:**
- `plugin-dev:plugin-structure` — plugin.json format, auto-discovery rules
- `plugin-dev:hook-development` — hooks.json format, event types, output format

**Additional research allowed:** Planner may query Context7 for Just `import` syntax details.

## Next Steps

1. `/plan-adhoc plans/plugin-migration/design.md` — create execution runbook
2. Load `plugin-dev:plugin-structure` and `plugin-dev:hook-development` before planning
