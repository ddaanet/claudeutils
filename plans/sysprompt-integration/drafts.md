# System Prompt Pattern Integration: Draft Module Content

Draft content for tool modules and semantic module updates. Subject to revision during
Opus processing (TASKS_OPUS.md task 4-5).

---

## Tool Modules to Create

### 1. `agents/modules/src/tools/read-edit.tool.md`

```markdown
---
semantic_type: tool_conditional
requires_tools: [Read, Edit, Write]
target_rules:
  weak: 5-6
---

# Read/Edit Tool Rules

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

### Re-Read Before Editing Modified Files

If you edit file X and will edit it again in the next batch, Read it first to get
current line numbers.
```

### 2. `agents/modules/src/tools/bash.tool.md`

```markdown
---
semantic_type: tool_conditional
requires_tools: [Bash]
target_rules:
  weak: 6-8
---

# Bash Tool Rules

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

### 3. `agents/modules/src/tools/task-agent.tool.md`

```markdown
---
semantic_type: tool_conditional
requires_tools: [Task]
target_rules:
  weak: 4-6
---

# Task/Agent Delegation Rules

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
---
semantic_type: tool_conditional
requires_tools: [WebFetch]
target_rules:
  weak: 2-4
---

# WebFetch Tool Rules

## Important (Tier 2)

### Handle Redirects Explicitly

When WebFetch reports redirect to different host, make new request with redirect URL. Do
not assume original content was fetched.
```

### 5. `agents/modules/src/tools/todowrite.tool.md`

```markdown
---
semantic_type: tool_conditional
requires_tools: [TodoWrite]
target_rules:
  weak: 8-12
---

# TodoWrite Tool Rules

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

### 6. `agents/modules/src/tools/askuser.tool.md`

```markdown
---
semantic_type: tool_conditional
requires_tools: [AskUserQuestion]
target_rules:
  weak: 3-4
---

# AskUserQuestion Tool Rules

## Important (Tier 2)

### Ask When Unsure

Use AskUserQuestion when you need clarification, want to validate assumptions, or need
to make a decision you're unsure about.

### No Time Estimates in Options

When presenting options or plans via AskUserQuestion, never include time estimates.
Focus on what each option involves, not how long it takes.
```

---

## Semantic Module Updates

### tool-batching.semantic.md

**Add/clarify three execution modes (parallel/chained/sequential):**

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

---

## MODULE_INVENTORY.md Addition

```markdown
## Tool-Conditional Modules

| Module     | requires_tools    | Purpose                        |
| ---------- | ----------------- | ------------------------------ |
| read-edit  | Read, Edit, Write | File I/O preferences, batching |
| bash       | Bash              | System command restrictions    |
| task-agent | Task              | Agent delegation patterns      |
| webfetch   | WebFetch          | Redirect handling              |
| todowrite  | TodoWrite         | Progress tracking              |
| askuser    | AskUserQuestion   | Question framing               |
```
