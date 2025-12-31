# Agent Generation Guides - Implementation Status

- **Date:** 2025-12-31
- **Context:** Stopgap manual generation guides until prompt-composer is implemented

---

## Current Status: READY FOR IMPLEMENTATION

### Completed

1. ✅ **Research completed** - Custom agent prompt composition (see design.md:494-577)
2. ✅ **Architecture designed** - File structure and organization defined
3. ✅ **Content sources identified** - All reference files mapped

### Key Finding: Custom Agents Must Include ALL Rules

**Research result (agent a80df58):** Custom agents in `.claude/agents/` do NOT
automatically receive Claude Code's system prompt rules. They must explicitly include:

- Core rules (emoji, objectivity, conciseness)
- Communication patterns
- Tool batching
- All behavioral guidelines

**Consequence:** Subagent prompts are LARGER than role prompts (cannot rely on system
prompt foundation).

---

## Implementation Plan

### Phase 1: Create Tool Modules (6 files)

Migrate content from `plans/prompt-composer/sysprompt-integration/drafts.md` to:

```
agents/modules/src/tools/
├── read-edit-write.tool.md
├── bash.tool.md
├── task.tool.md
├── webfetch.tool.md
├── todowrite.tool.md
└── askuser.tool.md
```

**Source:** drafts.md sections 1-6

### Phase 2: Create Config Files (2 files)

**`agents/config/tool-enablement.md`**

- Extract table from `plans/prompt-composer/sysprompt-integration/design.md:357-367`
- Single source of truth for which tools each role uses

**`agents/config/project-context.md`**

- Extract from existing .sys.md files
- Canonical template for project context section

### Phase 3: Create Guide Files (4 files)

**`agents/guides/README.md`**

- Guide selector with **STOPGAP WARNING**
- Points to three generation types

**`agents/guides/system-prompt-generation.md`**

- For complete system prompt override (--system-prompt flag)
- Output: agents/role-{name}.sys.md
- Composition: core + tools + role-specific + context

**`agents/guides/role-prompt-generation.md`**

- For use WITH Claude Code standard system prompt
- Output: agents/role-{name}.md (existing format)
- Composition: role-specific only

**`agents/guides/subagent-generation.md`**

- For .claude/agents/ role-based agents
- Output: .claude/agents/{role-name}.md
- **CRITICAL:** Must include ALL rules (no automatic injection)

### Phase 4: Update Plan Documentation (3 files)

**`plans/prompt-composer/sysprompt-integration/design.md`**

- ✅ Already updated with research findings
- Replace tool matrix with reference to agents/config/tool-enablement.md

**`plans/prompt-composer/README.md`**

- Add section about manual generation stopgap
- Reference agents/guides/README.md

**`plans/prompt-composer/sysprompt-integration/drafts.md`**

- Add migration notice at top
- Mark as superseded

### Phase 5: Cleanup (1 file)

Delete `agents/SYSPROMPT_GENERATION_GUIDE.md` (replaced by guides/)

---

## File Structure (Final)

```
agents/
├── modules/
│   ├── src/
│   │   ├── *.semantic.md              # 14 existing modules
│   │   ├── sysprompt-reference/       # Existing Claude Code patterns
│   │   │   ├── CATALOG.md
│   │   │   └── *.sysprompt.md (13 files)
│   │   └── tools/                     # NEW: 6 tool modules
│   │       ├── read-edit-write.tool.md
│   │       ├── bash.tool.md
│   │       ├── task.tool.md
│   │       ├── webfetch.tool.md
│   │       ├── todowrite.tool.md
│   │       └── askuser.tool.md
│   └── MODULE_INVENTORY.md
├── config/                            # NEW: 2 config files
│   ├── tool-enablement.md
│   └── project-context.md
├── guides/                            # NEW: 4 guide files
│   ├── README.md (with STOPGAP WARNING)
│   ├── system-prompt-generation.md
│   ├── role-prompt-generation.md
│   ├── subagent-generation.md
│   └── IMPLEMENTATION_STATUS.md (this file)
├── role-*.md                          # Existing role definitions
├── role-*.sys.md                      # Generated system prompts
└── SYSPROMPT_GENERATION_GUIDE.md      # DELETE after migration
```

---

## Key Design Decisions

### 1. README.md Pattern

Use README.md (not OVERVIEW.md) for directory entry points, matching
`plans/prompt-composer/README.md`

### 2. No Duplication

- ❌ Don't create agents/reference/ - would duplicate agents/modules/src/
- ✅ Use references to existing files
- ✅ Single source of truth for all content

### 3. System-Reminder Handling

- **Keep the rule** - explains what `<system-reminder>` tags mean
- Content is injected by Claude Code dynamically
- Rule tells model how to interpret injected tags
- Source: agents/modules/src/sysprompt-reference/system-reminders.sysprompt.md

### 4. Tool Modules Location

- Create in: `agents/modules/src/tools/`
- Keeps all modules under modules/ directory
- Follows semantic module pattern

### 5. No Task-Specific Agents

- Agents have **roles** (code, review, plan)
- Task-specific behavior → skills/slash commands (different mechanism)
- Subagent guide: role-based agents ONLY

---

## Critical Information for Implementation

### Subagent Composition (Based on Research)

Custom agents CANNOT assume Claude Code system prompt. Must explicitly include:

1. **Core rules** from `agents/modules/src/sysprompt-reference/`:
   - tone-style.sysprompt.md (emoji, conciseness)
   - professional-objectivity.sysprompt.md
   - system-reminders.sysprompt.md

2. **Communication patterns** from `agents/modules/src/communication.semantic.md`

3. **Tool batching** from `agents/modules/src/tool-batching.semantic.md`

4. **Tool modules** from `agents/modules/src/tools/` (based on enabled tools)

5. **Role-specific content** from `agents/role-{name}.md`

6. **Minimal project context** (lighter than system prompts)

### Role Prompt Composition

Role prompts work WITH Claude Code system prompt. Include ONLY:

- Role-specific rules
- Role-specific workflows
- Minimal context

DO NOT include (already in Claude Code sysprompt):

- Core rules (emoji, objectivity)
- Tool batching
- Communication patterns

### System Prompt Composition

Full replacement of Claude Code system prompt. Include EVERYTHING:

- Core rules
- Communication patterns
- Tool batching
- Tool modules (based on role's enabled tools)
- Role-specific rules
- Full project context

---

## Next Steps

1. Start with Phase 1 (tool modules)
2. Each phase builds on previous
3. Test generated prompts after each phase
4. Update this file as implementation progresses

---

## References

**Design documents:**

- `plans/prompt-composer/design.md` - Master design specification
- `plans/prompt-composer/sysprompt-integration/design.md` - System prompt patterns
- `plans/prompt-composer/README.md` - Prompt composer overview

**Existing modules:**

- `agents/modules/MODULE_INVENTORY.md` - Module catalog
- `agents/modules/src/sysprompt-reference/CATALOG.md` - System prompt patterns

**Research:**

- `plans/prompt-composer/sysprompt-integration/design.md:494-577` - Agent prompt
  composition research
