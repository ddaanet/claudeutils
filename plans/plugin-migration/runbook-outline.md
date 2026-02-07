# Plugin Migration — Runbook Outline

**Purpose:** Migrate edify-plugin (was agent-core) from symlink-based distribution to Claude Code plugin architecture.

**Source:** `plans/plugin-migration/design.md`

**Status:** Outline — pending review

---

## Requirements Mapping

| Requirement | Implementation Phase | Step(s) | Notes |
|-------------|---------------------|---------|-------|
| FR-1: Plugin auto-discovery | Phase 1, Phase 2 | 1.1-1.2, 2.1-2.3 | Plugin manifest + skills/agents structure |
| FR-2: `just claude` with `--plugin-dir` | Phase 0, Phase 4 | 0.1, 4.1-4.2 | Directory rename first, then justfile updates |
| FR-3: `/edify:init` scaffolding | Phase 2 | 2.3 | Dev mode implementation, consumer mode stubbed |
| FR-4: `/edify:update` fragment sync | Phase 2 | 2.4 | Dev mode no-op, consumer mode deferred |
| FR-5: Version check via hook | Phase 3 | 3.3 | UserPromptSubmit hook with once-per-session gating |
| FR-6: Portable justfile recipes | Phase 4 | 4.1-4.2 | Extract to portable.just with minimal prolog |
| FR-7: Symlink cleanup | Phase 5 | 5.1-5.2 | Final step after all validation |
| FR-8: Plan-specific agent coexistence | Phase 2, Phase 5 | 2.1 (structure), 5.3 (validation) | Plugin vs local agents |
| FR-9: Hooks migrate to plugin | Phase 3 | 3.1-3.3 | Direct format hooks.json |
| NFR-1: Dev mode performance parity | Phase 5 | 5.3 (validation with baseline comparison) | Edit→restart cycle time |
| NFR-2: Token overhead parity | Phase 5 | 5.3 (validation with token count measurement) | Context size diff ≤ 5% |

---

## Key Design Decisions

- **D-1:** Naming hierarchy: product = edify, git repo = edify-plugin (was agent-core), marketplace plugin = edify
- **D-2:** Hook scripts unchanged (except `pretooluse-symlink-redirect.sh` deleted)
- **D-3:** Fragment distribution via skill, not script
- **D-4:** `hooks.json` separate file with direct format `{"PreToolUse": [...]}`, not inline wrapper in `plugin.json`
- **D-5:** Justfile `import` for portable recipes
- **D-6:** `.edify-version` marker in project root
- **D-7:** Future Python package dependency (dual venv strategy, dual memory)
- **D-8:** Consumer mode deferred (dev mode only in this migration)

---

## Phase Structure

### Phase 0: Directory Rename (1 step)

**Scope:** Rename agent-core directory to edify-plugin across entire project

**Dependencies:** None

**Model:** Haiku (file operations)

**Estimated Complexity:** Trivial (git mv + path updates)

**Steps:**
- 0.1: Rename `agent-core/` → `edify-plugin/` using `git mv`, update all references in root justfile, `.gitmodules`, settings.json permissions, CLAUDE.md fragments

**Rationale:** Directory rename must be a distinct runbook step (D-1). All subsequent phases reference `edify-plugin/` paths.

---

### Phase 1: Plugin Manifest (2 steps)

**Scope:** Create plugin.json and .version marker

**Dependencies:** Phase 0 (edify-plugin directory exists)

**Model:** Haiku (file creation)

**Estimated Complexity:** Trivial (~10 lines total)

**Steps:**
- 1.1: Create `edify-plugin/.claude-plugin/plugin.json` with minimal manifest (name: "edify", version: "1.0.0")
- 1.2: Create `edify-plugin/.version` marker with initial version `1.0.0`

---

### Phase 2: Skills and Agents (4 steps)

**Scope:** Create `/edify:init` and `/edify:update` skills, verify existing skills/agents structure

**Dependencies:** Phase 1 (plugin manifest)

