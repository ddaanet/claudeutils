# Plan: Claude Code System Prompt Pattern Integration

**Goal**: Extract and integrate relevant patterns from Claude Code's system prompt into
our module system, enabling agents with overridden system prompts to retain beneficial
behaviors.

---

## Context

### Problem

When using Claude Code with a custom/overridden system prompt (via `--system-prompt` or
orchestration), agents lose access to Claude Code's built-in behavioral patterns:

- Tool usage best practices (batching, specialized tools over bash)
- Communication patterns (emoji, conciseness, professional objectivity)
- Safety patterns (OWASP, over-engineering avoidance)
- Progress tracking (TodoWrite usage patterns)

### Solution

Extract patterns from Claude Code's system prompt into our modular system, categorized
by:

1. **Tool-conditional modules** (`.tool.md`) - included when specific tools are enabled
2. **Core modules** (`.semantic.md`) - patterns that apply to all/most roles
3. **Role-specific modules** - patterns that apply to specific role types

### Source Material

- Claude Code system prompt v2.0.75 (from `claude-code-system-prompts` repository)
- Task agent prompt (agent-prompt-task-tool.md) for scope comparison
- Reference extraction in `agents/modules/src/sysprompt-reference/` (13 files)

### Related Plans

- `plans/DESIGN_MODULE_SYSTEM.md` - Overall module system architecture
- `plans/plan-module-system-outline.md` - Module system implementation phases

---

## System Prompt Reference Files

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
| Absolute paths           | ✗        | ✓    | Task agent only                      |

**Key finding**: System-reminder at end of Task agent file IS an actual injected
reminder, proving reminders ARE injected into subagent contexts. Handling instructions
not present may be oversight or expectation that agent naturally processes them.

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

