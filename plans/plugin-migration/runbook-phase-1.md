### Phase 1: Plugin manifest and structure (type: general, model: sonnet)

Create the plugin structure inside existing `agent-core/` directory. Checkpoint at end gates all downstream phases.

---

## Step 1.1: Create plugin manifest

**Objective**: Create `agent-core/.claude-plugin/plugin.json` with plugin name and version matching `pyproject.toml`.

**Prerequisites**:
- Read `pyproject.toml` (extract current version — currently `0.0.2`)

**Implementation**:
1. Create directory `agent-core/.claude-plugin/`
2. Create `agent-core/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "edify",
     "version": "0.0.2",
     "description": "Opinionated agent framework for Claude Code"
   }
   ```
3. Version must match `pyproject.toml` `version` field exactly

**Expected Outcome**:
- `agent-core/.claude-plugin/plugin.json` exists with valid JSON
- `name` is `edify`, `version` matches `pyproject.toml`

**Error Conditions**:
- If `.claude-plugin/` directory already exists → check contents, do not overwrite without verifying
- If `pyproject.toml` version format is unexpected → escalate

**Validation**:
- `cat agent-core/.claude-plugin/plugin.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['name']=='edify'; print('OK:', d['version'])"`

---

## Step 1.2: Create plugin hooks.json in wrapper format

**Objective**: Rewrite `agent-core/hooks/hooks.json` to contain all 9 surviving hook definitions in wrapper format, with `$CLAUDE_PLUGIN_ROOT` paths.

**Prerequisites**:
- Read `.claude/settings.json` hooks section (current hook bindings — source of truth for matchers and event types)
- Read `agent-core/hooks/hooks.json` (current subset — will be fully rewritten)
- Read outline.md Component 2 hook inventory table (authoritative list of all hooks and their matchers)

**Implementation**:
1. Rewrite `agent-core/hooks/hooks.json` in wrapper format per D-4:
   ```json
   {
     "hooks": {
       "PreToolUse": [...],
       "PostToolUse": [...],
       "UserPromptSubmit": [...],
       "SessionStart": [...],
       "Stop": [...]
     }
   }
   ```
2. Include all 9 surviving hooks with correct matchers:
   - `pretooluse-block-tmp.sh` — PreToolUse, matcher: `Write|Edit`
   - `submodule-safety.py` — PreToolUse, matcher: `Bash` AND PostToolUse, matcher: `Bash` (two entries)
   - `pretooluse-recipe-redirect.py` — PreToolUse, matcher: `Bash`
   - `pretooluse-recall-check.py` — PreToolUse, matcher: `Task`
   - `posttooluse-autoformat.sh` — PostToolUse, matcher: `Write|Edit`
   - `userpromptsubmit-shortcuts.py` — UserPromptSubmit (no matcher)
   - `sessionstart-health.sh` — SessionStart, matcher: `*`
   - `stop-health-fallback.sh` — Stop, matcher: `*`
3. All command paths use `$CLAUDE_PLUGIN_ROOT/hooks/` prefix (not `$CLAUDE_PROJECT_DIR`)
4. Omit `pretooluse-symlink-redirect.sh` (deleted in Phase 2)
5. Preserve existing command prefixes where needed (`python3`, `bash`)

**Expected Outcome**:
- `agent-core/hooks/hooks.json` contains wrapper format with all 5 event types
- 9 hook entries total (submodule-safety appears in both PreToolUse and PostToolUse)
- All paths use `$CLAUDE_PLUGIN_ROOT/hooks/`

**Error Conditions**:
- If JSON validation fails → fix syntax before proceeding
- If hook count doesn't match 9 → verify against outline Component 2 table

**Validation**:
- `python3 -c "import json; d=json.load(open('agent-core/hooks/hooks.json')); assert 'hooks' in d; print('Events:', list(d['hooks'].keys()))"`
- Count hook entries across all events equals 9

---

## Step 1.3: Validate plugin loading (checkpoint)

**Objective**: Verify plugin auto-discovery works with `claude --plugin-dir ./agent-core`. Gates all downstream phases.

**Prerequisites**:
- Steps 1.1, 1.2 complete

**Implementation**:
1. **Requires design:** Programmatic Claude CLI verification via tmux. The agent runs inside a tmux session, so TTY is available. Before building custom tooling, search for existing tools/patterns for tmux-based CLI interaction (send-keys, capture-pane, output verification).
2. Verification targets:
   - FR-1: Skills from `agent-core/skills/` discoverable (check `/help` output or skill listing)
   - FR-1: Agents from `agent-core/agents/` discoverable
   - FR-1: Hooks from `agent-core/hooks/hooks.json` loaded
   - FR-8: Plan-specific agents (`.claude/agents/handoff-cli-tool-*.md`) coexist with plugin agents — both discoverable, no conflicts
   - NFR-1: Dev mode cycle time — edit a skill, restart, verify change visible

**Expected Outcome**:
- Plugin skills, agents, and hooks all discoverable via `--plugin-dir`
- No conflicts between plugin agents and plan-specific agents
- Dev mode cycle time comparable to symlink approach

**Error Conditions**:
- If plugin not discovered → check `plugin.json` format, directory structure
- If hooks not loading → check wrapper format matches Claude Code expectations
- If agent conflicts → check namespace prefixing

**Validation**:
- STOP and report results to orchestrator before proceeding
- This is a manual validation checkpoint — all downstream phases depend on this passing
