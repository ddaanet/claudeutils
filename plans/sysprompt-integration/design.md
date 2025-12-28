# System Prompt Pattern Integration: Design

**Goal**: Extract and integrate relevant patterns from Claude Code's system prompt into
our module system, enabling agents with overridden system prompts to retain beneficial
behaviors.

- **Implementation**: See `tasks-opus.md` and `tasks-delegable.md`.
- **Draft Content**: See `drafts.md` for preliminary module content.

---

## Problem

When using Claude Code with a custom/overridden system prompt (via `--system-prompt` or
orchestration), agents lose access to Claude Code's built-in behavioral patterns:

- Tool usage best practices (batching, specialized tools over bash)
- Communication patterns (emoji, conciseness, professional objectivity)
- Safety patterns (OWASP, over-engineering avoidance)
- Progress tracking (TodoWrite usage patterns)

## Solution

Extract patterns from Claude Code's system prompt into our modular system, categorized
by:

1. **Tool-conditional modules** (`.tool.md`) - included when specific tools are enabled
2. **Core modules** (`.semantic.md`) - patterns that apply to all/most roles
3. **Role-specific modules** - patterns that apply to specific role types

---

## Source Material

- Claude Code system prompt v2.0.75 (from `claude-code-system-prompts` repository)
- Task agent prompt (agent-prompt-task-tool.md) for scope comparison
- Reference extraction in `agents/modules/src/sysprompt-reference/` (13 files)

### System Tool Descriptions

Instructions exist not only in the system prompt but also in **tool descriptions**
injected when tools are enabled. Source files in `claude-code-system-prompts`:

```
system-prompts/tool-description-*.md
```

**Key considerations:**

- **Not all tools in plain Claude Code**: Computer, ReadFile are IDE/extension-only.
- **Dynamic injection**: `tool-description-task-async-return-note.md` is NOT in initial
  prompt (injected later).
- **Large tool descriptions**:
  `tool-description-bash-git-commit-and-pr-creation-instructions.md` is substantial -
  included whenever Bash tool enabled.

**Budgeting implications:**

Role budgets must account for both scenarios:

1. **Fine-tuned sessions** (wrapper/agent files): Relevant tools only, minimal tool
   description overhead.
2. **Default interactive sessions**: All system tools enabled, full tool description
   load.

### Related Plans

- `plans/DESIGN_MODULE_SYSTEM.md` - Overall module system architecture
- `plans/plan-module-system-outline.md` - Module system implementation phases

---

## Reference Files Created

Created `agents/modules/src/sysprompt-reference/` with 13 reference files:

| File                                    | Content                                | Integration Target         |
| --------------------------------------- | -------------------------------------- | -------------------------- |
| `identity.sysprompt.md`                 | CLI context, output format             | Core                       |
| `security.sysprompt.md`                 | URL restrictions, OWASP                | Code roles                 |
| `professional-objectivity.sysprompt.md` | Technical accuracy                     | Conversational roles       |
| `planning-no-timelines.sysprompt.md`    | No time estimates                      | Planning roles             |
| `todowrite.sysprompt.md`                | Task tracking with examples            | todowrite.tool.md          |
| `askuser.sysprompt.md`                  | Question framing                       | askuser.tool.md            |
| `user-hooks.sysprompt.md`               | Hook handling                          | Deferred (research needed) |
| `doing-tasks.sysprompt.md`              | Over-engineering, read-before-modify   | Code roles                 |
| `system-reminders.sysprompt.md`         | System reminder handling               | Core                       |
| `tool-policy.sysprompt.md`              | Parallel/sequential, specialized tools | Tool modules               |
| `tone-style.sysprompt.md`               | Emoji, conciseness                     | Core                       |
| `help-feedback.sysprompt.md`            | Help commands                          | Interactive-only (skip)    |
| `documentation-lookup.sysprompt.md`     | Self-documentation                     | Interactive-only (skip)    |

See `CATALOG.md` in that directory for scope analysis and integration notes.

---

## Key Decisions

1. **Separate directory** (`tools/`) - cleaner than embedding in existing modules
2. **`.tool.md` suffix** - distinguishes from always-included `.semantic.md`
3. **`requires_tools` frontmatter** - declarative, composer handles matching
4. **No variable interpolation** - tool names are stable, keep it simple
5. **Single variant per tool module** - start simple, add tier variants if needed
6. **No markdown title before frontmatter** - frontmatter must be first (YAML spec)
7. **Bash consolidation** - all "prefer specialized tools" rules in bash.tool.md

