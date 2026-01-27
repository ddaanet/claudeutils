# Design: Documentation Refactoring with Domain-Based Rules

## Problem Summary

**CLAUDE.md (~350 lines):** Monolithic, always loaded. Contains cross-cutting rules mixed with domain-specific guidance.

**design-decisions.md (~800 lines):** Active guidance for regression prevention AND consolidation target for /remember. Growing unboundedly.

**Core issues:**
- Low discoverability: Agents scan entire docs for relevant rules
- No progressive disclosure: Everything loaded regardless of task
- Consolidation perpetuates growth: All learnings → design-decisions.md → unbounded
- Regressions: Agents forget to load design-decisions.md when needed

## Solution Architecture

### Three-Layer System

```
Layer 1: Always Loaded (CLAUDE.md ~100 lines)
├── Workflow selection (entry point)
├── Cross-cutting principles (token economy, stop on unexpected, no estimates)
├── Documentation structure (meta)
└── Terminology (reference)

Layer 2: Domain Rules (.claude/rules/)
├── cli-work.md         → paths: src/cli/**, commands/**
├── test-work.md        → paths: tests/**, **/*_test.py
├── workflow-work.md    → paths: plans/**, agents/workflows/**
├── delegation-work.md  → paths: (triggered by Task tool? or always?)
└── skill-work.md       → paths: .claude/skills/**  (already planned)

Layer 3: Domain Decision Docs (agents/decisions/)
├── cli.md              # CLI patterns, /remember target for CLI learnings
├── testing.md          # Test patterns, /remember target for test learnings
├── workflows.md        # Workflow patterns, /remember target for workflow learnings
├── delegation.md       # Delegation patterns, /remember target
└── architecture.md     # Module/path handling, general architecture
```

### Flow

1. Agent works on file matching `tests/**`
2. Rule `test-work.md` auto-loads: "Read agents/decisions/testing.md for conventions"
3. Agent reads domain doc, gets relevant guidance
4. Learning occurs → /remember routes to `agents/decisions/testing.md`
5. Domain doc grows, but bounded to single domain

### /remember Routing Update

Current routing (skill.md:45-49):
```
CLAUDE.md: Communication, error handling, session, delegation, tools, structure, hashtags
agents/design-decisions.md: Tech choices, design patterns, tradeoffs, architecture
```

Proposed routing:
```
CLAUDE.md: Cross-cutting principles only (~50 lines reserved)
agents/decisions/cli.md: CLI patterns, command design
agents/decisions/testing.md: Test organization, patterns
agents/decisions/workflows.md: Workflow patterns, runbook design
agents/decisions/delegation.md: Model selection, quiet execution, agent patterns
agents/decisions/architecture.md: Module structure, path handling, general design
.claude/skills/*/references/: Skill-specific learnings (unchanged)
```

Routing logic:
1. Identify learning domain from keywords/file patterns
2. Route to appropriate decisions/*.md file
3. If cross-cutting (applies everywhere), route to CLAUDE.md
4. If skill-specific, route to skill references (existing behavior)

## Migration Strategy

### Phase 1: Create Structure (Sonnet)

1. Create `agents/decisions/` directory
2. Split design-decisions.md content into domain files:
   - Extract CLI Design → decisions/cli.md
   - Extract Test Organization → decisions/testing.md
   - Extract Workflow Patterns → decisions/workflows.md
   - Extract Delegation Principle → decisions/delegation.md (from CLAUDE.md)
   - Remainder → decisions/architecture.md
3. Create rule files pointing to domain docs
4. Keep design-decisions.md as redirect/index (temporary)

### Phase 2: CLAUDE.md Refactoring (Sonnet)

1. Extract domain sections to decisions/*.md
2. Keep: Workflow Selection, Documentation Structure, Terminology, Core Principles
3. Remove: Delegation Principle, Bash Scripting, File System Rules, Tool Batching
4. Target: ~100 lines

### Phase 3: /remember Update (Sonnet)

1. Update routing table in skill.md
2. Add domain inference logic
3. Update File Selection section
4. Test with sample learnings

### Phase 4: Deprecate design-decisions.md

1. Verify all content migrated
2. Replace with redirect pointing to decisions/
3. Eventually delete (after confirming no references)

## Domain Mapping

| Content | Source | Destination |
|---------|--------|-------------|
| CLI Design | design-decisions.md | decisions/cli.md |
| Test Organization | design-decisions.md | decisions/testing.md |
| Workflow Patterns | design-decisions.md | decisions/workflows.md |
| Module Architecture | design-decisions.md | decisions/architecture.md |
| Path Handling | design-decisions.md | decisions/architecture.md |
| Delegation Principle | CLAUDE.md | decisions/delegation.md |
| Quiet Execution | CLAUDE.md | decisions/delegation.md |
| Model Selection | CLAUDE.md | decisions/delegation.md |
| Bash Scripting | CLAUDE.md | decisions/cli.md (or separate) |
| File System Rules | CLAUDE.md | decisions/architecture.md |
| Tool Batching | CLAUDE.md | decisions/delegation.md |

## Rule File Template

```yaml
---
paths:
  - "relevant/pattern/**"
  - "other/pattern/*"
---

When working on [domain] files, read `agents/decisions/[domain].md` for established patterns and conventions.

Key areas: [brief list of what the doc covers]
```

## Success Criteria

- CLAUDE.md ≤100 lines (core principles only)
- design-decisions.md deprecated/removed
- Domain docs each ≤200 lines
- Rules auto-load when working in domain
- /remember routes to appropriate domain doc
- No guidance lost in migration

## Open Questions

- **Delegation rules trigger:** No file pattern matches delegation work. Options:
  - Always load (defeats progressive disclosure)
  - Trigger on Task tool use (not supported)
  - Include in CLAUDE.md (cross-cutting)
- **Bash scripting placement:** CLI domain or separate?
- **Cross-cutting threshold:** What's truly cross-cutting vs domain-specific?

## Context Isolation (Validated)

**Concern:** Would rules cause context pollution for implementation agents executing runbook steps?

**Answer:** No. Task subagents receive only:
- Their own system prompt (agent definition)
- Environment details (working directory)
- Tool restrictions from frontmatter

Task subagents do NOT inherit:
- Parent's CLAUDE.md
- Parent's .claude/rules/
- Parent's conversation context

Rules are context-level constructs that don't propagate to subagents. This means:
- **Orchestrator** (main agent) sees rules → makes informed decisions, writes good runbooks
- **Implementation agents** (quiet-task, tdd-task) execute in isolation → clean context, no rule pollution

If a subagent needs specific context, use the `skills` field in the agent's frontmatter to preload explicitly. For runbook execution, minimal context is preferred.

Source: claude-code-guide agent validation of Claude Code architecture.

## Dependencies

- Pre-edit rule files task (already planned) - validates rules mechanism
- Existing domain docs: cli-design.md, test-strategy.md (may merge or reference)
