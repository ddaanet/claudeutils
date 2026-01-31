# Agent Instructions

@agent-core/fragments/workflows-terminology.md

---

## Documentation Structure

**Progressive discovery:** Don't preload all documentation. Read specific guides only when needed.

### Core Instructions
- **CLAUDE.md** (this file) - Agent instructions, workflows, communication rules

### Architecture & Design
- **agents/decisions/architecture.md** - Module structure, path handling, data models, code quality
- **agents/decisions/cli.md** - CLI patterns and conventions
- **agents/decisions/testing.md** - Testing conventions and patterns
- **agents/decisions/workflows.md** - Oneshot and TDD workflow patterns
- **agents/implementation-notes.md** - Detailed implementation decisions (read when implementing similar features)

### Current Work
- @agents/session.md - Current session handoff context (update only on handoff)
- @agents/learnings.md - Accumulated learnings (append-only, soft limit 80 lines)

---

## Communication Rules

@agent-core/fragments/communication.md

@agent-core/fragments/token-economy.md

@agent-core/fragments/commit-skill-usage.md

@agent-core/fragments/no-estimates.md

@agent-core/fragments/error-handling.md

@agent-core/fragments/code-removal.md

@agent-core/fragments/bash-strict-mode.md

@agent-core/fragments/tmp-directory.md

@agent-core/fragments/sandbox-exemptions.md

@agent-core/fragments/claude-config-layout.md

@agent-core/fragments/vet-requirement.md

## Session Management

@agent-core/fragments/execute-rule.md

**Pending task notation:**

When user says "pending: task description":
- Do NOT execute the task now
- Keep in context and write to session.md Pending Tasks section on next handoff
- Acknowledge receipt: "Added to pending tasks"

@agent-core/fragments/delegation.md

### Skill Development

**Rule:** When creating, editing, or discussing skills, start by loading the `plugin-dev:skill-development` skill.

**Location:** All skills live in `agent-core/skills/`. They are symlinked from `.claude/skills/`. Run `just sync-to-parent` in `agent-core/` to update symlinks.

**Why:** The skill-development skill provides:
- Skill structure and frontmatter guidance
- Progressive disclosure patterns
- Triggering condition best practices
- Integration with Claude Code plugin system

**Usage:** Invoke the skill before beginning skill work to load context and patterns.

@agent-core/fragments/tool-batching.md