---

## Design Questions Resolved

### Q1: read-edit.tool.md - bash-related instructions

**A**: read-edit.tool.md MUST NOT require Bash. It contains file I/O instructions that
apply whenever Read/Edit/Write are available. The "prefer over Bash" rules should
either:

- Move to bash.tool.md (consolidate all bash-related guidance there), OR
- Use conditional sections within read-edit.tool.md

**Decision**: Consolidate "prefer Read/Edit/Write over Bash" into bash.tool.md since:

- No reasonable use case for Bash without Read/Edit/Write
- Simpler to have all bash-related guidance in one place
- read-edit.tool.md focuses on file operation mechanics (batching, sequencing)

### Q2: read-edit.tool.md - "refresh after write"

**A**: **REVISED interpretation**. Original intent was to save a tool call for the
following edit-execute batch at minimal context cost (old reads discarded). The rule:

- Edits in same batch should NOT have downstream dependencies at all
- Refresh is for the next batch (edit→test cycle), not within-batch
- Move to Preferred tier and clarify: "refresh before next batch that depends on writes"

### Q3: bash.tool.md - use case for "bash without read/write"?

**A**: No reasonable use case identified. All roles with Bash also have Read/Edit/Write.
**Decision**: Consolidate ALL bash-related instructions (including "prefer specialized
tools") into bash.tool.md. This module implicitly requires Read/Edit/Write be available
(enforced by role configs, not requires_tools).

### Q4: todowrite.tool.md - weak-only assumption wrong?

**A**: **CORRECTED**. Tool modules are NOT weak-only. All agents (strong/standard/weak)
use tools. Claude Code uses one system prompt for all model classes, so examples may
have been added for weak model adherence but apply to all.

**Implication**: Tool modules should have tier variants like semantic modules. Examples
may be T2/T3 content that strong models don't need. But for simplicity, start with
single variant per tool module (equivalent to "weak" in detail level).

### Q5: tool-batching.semantic.md - parallel/chained/sequential

**A**: Clarification accepted. Three modes:

1. **Parallel**: No dependencies (Read A, Read B)
2. **Chained**: B runs after A, but B's params don't need A's result (Edit→Test)
3. **Sequential**: B's params depend on A's result (Read→Edit at discovered line)

### Q6: Tool interspersion and context benefit

**A**: **OPEN TRADEOFF**. The system prompt places tool instructions WITHIN workflow
prose (e.g., "When doing tasks... use the TodoWrite tool..."). This interspersion may
provide context benefit - rules are encountered where semantically relevant.

Our composition extracts rules into separate sections (tiered modules). This loses the
natural context association. Adding explicit context to extracted rules (e.g., "When
planning multi-step tasks, use TodoWrite") increases prompt size and cognitive burden.

- **Interspersed**: Context preserved, but harder to tier/budget.
- **Extracted**: Easier to tier/budget, but may lose context benefit.

No clear winner. Start with extracted approach (simpler tooling), monitor for adherence
issues that suggest context loss.

---

## Research: Task Agent vs Main Prompt

Task agent prompt (agent-prompt-task-tool.md) is a **minimal replacement** for the main
system prompt. Rules NOT in Task agent are effectively "interactive-only" in default
Claude Code.

| Pattern                  | Main     | Task | Scope                                |
| ------------------------ | -------- | ---- | ------------------------------------ |
| Hooks                    | ✓        | ✗    | Interactive-only                     |
| System-reminder handling | ✓        | ✗    | *Reminders injected but no handling* |
| Professional objectivity | ✓        | ✗    | Conversational roles                 |
| Over-engineering         | ✓        | ✗    | Interactive-only                     |
| OWASP security           | ✓        | ✗    | Interactive-only                     |
| Read before modify       | ✓        | ✗    | Interactive-only                     |
| Emoji                    | ✓        | ✓    | Both (core)                          |
| File creation            | ✓        | ✓    | Both (core)                          |
| Documentation files      | implicit | ✓    | Task agent MORE specific             |
| Absolute paths           | ✗        | ✓    | Task agent Bash only (cwd resets)    |

**Key finding**: System-reminder at end of Task agent file IS an actual injected
reminder, proving reminders ARE injected into subagent contexts. Handling instructions
not present may be oversight or expectation that agent naturally processes them.

---

## Pending Research

| Topic                     | Notes                                                                                   |
| ------------------------- | --------------------------------------------------------------------------------------- |
| User hooks                | Verify hook availability per execution context                                          |
| Tool description analysis | Extract instructions from tool-description-*.md files                                   |
| Instruction count         | Verify system prompt + tool descriptions ≈ 50 total (validates extraction completeness) |
| bash-git-commit scope     | Analyze large bash-git-commit-and-pr-creation instructions                              |

---

## Architecture

### Tool Module Directory Structure

```
agents/modules/src/tools/
  read-edit.tool.md      # requires: [Read, Edit, Write]
  bash.tool.md           # requires: [Bash]
  task-agent.tool.md     # requires: [Task]
  webfetch.tool.md       # requires: [WebFetch]
  todowrite.tool.md      # requires: [TodoWrite]
  askuser.tool.md        # requires: [AskUserQuestion]
```

### Role Config Schema Extension

```yaml
# agents/roles/code.yaml
role: code
target_class: weak
rule_budget: 35

modules:
  - communication
  - checkpoint-obedience
  - tdd-cycle

enabled_tools: # NEW
  - Read
  - Edit
  - Write
  - Bash
  - Task
```

Composer automatically includes tool modules where `requires_tools ⊆ enabled_tools`.

### Role Tool Enablement

| Role     | Read/Edit | Bash | Task | WebFetch | TodoWrite | AskUser |
| -------- | --------- | ---- | ---- | -------- | --------- | ------- |
| planning | ✓         | ✓    | ✓    | ✓        | ✓         | ✓       |
| code     | ✓         | ✓    | ✓    | -        | -         | -       |
| lint     | ✓         | ✓    | -    | -        | ✓         | -       |
| execute  | ✓         | ✓    | ✓    | -        | -         | -       |
| refactor | ✓         | ✓    | ✓    | -        | ✓         | ✓       |
| review   | ✓         | ✓    | ✓    | -        | -         | -       |
| remember | ✓         | ✓    | -    | -        | ✓         | ✓       |

### Budget Impact

| Tool Module | Weak Rules | Included When           |
| ----------- | ---------- | ----------------------- |
| read-edit   | 5-6        | Read+Edit+Write enabled |
| bash        | 6-8        | Bash enabled            |
| task-agent  | 4-6        | Task enabled            |
| webfetch    | 2-4        | WebFetch enabled        |
| todowrite   | 8-12       | TodoWrite enabled       |
| askuser     | 3-4        | AskUserQuestion enabled |

- **Maximum additional**: ~35 rules (if all tools enabled)
- **Typical code role**: ~16 rules (Read/Edit/Bash/Task, no TodoWrite/AskUser)
- **Minimal lint role**: ~20 rules (Read/Edit/Bash/TodoWrite)

---

## Scope Analysis

### Patterns to Add to Existing Modules

| Pattern                    | Target Module             | Tier | Scope          |
| -------------------------- | ------------------------- | ---- | -------------- |
| Professional objectivity   | communication.semantic.md | T1   | Conversational |
| Emoji: avoid               | communication.semantic.md | T1   | **Core**       |
| Short and concise          | communication.semantic.md | T2   | **Core**       |
| Planning without timelines | plan-creation.semantic.md | T2   | Planning roles |
| Over-engineering avoidance | code-quality.semantic.md  | T1   | Code roles     |
| OWASP security             | code-quality.semantic.md  | T1   | Code roles     |
| System-reminder handling   | (new context module)      | T2   | **Core**       |

### AskUser Scope Clarification

Q: "Relevant for execute but not code?"

**A**: Both are plan execution roles, but differ in decision scope:

- **code**: Follows detailed plan with specific targets. Writes new logic. Unexpected =
  STOP (per communication).
- **execute**: Executes fully-specified refactoring plans from refactor agent. Must NOT
  write new logic, only modifies existing code without changing behavior. Task must be
  fully specified - no decisions needed.
- **refactor**: Broader scope, designs the refactoring approach, may need clarification.

AskUser NOT for code or execute roles - if unexpected, stop and handoff.

---

## Deferred (Phase 3 of main plan)

- Config schema `enabled_tools` field
- Composer tool module selection logic
