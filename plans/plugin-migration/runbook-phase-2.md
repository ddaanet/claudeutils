# Phase 2: Skills and Agents

**Purpose:** Verify existing skill/agent structure meets plugin requirements, create `/edify:init` and `/edify:update` skills.

**Dependencies:** Phase 1 (plugin manifest exists)

**Model:** Sonnet (skill design requires reasoning)

---

## Step 2.1: Verify agent structure

**Objective:** Confirm `edify-plugin/agents/` contains 14 agent `.md` files and structure matches plugin auto-discovery requirements.

**Execution Model:** Haiku (inline verification)

**Implementation:**

Verify agent structure:

```bash
# Count agent .md files
agent_count=$(find edify-plugin/agents -maxdepth 1 -name "*.md" -type f | wc -l)
echo "Agent count: $agent_count"

# List agent files
find edify-plugin/agents -maxdepth 1 -name "*.md" -type f | sort
```

**Expected count:** 14 agent files

**Design Reference:**
- Design Component 1: "Plugin agents are discovered from `edify-plugin/agents/`. Plan-specific agents (`*-task.md`) live in `.claude/agents/` as regular files."
- Plugin auto-discovery: All `.md` files in `agents/` directory load automatically

**Validation:**
- Agent count equals 14: `[ "$agent_count" -eq 14 ]`
- All files are `.md` extension
- Files are at `agents/` root level (not nested in subdirectories)

**Expected Outcome:** 14 agent `.md` files confirmed at `edify-plugin/agents/`.

**Error Conditions:**
- Count mismatch → Investigate missing or extra files
- Nested subdirectories found → Agents must be at root level for auto-discovery

**Success Criteria:**
- Exactly 14 `.md` files in `edify-plugin/agents/`
- All agents at root level (no subdirectories)

---

## Step 2.2: Verify skill structure

**Objective:** Confirm `edify-plugin/skills/` contains 16 skill subdirectories, each with `SKILL.md` file.

**Execution Model:** Haiku (inline verification)

**Implementation:**

Verify skill structure:

```bash
# Count skill directories
skill_count=$(find edify-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "Skill directory count: $skill_count"

# Count SKILL.md files
skill_md_count=$(find edify-plugin/skills -name "SKILL.md" | wc -l)
echo "SKILL.md count: $skill_md_count"

# List skill directories
find edify-plugin/skills -mindepth 1 -maxdepth 1 -type d | sort

# Verify each directory has SKILL.md
for dir in edify-plugin/skills/*/; do
  if [ ! -f "$dir/SKILL.md" ]; then
    echo "Missing SKILL.md in: $dir"
  fi
done
```

**Expected counts:**
- 16 skill subdirectories
- 16 `SKILL.md` files (one per directory)

**Design Reference:**
- Design outline: "16 skills symlinked via `just sync-to-parent`"
- Plugin auto-discovery: "All `SKILL.md` files in skill subdirectories load automatically"

**Validation:**
- Skill directory count: `[ "$skill_count" -eq 16 ]`
- SKILL.md count: `[ "$skill_md_count" -eq 16 ]`
- Every directory has SKILL.md file

**Expected Outcome:** 16 skill subdirectories confirmed, each with `SKILL.md`.

**Error Conditions:**
- Count mismatch → Investigate missing or extra skills
- Missing SKILL.md → Skill won't auto-discover (must be named exactly `SKILL.md`)
- Skills at root level (not in subdirectories) → Won't auto-discover

**Success Criteria:**
- Exactly 16 subdirectories in `edify-plugin/skills/`
- Every subdirectory contains `SKILL.md`
- No orphan SKILL.md files outside skill directories

---

## Step 2.3: Create /edify:init skill

**Objective:** Create `/edify:init` skill at `edify-plugin/skills/init/SKILL.md` for dev mode scaffolding.

**Execution Model:** Sonnet (skill design)

**Implementation:**

Create skill directory and SKILL.md:

```bash
mkdir -p edify-plugin/skills/init
```

Then create `edify-plugin/skills/init/SKILL.md` with:

**YAML frontmatter:**
```yaml
---
name: edify:init
description: Scaffold CLAUDE.md structure and fragment references for edify plugin (dev mode only)
version: 1.0.0
---
```

