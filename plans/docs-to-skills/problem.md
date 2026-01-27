# Problem: Documentation Discoverability and Progressive Disclosure

## Current State

**CLAUDE.md (~350 lines):** Monolithic, always loaded. Sections: Workflow Selection, Communication Rules, Error Handling, Bash Scripting, File System Rules, Session Management, Delegation, Pre-Edit Checks, Tool Batching, Hashtags.

**design-decisions.md (~800 lines):** Historical archive. Sections: Module Architecture, Path Handling, CLI Design, Test Organization, Workflow Patterns. Rarely consulted.

**Problems:**
- Low discoverability: Agents scan entire doc for relevant rules
- No progressive disclosure: Everything loaded regardless of task
- Poor organization: Related rules scattered
- Learnings lost: Consolidate back to monolithic docs, perpetuating problem
- Always-on cost: All rules loaded even when irrelevant

## Desired State

**Skills-based documentation:**
- Topical skills triggered by context (file patterns, tool usage, workflow stage)
- Progressive disclosure: Load only relevant guidance
- High discoverability: Skill descriptions with trigger phrases
- Consolidation target: Learnings flow to skill references, not monolithic docs
- Bounded growth: Each skill focused on single domain

**Example:**
```
Current: CLAUDE.md → "Bash Scripting" section (always loaded)
Proposed: .claude/skills/bash-scripting/SKILL.md (triggers on Bash tool use)
```

## Inspiration: Cursor Learnings Pattern

From `gist.github.com/jediahkatz/e528631580cc42dd5b8092aa7f162851`:

- Skills in `.cursor/skills/` (personal or project)
- Topic-based segmentation: Multiple topics → separate skills
- Consolidation merges into existing skills without duplication
- Max ~500 lines per skill

**Key insight:**
> "Read existing SKILL.md. Identify where new learnings fit. Integrate without duplicating."

Prevents fragmentation, maintains coherent skills.

## Design Questions

### 1. CLAUDE.md Section Mapping

**Candidates for conversion:**
- Bash Scripting → `bash-scripting` skill (trigger: Bash tool use)
- File System Rules → `sandboxed` skill (trigger: Bash tool, file operations)
- Delegation Principle → `delegation` skill (trigger: orchestrator tasks)
- Tool Batching → `tool-optimization` skill (trigger: multi-tool workflows)
- Error Handling → `error-handling` skill (trigger: after failures? always?)
- Communication Rules → `communication` skill (trigger: always? orchestrator-only?)

**Stay in CLAUDE.md:**
- Workflow Selection (entry point)
- Documentation Structure (meta)
- Terminology (reference)
- Core principles (~50 lines minimal always-loaded)

### 2. design-decisions.md Treatment

Mostly stays archival (historical reference). Possibly:
- Extract high-value sections to skill references (CLI Design, Test Organization)
- Create `architecture` skill pointing to key decisions
- Most sections remain, referenced by skills when relevant

### 3. Triggering Mechanisms

**Options:**
- Tool-based: Bash tool → bash-scripting skill
- File-based: Editing `*.md` → documentation-writing skill
- Workflow-based: /orchestrate → orchestration skill
- Model-based: Opus session → designer-guidelines skill

**Challenge:** Cross-cutting rules (token economy, error handling, stop on unexpected results).

**Solutions:**
- Minimal always-loaded CLAUDE.md with core principles
- Cross-cutting skill with broad trigger phrases
- Rule-based injection (`.claude/rules/` pattern from context.md)

### 4. Cross-Cutting Concerns

Rules like "token economy", "stop on unexpected results", "no time estimates" apply everywhere.

**Options:**
1. Minimal always-loaded CLAUDE.md (~50 lines)
2. Cross-cutting skill with broad triggers
3. `.claude/rules/` with path patterns

**Likely hybrid:** Core principles in CLAUDE.md, domain rules in skills, file-specific rules in `.claude/rules/`.

### 5. Migration Strategy

**Incremental (recommended):**
1. Create pilot skill (bash-scripting or sandboxed)
2. Test triggering, measure impact
3. Iterate taxonomy
4. Extract remaining sections

**vs Full redesign:** All at once, higher risk.

**vs Dual system:** CLAUDE.md + skills coexist, gradual shrinkage.

### 6. Integration with Learnings Consolidation

Current: `plans/learnings-consolidation/design.md` stages learnings → `/remember` consolidates to skill references.

**Dependency:** Docs-to-skills creates consolidation targets. As CLAUDE.md converts to skills, learnings flow to those skill references instead of monolithic docs.

Example: Bash learning → `.claude/skills/bash-scripting/references/learnings.md`

## Success Criteria

- CLAUDE.md shrinks to <100 lines (core principles)
- Skills trigger contextually, not always-loaded
- Agents find relevant guidance without grep
- Learnings consolidate to focused skill references
- New rules flow to appropriate skills

## Open Questions

- How to handle always-relevant rules (communication, token economy)?
- Should design-decisions.md convert or stay archival?
- Right skill granularity (broad vs narrow)?
- Test skill triggering effectiveness?
- Use `.claude/rules/` for file-based injection?
- Which section converts first (pilot)?
