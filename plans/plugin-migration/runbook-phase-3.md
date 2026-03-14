### Phase 3: Migration skills (type: general, model: opus)

Create `/edify:init` and `/edify:update` skills — agentic prose artifacts requiring opus.

---

## Step 3.1: Create /edify:init skill and CLAUDE.md template

**Objective**: Create the `/edify:init` skill that helps new consumer projects set up edify framework, plus the CLAUDE.md template it references.

**Script Evaluation**: Prose (agentic skill definition)
**Execution Model**: Opus (architectural artifact — agentic prose determining downstream agent behavior)

**Prerequisites**:
- Read outline.md Component 4 "Migration Command" section (behavioral specification)
- Read 2-3 existing skills for format reference: `agent-core/skills/commit/SKILL.md`, `agent-core/skills/handoff/SKILL.md`
- Read `agent-core/fragments/` directory listing (know what fragments exist for distribution)
- Read current CLAUDE.md (understand `@`-reference structure for template design)

**Implementation**:
1. Create `agent-core/skills/init/SKILL.md`:
   - **Conversational, not predetermined recipe.** No real consumer use case yet — over-specifying behavior bakes in unvalidated assumptions
   - Skill should load reference material and discuss setup with user:
     - What fragments to copy to `agents/rules/`
     - How to rewrite CLAUDE.md `@`-references to local copies
     - What `agents/` structure to scaffold (session.md, learnings.md)
     - `.edify.yaml` format and sync policy
   - Reference points the skill needs to be aware of:
     - Fragment inventory (`agent-core/fragments/*.md`)
     - `agents/` directory structure conventions
     - CLAUDE.md template at `agent-core/templates/CLAUDE.template.md`
     - `.edify.yaml` format (version, sync_policy)
   - Idempotent: check before acting, never destroy existing content
   - Consumer mode only — marketplace install context
   - Frontmatter: `name: init`, appropriate description for triggering

2. Create `agent-core/templates/CLAUDE.template.md`:
   - Template for consumer project CLAUDE.md
   - Uses `@agents/rules/` references (local copies, not `agent-core/` submodule paths)
   - Includes standard sections: workflows, communication rules, operational rules
   - Placeholders for project-specific content
   - Must be a starting point, not a complete CLAUDE.md — the `/edify:init` conversation fills in project-specific details

**Expected Outcome**:
- `agent-core/skills/init/SKILL.md` exists with valid skill frontmatter and conversational design
- `agent-core/templates/CLAUDE.template.md` exists with template structure
- Skill references template path correctly

**Error Conditions**:
- If `agent-core/skills/init/` directory doesn't exist → create it
- If template references fragments that don't exist → verify fragment inventory

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer for skill quality review
3. Verify skill appears in plugin discovery: `claude --plugin-dir ./agent-core` → `/help` lists `/edify:init`

---

## Step 3.2: Create /edify:update skill

**Objective**: Create the `/edify:update` skill that syncs fragments and portable justfile when plugin version changes.

**Script Evaluation**: Prose (agentic skill definition)
**Execution Model**: Opus (architectural artifact — agentic prose)

**Prerequisites**:
- Read outline.md Component 4 `/edify:update` section
- Read `agent-core/skills/init/SKILL.md` (created in Step 3.1 — understand separation of concerns)
- Read 1-2 existing skills for format reference

**Implementation**:
1. Create `agent-core/skills/update/SKILL.md`:
   - Behavior: sync fragments + portable justfile module(s), update `.edify.yaml` version
   - Separate from init — update is sync-only, not scaffolding
   - Should handle:
     - Compare current fragments in `agents/rules/` with plugin's `fragments/`
     - Copy updated fragments, preserving any local customizations (warn on conflicts)
     - Sync portable justfile module(s) to project
     - Update `.edify.yaml` version to match current plugin version
   - Idempotent: safe to run when already up-to-date
   - Frontmatter: `name: update`, appropriate description

**Expected Outcome**:
- `agent-core/skills/update/SKILL.md` exists with valid skill frontmatter
- Skill clearly separated from `/edify:init` (sync vs scaffold)
- Handles conflict detection for modified fragments

**Error Conditions**:
- If fragments directory doesn't exist in consumer project → suggest running `/edify:init` first

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer for skill quality review
3. Verify skill appears in plugin discovery
