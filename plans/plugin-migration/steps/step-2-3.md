# Step 2.3

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

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
