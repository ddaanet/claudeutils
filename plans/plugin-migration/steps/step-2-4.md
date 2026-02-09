# Step 2.4

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

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

# Phase 3: Hook Migration

**Purpose:** Create plugin hook configuration, version check hook script, and delete obsolete symlink-redirect hook.

**Dependencies:** Phase 1 (plugin manifest exists)

**Model:** Haiku (configuration and script files)

---