**Model:** Sonnet (skill design requires reasoning)

**Estimated Complexity:** Moderate (~200-250 lines total; init skill primary, update skill minimal in dev mode)

**Steps:**
- 2.1: Verify `edify-plugin/agents/` contains 14 agent .md files (no moves needed for plugin discovery)
- 2.2: Verify `edify-plugin/skills/` structure matches plugin auto-discovery requirements (16 subdirectories with SKILL.md files)
- 2.3: Create `/edify:init` skill at `edify-plugin/skills/init/SKILL.md` (dev mode implementation, consumer mode stubbed with TODO markers per D-8)
- 2.4: Create `/edify:update` skill at `edify-plugin/skills/update/SKILL.md` (dev mode no-op, consumer mode fragment copy per D-8)

---

### Phase 3: Hook Migration (3 steps)

**Scope:** Create hooks.json, version-check hook, delete symlink-redirect hook

**Dependencies:** Phase 1 (plugin manifest)

**Model:** Haiku (mostly configuration files)

**Estimated Complexity:** Low (~150 lines total)

**Steps:**
- 3.1: Create `edify-plugin/hooks/hooks.json` with direct format `{"PreToolUse": [...]}` using `$CLAUDE_PLUGIN_ROOT` paths (per D-4)
- 3.2: Delete `edify-plugin/hooks/pretooluse-symlink-redirect.sh` (purpose eliminated by plugin auto-discovery)
- 3.3: Create `edify-plugin/hooks/userpromptsubmit-version-check.py` (version mismatch detection with once-per-session gating via `tmp/.edify-version-checked` temp file)

---

### Phase 4: Justfile Modularization (2 steps)

**Scope:** Extract portable recipes, update root justfile with import

**Dependencies:** Phase 0 (edify-plugin directory rename)

**Model:** Haiku (file moves and edits)

**Estimated Complexity:** Moderate (~200 lines moved + minimal bash prolog per D-5)

**Steps:**
- 4.1: Create `edify-plugin/just/portable.just` with extracted recipes (claude with `--plugin-dir ./edify-plugin`, claude0, wt-*, precommit-base) + minimal bash prolog (fail, visible, color variables only per D-5)
- 4.2: Update root `justfile` (add `import 'edify-plugin/just/portable.just'`, remove migrated recipes, keep project-specific recipes and full bash prolog)

---

### Phase 5: Cleanup and Validation (3 steps)

**Scope:** Remove symlinks, update fragment docs, test everything

**Dependencies:** Phase 1-4 complete (all plugin components ready)

**Model:** Haiku for cleanup, Sonnet for validation

**Estimated Complexity:** Low for cleanup, High for validation

**Steps:**
- 5.1: Remove symlinks from `.claude/skills/` (16 symlinks), `.claude/agents/` (12 symlinks, preserve `*-task.md` regular files), `.claude/hooks/` (4 symlinks)
- 5.2: Cleanup configuration and documentation:
  - Remove `hooks` section from `.claude/settings.json`
  - Remove `sync-to-parent` recipe from `edify-plugin/justfile`
  - Update `edify-plugin/fragments/claude-config-layout.md`, `sandbox-exemptions.md`, `project-tooling.md`, `delegation.md` (remove `sync-to-parent` references)
- 5.3: Validate all functionality:
  - Plugin discovery: `claude --plugin-dir ./edify-plugin` → skills in `/help`, agents in Task tool
  - Hook testing: trigger each PreToolUse, PostToolUse, UserPromptSubmit event, verify behavior matches baseline
  - Agent coexistence: create test `*-task.md` agent, verify both plugin and local agents visible (FR-8)
  - NFR-1: compare edit→restart cycle time (should match symlink baseline)
  - NFR-2: measure context size before/after migration with identical session (token count diff ≤ 5%)

---

### Phase 6: Cache Regeneration (2 steps)

**Scope:** Regenerate cached help files after justfile changes