**Skill content structure:**

1. **Purpose section:**
   - Scaffolds project structure for edify plugin
   - Dev mode only (submodule present)
   - Idempotent (safe to re-run)

2. **When to Use:**
   - New project setup
   - Adding edify to existing project
   - After cloning project with edify-plugin submodule

3. **Behavior:**
   - Detect installation mode: `test -d edify-plugin` (check `edify-plugin/` directory exists)
   - Create `agents/` directory if missing: `mkdir -p agents`
   - Create `agents/session.md` from template if missing: copy from `edify-plugin/templates/session.template.md`
   - Create `agents/learnings.md` from template if missing: copy from `edify-plugin/templates/learnings.template.md`
   - Create `agents/jobs.md` from template if missing: copy from `edify-plugin/templates/jobs.template.md`
   - If no CLAUDE.md: copy `edify-plugin/templates/CLAUDE.template.md` with `@edify-plugin/fragments/` references
   - If CLAUDE.md exists: no modification (preserve user content)
   - Write `.edify-version` with current plugin version from `edify-plugin/.version`
   - Use Bash tool for all file operations (mkdir, cp, version writes)

4. **Consumer mode handling:**
   - Detect consumer mode: `test ! -d edify-plugin` (no `edify-plugin/` directory)
   - Add TODO markers: "Consumer mode fragment copying not yet implemented" (per D-7: Consumer Mode Deferred)
   - Exit with clear message directing to dev mode setup

5. **Idempotency guarantees:**
   - Every operation checks before acting (if file exists, skip copy)
   - Re-running applies only missing pieces
   - No data destruction risk
   - **Why init-specific**: Init scaffolds missing structure (safe to re-run); update overwrites (explicit sync action)

**Design References:**
- Component 1: Plugin auto-discovery (skills/*/SKILL.md pattern)
- Component 4: `/edify:init` scaffolding behavior
- D-3: Fragment distribution via skill, not script
- D-7: Consumer mode deferred (dev mode only in this migration)

**Validation:**
- Skill file exists at `edify-plugin/skills/init/SKILL.md`
- YAML frontmatter is valid: contains required fields (name, description, version), name is `edify:init`, version follows semver (1.0.0), no YAML parse errors
- Skill description triggers on "scaffold", "setup", "init"
- Dev mode logic is complete with explicit bash commands
- Consumer mode has TODO markers referencing D-7

**Expected Outcome:** `/edify:init` skill created with dev mode implementation.

**Error Conditions:**
- Invalid YAML frontmatter → Fix syntax, validate with `python -c 'import yaml; yaml.safe_load(open("..."))'`
- Missing template files → Verify templates exist in `edify-plugin/templates/`, copy template from upstream if missing
- Logic errors → Review behavior against design Component 4 and D-3

**Success Criteria:**
- Skill file exists and is well-formed
- Skill invokable via `/edify:init` command
- Dev mode behavior complete per design
- Consumer mode clearly marked as TODO

---

## Step 2.4: Create /edify:update skill

**Objective:** Create `/edify:update` skill at `edify-plugin/skills/update/SKILL.md` for fragment sync.

**Execution Model:** Sonnet (skill design)

**Implementation:**

Create skill directory and SKILL.md:

```bash
mkdir -p edify-plugin/skills/update
```

Then create `edify-plugin/skills/update/SKILL.md` with:

**YAML frontmatter:**
```yaml
---
name: edify:update
description: Sync fragments when edify plugin version changes (no-op in dev mode)
version: 1.0.0
---
```

**Skill content structure:**

1. **Purpose section:**
   - Syncs fragments when plugin updates
   - Dev mode: No-op (fragments read directly via `@edify-plugin/fragments/`)
   - Consumer mode: Copies updated fragments to `agents/rules/`

2. **When to Use:**
   - After version check hook warns of fragment staleness
   - Manually checking for fragment updates
   - After plugin upgrade

3. **Behavior (dev mode):**
   - Check installation mode: `test -d edify-plugin` (verify `edify-plugin/` directory exists)
   - Read current `$CLAUDE_PROJECT_DIR/.edify-version` and plugin version from `edify-plugin/.version`
   - If versions match: "Already up to date"
   - If versions differ: "Dev mode uses direct references, no sync needed. Updated .edify-version marker."
   - Write current version to `$CLAUDE_PROJECT_DIR/.edify-version`
   - Skill removes temp file `tmp/.edify-version-checked` to reset once-per-session gate after version update
   - Exit successfully
   - Use Bash tool for all file operations (version reads, version write, temp file removal)

4. **Behavior (consumer mode):**
   - Check installation mode: `test ! -d edify-plugin` (no `edify-plugin/` directory)
   - Add TODO markers: "Consumer mode fragment copying not yet implemented" (per D-7: Consumer Mode Deferred)
   - Copy fragments from `$CLAUDE_PLUGIN_ROOT/fragments/` to `agents/rules/`
   - Update `@` references in CLAUDE.md
   - Write current version to `$CLAUDE_PROJECT_DIR/.edify-version`

5. **Version marker update:**
   - Always update `.edify-version` to match plugin version source (`edify-plugin/.version` in dev mode, `$CLAUDE_PLUGIN_ROOT/.version` in consumer mode)
   - Removes `tmp/.edify-version-checked` after update to allow version check hook to fire again

**Design References:**
- Component 1: Plugin auto-discovery (skills/*/SKILL.md pattern)
- Component 4: `/edify:update` skill behavior
- D-7: Consumer mode deferred
- Fragment versioning: dev mode reads directly, consumer mode copies

