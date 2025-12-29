# System Prompt Pattern Integration: Delegable Tasks

Tasks that can be delegated to weak agents after detailed planning by Opus. See
`design.md` for context, `tasks-opus.md` for prerequisite tasks, `drafts.md` for
preliminary module content.

**Prerequisites**: Complete Opus tasks 4-5 (finalized module content).

---

## File Creation Tasks

### 1. Create Tool Modules Directory

Create `agents/modules/src/tools/` directory.

### 2. Create Tool Module Files

Create 6 tool module files with finalized content from Opus task 4:

- `agents/modules/src/tools/read-edit.tool.md`
- `agents/modules/src/tools/bash.tool.md`
- `agents/modules/src/tools/task-agent.tool.md`
- `agents/modules/src/tools/webfetch.tool.md`
- `agents/modules/src/tools/todowrite.tool.md`
- `agents/modules/src/tools/askuser.tool.md`

Each file follows structure:

```markdown
---
semantic_type: tool_conditional
requires_tools: [ToolName]
target_rules:
  weak: N-M
---

# Module Title

## Critical (Tier 1)

...

## Important (Tier 2)

...
```

---

## File Update Tasks

### 3. Update Semantic Modules

Update existing modules with patterns from Opus task 5:

- `agents/modules/src/communication.semantic.md`
- `agents/modules/src/plan-creation.semantic.md`
- `agents/modules/src/code-quality.semantic.md`
- `agents/modules/src/tool-batching.semantic.md`

### 4. Create New Semantic Module

Create `agents/modules/src/context.semantic.md` for system-reminder handling.

---

## Documentation Tasks

### 5. Update MODULE_INVENTORY.md

Add tool modules section to `agents/modules/MODULE_INVENTORY.md`:

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

### 6. Update CATALOG.md

Update `agents/modules/src/sysprompt-reference/CATALOG.md` with:

- Scope analysis results
- Mapping from reference files to final modules
- Notes on interactive-only patterns (skipped)

---

## Detailed Planning Required

Each task above requires detailed planning before delegation:

- Exact file content (for creation tasks)
- Exact edit locations and content (for update tasks)
- Verification steps

Opus should produce detailed plans that weak agents can execute mechanically.