**Dependencies:** Phase 4 (justfile import changes `just --list` output), Phase 5 (edify-plugin justfile sync-to-parent removal)

**Model:** Haiku (script execution)

**Estimated Complexity:** Trivial (2 commands)

**Steps:**
- 6.1: Regenerate `.cache/just-help.txt` (imported recipes change output)
- 6.2: Regenerate `.cache/just-help-edify-plugin.txt` (sync-to-parent removed, filename updated from agent-core)

---

## Complexity Distribution

| Phase | Steps | Complexity | Rationale |
|-------|-------|------------|-----------|
| Phase 0 | 1 | Trivial | Directory rename + path updates |
| Phase 1 | 2 | Trivial | Simple JSON + version file |
| Phase 2 | 4 | Moderate | Skill design requires reasoning |
| Phase 3 | 3 | Low | Config + script creation |
| Phase 4 | 2 | Moderate | Recipe extraction + bash prolog |
| Phase 5 | 3 | Mixed | Cleanup low, validation high |
| Phase 6 | 2 | Trivial | Cache regeneration |

**Total:** 17 steps across 7 phases

---

## Phase Dependencies

```
Phase 0 (Directory Rename)
    ↓
Phase 1 (Manifest)
    ↓
    ├─→ Phase 2 (Skills/Agents)
    ├─→ Phase 3 (Hooks)
    └─→ Phase 4 (Justfile) — depends on Phase 0
         ↓       ↓       ↓
         └───────┴───────┘
                 ↓
          Phase 5 (Cleanup)
                 ↓
          Phase 6 (Cache)
```

**Notes:**
- Phase 0 must complete first (directory rename required for all edify-plugin/ paths)
- Phase 1 must complete after Phase 0 (plugin manifest uses edify-plugin/ path)
- Phases 2, 3 are independent and can run in parallel after Phase 1
- Phase 4 depends on Phase 0 (justfile uses edify-plugin/ paths) and Phase 1 (for --plugin-dir consistency)
- Phase 5 must wait for all plugin components (2-4) to be verified working
- Phase 6 must wait for cleanup (justfile changes in Phase 4 and Phase 5)

---

## Success Criteria

**Per-phase checkpoints:**

Each phase ends with verification before proceeding to next phase.

- Phase 0: Directory renamed (`edify-plugin/` exists), all path references updated (justfile, .gitmodules, settings.json, CLAUDE.md)
- Phase 1: `plugin.json` and `.version` files exist at `edify-plugin/.claude-plugin/` and `edify-plugin/` and parse correctly
- Phase 2: Skills appear in `/help` output after `claude --plugin-dir ./edify-plugin`; agents visible in Task tool
- Phase 3: Hooks fire correctly (manual testing for each event type: PreToolUse, PostToolUse, UserPromptSubmit) with direct format hooks.json
- Phase 4: `just claude` works via import with `--plugin-dir ./edify-plugin`, `just wt-new test` creates worktree correctly
- Phase 5: All symlinks removed, plugin discovery works, hooks functional, NFR validation complete (performance + token overhead measured)
- Phase 6: Cache files contain updated content (imported recipes visible in `just --list` output, edify-plugin justfile without sync-to-parent)

**Overall success:**
- Plugin loads without errors (`claude --plugin-dir ./edify-plugin`)
- All skills/agents/hooks functional (manual validation)
- Performance parity with symlink approach (NFR-1: edit→restart cycle time matches baseline)
- No token overhead increase (NFR-2: context size diff ≤ 5%)
- Existing project workflows unaffected (hooks behavior matches current)

---

## Open Questions

1. **Symlink count verification:** Design says 16 skills + 12 agents + 4 hooks = 32 symlinks. During Phase 5 step 5.1, verify actual count matches expected distribution before removal.

---

## Notes

