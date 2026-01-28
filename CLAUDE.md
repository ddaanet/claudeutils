# Agent Instructions

## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Implementation tasks** (code, files, scripts, migrations, refactoring) → Use `/oneshot` skill
- **Workflow in progress** (check session.md) → Continue from current state

The `/oneshot` skill auto-detects methodology and complexity, routing to appropriate workflow.

**TDD workflow** - Feature development with test-first methodology:
- **Signals:** Test-first culture, user mentions "test/TDD/red-green", behavioral verification needed
- **Route:** `/design` (TDD mode) → `/plan-tdd` → [tdd-plan-reviewer] → [apply fixes if needed] → **prepare-runbook.py** → `/orchestrate` → `/vet`
- **Review:** tdd-plan-reviewer agent checks for prescriptive code and RED/GREEN violations
- **CRITICAL:** Must run prepare-runbook.py after review (and fixes) before `/orchestrate` - generates step files and execution artifacts

**Oneshot workflow** - General implementation tasks:
- **Signals:** Infrastructure, refactoring, prototyping, migrations, default case
- **Route:** `/design` → `/plan-adhoc` → `/orchestrate` → `/vet`
- **Detailed guide:** `agent-core/agents/oneshot-workflow.md` (read when executing oneshot workflow)

**Progressive discovery:** Don't preload all workflow documentation. Read detailed guides only when executing that specific workflow type. Use references as needed during execution.

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

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What the user wants to accomplish |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Step-by-step implementation instructions (previously called "plan") |
| **Step** | Individual unit of work within a runbook |
| **Runbook prep** | 4-point process: Evaluate, Metadata, Review, Split |

**Note on directory naming:** The `plans/` directory is a historical convention and remains unchanged. It contains runbooks, step files, and execution artifacts.

---

## Communication Rules

@agent-core/fragments/communication.md

**Additional communication rules:**
- **Token economy** - Do NOT repeat file contents in responses. Give file references (path:line or path) instead. Be concise.
- **Avoid numbered lists** - Use bullets unless sequencing/ordering matters. Numbered lists cause renumbering churn when edited.
- **Use /commit skill** - Always invoke `/commit` skill when committing; it handles multi-line message format correctly. Use `/gitmoji` before `/commit` for emoji-prefixed messages
- **No estimates unless requested** - Do NOT make estimates, predictions, or extrapolations unless explicitly requested by the user. Report measured data only.

## Error Handling

**Errors should never pass silently.**

- Do not swallow errors or suppress error output
- Errors provide important diagnostic information
- Report all errors explicitly to the user
- Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`, ignoring exit codes)
- If a command fails, surface the failure - don't hide it

**Exception:** In bash scripts using token-efficient pattern, `|| true` is used to handle expected non-zero exits (grep no-match, diff differences). See `/token-efficient-bash` skill.

## Bash Scripting

@agent-core/fragments/bash-strict-mode.md

## File System Rules

**Use project-local `tmp/` directory, NOT system `/tmp/`**

- **CRITICAL:** All temporary files must go in `<project-root>/tmp/`, never in `/tmp/` or `/tmp/claude/`
- Rationale: Sandbox restrictions, project isolation, cleanup control
- Permission enforcement: `Write(/tmp/*)` is denied in settings.json
- For runbook execution: Use `plans/*/reports/` directory
- For ad-hoc work: Use project-local `tmp/`

## Session Management

### Execute Rule (#execute)

When asked to "#execute" or "execute":
- Load session context (same as #load)
- Immediately perform the next pending task

This is the primary command for continuing work across sessions.

**If in-progress task exists:**
- Report status to user: "Continuing [task description]"
- Resume work on that task

**If no in-progress task, but pending tasks exist:**
- Take first pending task
- Report to user: "Starting next task: [task description]"
- Begin work

**If no pending tasks:**
- Report status to user: "No pending tasks."
- Wait for instructions

**Task status notation in session.md:**
- `- [ ]` = Pending task
- `- [x]` = Completed task
- `- [>]` = In-progress task (optional, or use bold/italics)

This enables seamless multi-session workflows with automatic continuation.

## Project Structure

### agent-core Path Rule

**CRITICAL:** Always make changes in `~/code/claudeutils/agent-core/`, NOT `~/code/agent-core/`

- `~/code/agent-core/` is a separate git repository (submodule source)
- `~/code/claudeutils/agent-core/` is the local working copy within this project
- All development work must happen in the claudeutils copy
- Never modify files in `~/code/agent-core/` directly

## Delegation Principle

@agent-core/fragments/delegation.md

### Script-First Evaluation

**Rule:** Before delegating a task to an agent, evaluate if it can be performed by a simple script.

**Evaluation criteria:**
- **≤25 lines**: Execute directly with Bash - don't delegate to agent
  - Examples: File moves, directory creation, symlinks, simple diffs, basic git operations
- **25-100 lines**: Consider delegating with prose description, or write script if logic is straightforward
- **>100 lines or complex logic**: Delegate to agent with clear requirements

**Critical:** Simple file operations (mv, cp, ln, mkdir, diff) should NEVER be delegated to agents. Execute them directly.

**Examples:**
- ❌ Wrong: Delegate "move files and create symlinks" to haiku agent
- ✅ Correct: Execute `mkdir -p target/ && mv source/* target/ && ln -s ../target source/`

**Why this matters:**
- Agent invocations have overhead (context, prompting, potential errors)
- Simple scripts are faster, more reliable, and easier to verify
- Saves tokens and execution time
- Reduces risk of misinterpretation

**Reference:** See `/plan-adhoc` skill Point 1 for detailed script evaluation guidance.

### Pre-Delegation Checkpoint

Before invoking Task tool, verify:
- Model matches stated plan (haiku/sonnet/opus)
- If changing model, state reason explicitly

### Commit Agent Delegation Pattern

**Rule:** When delegating commits, orchestrator analyzes changes and drafts message, agent executes.

**Orchestrator (sonnet) responsibilities:**
1. Run `git diff HEAD` to review changes
2. Analyze what changed and why
3. Draft commit message following format (imperative, 50-72 chars, bullet details)
4. Delegate to commit agent with literal message

**Delegation format:**
```
Invoke commit agent with prompt:
"Commit with message: '<exact commit message>'"
```

**Agent (haiku) returns:**
- Success: `<commit-hash>` (e.g., "abc123f")
- Failure: `Error: <diagnostic info>`

**Benefits:**
- Keeps orchestrator context lean (~20 tokens vs ~1000+)
- Commit analysis doesn't pollute step execution context
- Git command output stays in agent transcript
- Aligns with quiet execution pattern

**Example:**
```
Orchestrator analyzes: "Added 3 files, changed authentication logic"
Orchestrator drafts: "Add OAuth2 authentication\n\n- Add login endpoint\n- Add token validation\n- Add refresh token logic"
Orchestrator delegates: commit agent with literal message
Agent returns: "a7f38c2"
```

### Skill Development

**Rule:** When creating, editing, or discussing skills, start by loading the `plugin-dev:skill-development` skill.

**Why:** The skill-development skill provides:
- Skill structure and frontmatter guidance
- Progressive disclosure patterns
- Triggering condition best practices
- Integration with Claude Code plugin system

**Usage:** Invoke the skill before beginning skill work to load context and patterns.

## Tool Batching

@agent-core/fragments/tool-batching.md