**A**: Tiering provides primacy. Must evaluate whether composition loses context
benefit. The system prompt places tool instructions WITHIN workflow prose (e.g., "When
doing tasks... use the TodoWrite tool..."). Our composition extracts rules into
sections.

- **Risk**: Extracted rules may lose semantic connection to workflow context.
- **Mitigation**: Ensure tool modules reference the workflow context explicitly in rule
  text. E.g., "When planning multi-step tasks, use TodoWrite" vs just "Use TodoWrite".

---

## Design Summary

### Architecture Decision

Create **tool fragment modules** (`.tool.md`) in `agents/modules/src/tools/` that are
automatically included when their required tools match a role's `enabled_tools`.

```
agents/modules/src/tools/
  read-edit.tool.md      # requires: [Read, Edit, Write]
  bash.tool.md           # requires: [Bash]
  task-agent.tool.md     # requires: [Task]
  webfetch.tool.md       # requires: [WebFetch]
  todowrite.tool.md      # requires: [TodoWrite]
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

---

## Files to Create

### 1. `agents/modules/src/tools/read-edit.tool.md`

```markdown
# Read/Edit Tool Rules

---

semantic_type: tool_conditional
requires_tools: [Read, Edit, Write]
target_rules:
weak: 6-8

---

## Critical (Tier 1)

### Prefer Specialized Tools Over Bash

Use Read tool for file reading, not cat via Bash. Use Edit/Write for file modification,
not sed or heredocs. Specialized tools have better error handling.

### Sequential Same-File Edits

When making multiple edits to the same file, edit sequentially to avoid line number
drift. Insert bottom-to-top so earlier insertions don't shift later targets.

## Important (Tier 2)

### Batch Independent File Operations

Read multiple files in one message when all needed soon. Edit different files in
parallel when changes are independent.

### Refresh Context After Writes

After writes, read modified files before dependent edits. Stale line numbers cause edit
failures.
```

### 2. `agents/modules/src/tools/bash.tool.md`

```markdown
# Bash Tool Rules

---

semantic_type: tool_conditional
requires_tools: [Bash]
target_rules:
weak: 4-6

---

## Critical (Tier 1)

### Reserve Bash for System Commands

Use Bash for system commands only: git, build, process management. Never use Bash to
communicate - use direct responses.

### Never Use Bash for File I/O

Do not use cat/head/tail when Read available. Do not use echo/heredocs when Write
available. Do not use sed/awk when Edit available.
```

### 3. `agents/modules/src/tools/task-agent.tool.md`

```markdown
# Task/Agent Delegation Rules

---

semantic_type: tool_conditional
requires_tools: [Task]
target_rules:
weak: 4-6

---

## Critical (Tier 1)

### Delegate Complex File Search

Use Task tool for file search to reduce context usage. Agent explores codebase and
returns relevant results without polluting main context.

### Use Explore Agent for Codebase Navigation

For open-ended exploration requiring multiple Glob/Grep rounds, use Explore agent
instead of direct calls.

## Important (Tier 2)

### Proactive Task Delegation

When task matches an agent description, proactively delegate. Don't attempt complex
multi-step exploration manually.
```

### 4. `agents/modules/src/tools/webfetch.tool.md`

```markdown
# WebFetch Tool Rules

---

semantic_type: tool_conditional
requires_tools: [WebFetch]
target_rules:
weak: 2-4

---

## Important (Tier 2)

### Handle Redirects Explicitly

When WebFetch reports redirect to different host, make new request with redirect URL. Do
not assume original content was fetched.
```

### 5. `agents/modules/src/tools/todowrite.tool.md`

```markdown
# TodoWrite Tool Rules

---

semantic_type: tool_conditional
requires_tools: [TodoWrite]
target_rules:
weak: 2-4

---

## Important (Tier 2)

### Track Progress Frequently

Use TodoWrite for multi-step tasks. Create todos at start, update as steps complete,
mark completed immediately after success.
```

---

## Files to Modify

### 1. `agents/modules/src/tool-batching.semantic.md`

**Clarify three execution modes (parallel/chained/sequential):**

```markdown
## Critical (Tier 1)

### Parallel for Independent Operations

When multiple tool calls have no dependencies, make all in same batch. Do not serialize
what can run concurrently. Example: Reading multiple unrelated files.

### Chained for Ordered Operations

When tool B must run after A completes, but B's parameters don't depend on A's return
value, use chained execution. Example: Edit file, then run tests. Tests don't need
edit's return value, just need edit to complete first.

### Sequential for Data Dependencies

When tool B's parameters depend on A's return value, call A first, then construct B's
call using A's result. Never use placeholders or guess values that depend on previous
results. Example: Read file to find line number, then edit at that line.

## Important (Tier 2)

### Never Guess Missing Parameters

If a required parameter cannot be determined from context, ask the user. Do not make up
values or use placeholders.

### Use Exact User-Provided Values

When user provides a specific value (e.g., in quotes), use that value EXACTLY. Do not
modify, "improve", or normalize user-provided values.

### Plan Tool Batches Before Executing

Before making tool calls, identify ALL changes needed. Group by dependency: independent
operations in parallel, dependent operations chained or sequential.
```

### 2. `agents/modules/MODULE_INVENTORY.md`

**Add tool modules section:**

```markdown
## Tool-Conditional Modules

| Module     | requires_tools    | Purpose                        |
| ---------- | ----------------- | ------------------------------ |
| read-edit  | Read, Edit, Write | File I/O preferences, batching |
| bash       | Bash              | System command restrictions    |
| task-agent | Task              | Agent delegation patterns      |
| webfetch   | WebFetch          | Redirect handling              |
| todowrite  | TodoWrite         | Progress tracking              |
```

---

## Implementation Checklist

### Tool Modules

- [ ] Create `agents/modules/src/tools/` directory
- [ ] Create `agents/modules/src/tools/read-edit.tool.md` (no Bash requirement)
- [ ] Create `agents/modules/src/tools/bash.tool.md` (consolidated: specialized tools +
      communication)
- [ ] Create `agents/modules/src/tools/task-agent.tool.md`
- [ ] Create `agents/modules/src/tools/webfetch.tool.md`
- [ ] Create `agents/modules/src/tools/todowrite.tool.md` (expanded with examples)
- [ ] Create `agents/modules/src/tools/askuser.tool.md`

### Existing Module Updates

- [ ] Update `tool-batching.semantic.md` with parallel/chained/sequential
- [ ] Update `communication.semantic.md`:
  - Add emoji: avoid (T1, core)
  - Add short and concise (T2, core)
  - Add professional objectivity (T1, conversational roles only via role config)
- [ ] Update `plan-creation.semantic.md` with no-timelines rule
- [ ] Update `code-quality.semantic.md` with over-engineering and OWASP
- [ ] Create `context-system-reminders.semantic.md` (core)

### Documentation

- [x] Create `agents/modules/src/sysprompt-reference/` (13 files)
- [ ] Update `agents/modules/MODULE_INVENTORY.md` with tool modules
- [ ] Update sysprompt-reference/CATALOG.md with scope analysis

**Deferred** (Phase 3 of main plan):

- Config schema `enabled_tools` field
- Composer tool module selection logic
- Research: user hooks availability per execution context

---

## Budget Impact

| Tool Module | Weak Rules | Included When           |
| ----------- | ---------- | ----------------------- |
| read-edit   | 6-8        | Read+Edit+Write enabled |
| bash        | 4-6        | Bash enabled            |
| task-agent  | 4-6        | Task enabled            |
| webfetch    | 2-4        | WebFetch enabled        |
| todowrite   | 2-4        | TodoWrite enabled       |

- **Maximum additional**: ~24 rules (if all tools enabled)
- **Typical code role**: ~18 rules (no WebFetch/TodoWrite)
- **Minimal lint role**: ~10 rules (Read/Edit/Bash only)

---

## Key Decisions

1. **Separate directory** (`tools/`) - cleaner than embedding in existing modules
2. **`.tool.md` suffix** - distinguishes from always-included `.semantic.md`
3. **`requires_tools` frontmatter** - declarative, composer handles matching
4. **No variable interpolation** - tool names are stable, keep it simple
5. **Single variant per tool module** - start simple, add tier variants if needed
6. **No markdown title before frontmatter** - frontmatter must be first (YAML spec)
7. **Bash consolidation** - all "prefer specialized tools" rules in bash.tool.md

## Role Tool Enablement

| Role     | Read/Edit | Bash | Task | WebFetch | TodoWrite | AskUser |
| -------- | --------- | ---- | ---- | -------- | --------- | ------- |
| planning | ✓         | ✓    | ✓    | ✓        | ✓         | ✓       |
| code     | ✓         | ✓    | ✓    | -        | -         | -       |
| lint     | ✓         | ✓    | -    | -        | ✓         | -       |
| execute  | ✓         | ✓    | ✓    | -        | -         | -       |
| refactor | ✓         | ✓    | ✓    | -        | ✓         | ✓       |
| review   | ✓         | ✓    | ✓    | -        | -         | -       |
| remember | ✓         | ✓    | -    | -        | ✓         | -       |

---

## Additional Patterns from System Prompt

### Scope Analysis (Task Agent comparison)

| Pattern                  | In Task Agent? | Scope Decision                                      |
| ------------------------ | -------------- | --------------------------------------------------- |
| Professional objectivity | ✗              | Conversational roles (planning, refactor, remember) |
| Over-engineering         | ✗              | Code roles (useful despite not in Task agent)       |
| OWASP security           | ✗              | Code roles (useful despite not in Task agent)       |
| Read before modify       | ✗              | All task roles (omission may be oversight)          |
| Emoji: avoid             | ✓              | **Core** (in both prompts)                          |
| File creation            | ✓              | **Core** (in both prompts)                          |
| System reminders         | ✗              | **Core** (reminders ARE injected everywhere)        |
| Hooks                    | ✗              | Interactive-only (orchestrated may not have hooks)  |

### To Add to Existing Modules

| Pattern                    | Target Module             | Tier | Scope          |
| -------------------------- | ------------------------- | ---- | -------------- |
| Professional objectivity   | communication.semantic.md | T1   | Conversational |
| Emoji: avoid               | communication.semantic.md | T1   | **Core**       |
| Short and concise          | communication.semantic.md | T2   | **Core**       |
| Planning without timelines | plan-creation.semantic.md | T2   | Planning roles |
| Over-engineering avoidance | code-quality.semantic.md  | T1   | Code roles     |
| OWASP security             | code-quality.semantic.md  | T1   | Code roles     |
| System-reminder handling   | (new context module)      | T2   | **Core**       |

### New Tool Modules

| Module          | requires_tools  | Purpose                             |
| --------------- | --------------- | ----------------------------------- |
| askuser.tool.md | AskUserQuestion | Question framing, no time estimates |

### AskUser Scope Clarification

Q: "Relevant for execute but not code?"

**A**: Both are plan execution roles, but differ in decision scope:

- **code**: Follows detailed plan with specific targets. Unexpected = STOP (per
  communication).
- **execute**: Runs commands where user input may be needed ("which test?").
- **refactor**: Broader scope, may need clarification on approach.

AskUser NOT for code role - if unexpected, stop and handoff.

### Deferred Research

| Pattern    | Notes                                                  |
| ---------- | ------------------------------------------------------ |
| User hooks | Need to verify hook availability per execution context |

---

## Updated Tool Module Definitions

### read-edit.tool.md (REVISED - no Bash requirement)

```markdown
# Read/Edit Tool Rules

---
semantic_type: tool_conditional
requires_tools: [Read, Edit, Write]
target_rules:
  weak: 6-8
---

## Critical (Tier 1)

### Sequential Same-File Edits

When making multiple edits to the same file, edit sequentially to avoid line number
drift. Insert bottom-to-top so earlier insertions don't shift later targets.

### No Downstream Dependencies in Same Batch

Edits within a single batch must be independent. Do not edit line N then reference what
was written there in the same batch.

## Important (Tier 2)

### Batch Independent File Operations

Read multiple files in one message when all needed soon. Edit different files in
parallel when changes are independent.

### Prefer Editing Over Creating

ALWAYS prefer editing existing files to creating new ones. Only create files when
absolutely necessary for the task. NEVER proactively create documentation.

## Preferred (Tier 3)

### Refresh Context Before Next Batch

After a write batch, if the next batch (e.g., test run) depends on those writes, the
context is already updated. But if making MORE edits to same files, read first.
```

### bash.tool.md (REVISED - consolidated)

```markdown
# Bash Tool Rules

---
semantic_type: tool_conditional
requires_tools: [Bash]
target_rules:
  weak: 6-8
---

## Critical (Tier 1)

### Reserve Bash for System Commands

Use Bash for actual system commands only: git, build, package managers, process
management. NOT for file operations.

### Use Specialized Tools for File I/O

Use Read for file reading, not cat/head/tail. Use Edit for modifications, not sed/awk.
Use Write for file creation, not heredocs or echo. Specialized tools have better error
handling.

### Never Communicate Via Bash

Never use echo, printf, or other Bash commands to communicate with user. Output all
communication directly in response text. Never use code comments to communicate.

## Important (Tier 2)

### Bash is for Execution, Not Exploration

For exploring codebases, use Glob/Grep/Read. Reserve Bash for running commands that have
side effects: builds, tests, git operations.
```

### todowrite.tool.md (REVISED - Expanded)

```markdown
# TodoWrite Tool Rules

---

semantic_type: tool_conditional
requires_tools: [TodoWrite]
target_rules:
weak: 8-12

---

## Critical (Tier 1)

### Use TodoWrite Very Frequently

Use TodoWrite tool VERY frequently for task tracking and planning. It is EXTREMELY
helpful for breaking complex tasks into smaller steps. If you do not use this tool when
planning, you may forget important tasks - that is unacceptable.

### Mark Completed Immediately

Mark todos as completed as soon as each task is done. Do NOT batch multiple completions.
Update status in real-time as you work.

## Important (Tier 2)

### Break Down Complex Tasks

For multi-step tasks, create todo items for each step at the start. Add new items when
you discover sub-tasks (e.g., finding 10 type errors → create 10 items).

### Show Progress to User

Use todos to give user visibility into progress. Mark items in_progress when starting,
completed when done. One in_progress item at a time.

## Examples

<example>
user: Run the build and fix any type errors
assistant: Uses TodoWrite to create:
- Run the build
- Fix any type errors

Runs build, finds 10 errors. Uses TodoWrite to add 10 items for each error. Marks first
as in_progress, fixes it, marks completed, moves to next...
</example>

<example>
user: Implement usage metrics tracking with export
assistant: Uses TodoWrite to plan:

1. Research existing metrics in codebase
2. Design metrics collection system
3. Implement core tracking
4. Create export functionality

Starts research, marks in_progress. Finds existing code. Marks completed, continues to
next item...
</example>
```

### askuser.tool.md (NEW)

```markdown
# AskUserQuestion Tool Rules

---

semantic_type: tool_conditional
requires_tools: [AskUserQuestion]
target_rules:
weak: 3-4

---

## Important (Tier 2)

### Ask When Unsure

Use AskUserQuestion when you need clarification, want to validate assumptions, or need
to make a decision you're unsure about.

### No Time Estimates in Options

When presenting options or plans via AskUserQuestion, never include time estimates.
Focus on what each option involves, not how long it takes.
```