- **Directory rename first:** Phase 0 must complete before other phases to ensure all paths reference `edify-plugin/` consistently (D-1)
- **Dev mode only:** This runbook implements dev mode (submodule + `--plugin-dir`). Consumer mode (marketplace install) is designed but deferred per D-8
- **hooks.json format:** Direct format `{"PreToolUse": [...]}`, not wrapper format (D-4)
- **Idempotency:** All file creation steps check existence first. Runbook can be re-run safely
- **Rollback:** Each phase is independently revertible via git. Phase 5 (symlink cleanup) is the point of no return — execute last
- **Testing strategy:** Manual testing per component. Hook testing requires restart (hooks only load at session start)

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- Phase 1 (2 trivial steps: create plugin.json + .version) — consider merging into single step if both files are simple file creation with no logic
- Phase 6 (2 trivial cache regeneration commands) — can be batched as single step with two commands

**Phase 0 expansion:**
- Directory rename affects: `.gitmodules`, root justfile `import` statement, `.claude/settings.json` permissions.allow patterns, CLAUDE.md fragment `@` references
- Use `git mv agent-core edify-plugin` to preserve history
- Search for all `agent-core` string occurrences: `grep -r "agent-core" --exclude-dir=.git --exclude-dir=plans` to catch missed references
- Test after rename: `just --list` should work (validates justfile syntax), symlinks still resolve (validates existing workflow until Phase 5)

**Phase 2 expansion:**
- Load `plugin-dev:plugin-structure` and `plugin-dev:hook-development` skills before expanding Phase 2 (skill creation needs plugin auto-discovery rules)
- `/edify:init` skill: emphasize dev-mode implementation with clear TODO markers for consumer mode code paths per D-8
- `/edify:update` skill: note that dev mode is no-op (fragments read directly via `@edify-plugin/fragments/` references), consumer mode copies fragments

**Phase 3 expansion:**
- Direct format for hooks.json: `{"PreToolUse": [...]}` not `{"hooks": {"PreToolUse": [...]}}` per D-4
- Hook testing requires restart after creation — add explicit "restart Claude Code session" instruction before validation
- Test procedure for each hook event type: PreToolUse (Write/Edit + Bash), PostToolUse (Bash), UserPromptSubmit (any prompt)
- Version check hook: verify temp file gating mechanism works (first prompt warns, subsequent prompts silent)

**Phase 4 expansion:**
- `claude` recipe must use `--plugin-dir ./edify-plugin` (not `./agent-core`) — consistency with Phase 0 rename
- portable.just bash prolog scope per D-5: fail, visible, color variables only (minimal subset of root justfile prolog)
- precommit-base recipe calls validators via `edify-plugin/bin/` relative paths

**Phase 5 expansion:**
- NFR validation requires baseline capture BEFORE migration — add pre-migration baseline step at beginning of Phase 5
- Baseline measurements: edit→restart cycle time (stopwatch), context size (count tokens in session with identical prompt)
- Agent coexistence test: create simple `test-task.md` agent, verify both plugin agents and local agent appear in Task tool dropdown
- Fragment doc updates (step 5.2) — files: claude-config-layout.md, sandbox-exemptions.md, project-tooling.md, delegation.md

**Checkpoint guidance:**
- Phase 0 checkpoint: verify `just --list` works and symlinks still resolve before proceeding to Phase 1
- Each phase ends with explicit verification before proceeding to next phase
- Phase 5 is critical validation checkpoint — do NOT proceed to Phase 6 (cache regeneration) until all functionality verified working
- If plugin discovery fails at any point before Phase 5 step 5.1 (symlink removal), rollback is simple: revert git changes

**References to include:**
- Design D-1 (naming hierarchy) — edify-plugin is git repo name, edify is marketplace plugin name
- Design D-4 (hooks.json format) — direct format `{"PreToolUse": [...]}` for hooks/hooks.json file
- Design D-5 (justfile import) — portable.just bash prolog scope: fail, visible, color variables only
- Design Component 2 (hook migration) — direct format hooks.json with `$CLAUDE_PLUGIN_ROOT` paths
- Design Component 7 (version check) — temp file path `tmp/.edify-version-checked` for once-per-session gating