**Validation:**
- Skill file exists at `edify-plugin/skills/update/SKILL.md`
- YAML frontmatter is valid: contains required fields (name, description, version), name is `edify:update`, version follows semver (1.0.0), no YAML parse errors
- Skill description triggers on "update", "sync", "fragments"
- Dev mode logic is complete with explicit bash commands (version marker update only)
- Consumer mode has TODO markers referencing D-7

**Expected Outcome:** `/edify:update` skill created with dev mode as no-op.

**Error Conditions:**
- Invalid YAML frontmatter → Fix syntax
- Missing version file references → Add correct paths
- Logic errors → Review behavior against design

**Success Criteria:**
- Skill file exists and is well-formed
- Skill invokable via `/edify:update` command
- Dev mode behavior: version marker update only
- Consumer mode clearly marked as TODO

---

## Phase 2 Checkpoint

**Verification:**

Run these commands to verify Phase 2 completion:

```bash
# Verify agent structure
agent_count=$(find edify-plugin/agents -maxdepth 1 -name "*.md" -type f | wc -l)
[ "$agent_count" -eq 14 ] && echo "✓ Agent structure verified" || echo "✗ Agent count mismatch"

# Verify skill structure
skill_count=$(find edify-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
skill_md_count=$(find edify-plugin/skills -name "SKILL.md" | wc -l)
[ "$skill_count" -eq 18 ] && [ "$skill_md_count" -eq 18 ] && echo "✓ Skill structure verified (16 existing + 2 new)" || echo "✗ Skill count mismatch"

# Verify new skills exist
test -f edify-plugin/skills/init/SKILL.md && echo "✓ /edify:init skill created" || echo "✗ /edify:init missing"
test -f edify-plugin/skills/update/SKILL.md && echo "✓ /edify:update skill created" || echo "✗ /edify:update missing"

# Verify YAML frontmatter is valid
for skill in init update; do
  python3 -c "import yaml; yaml.safe_load(open('edify-plugin/skills/$skill/SKILL.md'))" && \
    echo "✓ $skill YAML valid" || echo "✗ $skill YAML invalid"
done

# Test plugin discovery (requires restart)
echo "Manual test required:"
echo "  1. Exit current Claude Code session"
echo "  2. Restart: claude --plugin-dir ./edify-plugin"
echo "  3. Verify /edify:init and /edify:update appear in /help output"
echo "  4. Verify skills are invokable (run /edify:init --help or similar)"
```

**Success:** All verification commands pass, skills discoverable after restart

**On failure:** Review error messages, fix issues, re-run verification

**Next:** Proceed to Phase 3 (Hook Migration)
