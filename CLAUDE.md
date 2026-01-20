# Agent Instructions

**Current work state:** Read `agents/context.md` for active tasks and decisions.
**Architecture decisions:** See `agents/design-decisions.md` for technical rationale.

---

## Workflow Selection

**Entry point:** Use `/oneshot` skill for all one-off tasks. It auto-detects methodology.

**TDD workflow** - Feature development with test-first methodology:
- **Signals:** Test-first culture, user mentions "test/TDD/red-green", behavioral verification needed
- **Route:** `/design` (TDD mode) → `/plan-tdd` → `/orchestrate` → `/vet` → `/review-analysis`
- **Detailed guide:** `agent-core/agents/tdd-workflow.md` (read when executing TDD workflow)

**Oneshot workflow** - General implementation tasks:
- **Signals:** Infrastructure, refactoring, prototyping, migrations, default case
- **Route:** `/design` → `/plan-adhoc` → `/orchestrate` → `/vet`
- **Detailed guide:** `agent-core/agents/oneshot-workflow.md` (read when executing oneshot workflow)

**Progressive discovery:** Don't preload all workflow documentation. Read detailed guides only when executing that specific workflow type. Use references as needed during execution.

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

1. **Stop on unexpected results** - If something fails OR succeeds unexpectedly, describe expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction** - Do NOT proceed with a plan or TodoWrite list unless user explicitly says "continue" or equivalent
3. **Be explicit** - Ask clarifying questions if requirements unclear
4. **Stop at boundaries** - Complete assigned task then stop (no scope creep)
5. **Use /commit skill** - Always invoke `/commit` skill when committing; it handles multi-line message format correctly
6. **No estimates unless requested** - Do NOT make estimates, predictions, or extrapolations unless explicitly requested by the user. Report measured data only.

## Error Handling

**Errors should never pass silently.**

- Do not swallow errors or suppress error output
- Errors provide important diagnostic information
- Report all errors explicitly to the user
- Never use error suppression patterns (e.g., `|| true`, `2>/dev/null`, ignoring exit codes)
- If a command fails, surface the failure - don't hide it

## Session Management

### Execute Rule (#execute)

When asked to "#execute" or "execute":
1. Load session context (same as #load)
2. Immediately perform the next pending task

This is the primary command for continuing work across sessions.

### Load Rule (#load)

When asked to "#load" or "load", read the session context files:
- `agents/session.md` - Current work state, handoff context, decisions, blockers
- `agents/context.md` - Active multi-step task context (if exists)

Do not search for these files; read them directly at these paths.

**After reading session.md, continue work automatically:**

1. **If in-progress task exists:**
   - Report status to user: "Continuing [task description]"
   - Resume work on that task

2. **If no in-progress task, but pending tasks exist:**
   - Take first pending task
   - Report to user: "Starting next task: [task description]"
   - Begin work

3. **If no pending tasks:**
   - Report status to user: "Session loaded. No pending tasks."
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

**Delegate everything.** The orchestrator (main agent) coordinates work but does not implement directly:

1. **Break down** complex requests into discrete tasks
2. **Assign** each task to a specialized agent (role) or invoke a skill
3. **Monitor** progress and handle exceptions
4. **Synthesize** results for the user

Specialized agents focus on their domain; the orchestrator maintains context and flow.

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

### Model Selection for Delegation

**Rule:** Match model cost to task complexity.

- **Haiku:** Execution, implementation, simple edits, file operations
- **Sonnet:** Default for most work, balanced capability
- **Opus:** Architecture, planning, complex design decisions only

**Critical:** Never use opus for straightforward execution tasks (file creation, edits, running commands). This wastes cost and time.

### Quiet Execution Pattern

**Rule:** Execution agents report to files, not to orchestrator context.

**For execution tasks:**

1. Specify output file path in task prompt (typically `plans/<runbook-name>/reports/<report-name>.md`)
2. Instruct agent to write detailed output to that file
3. Agent returns only: filename (success) or error message (failure)
4. Use second agent to read report and provide distilled summary to user

**Goal:** Prevent orchestrator context pollution with verbose task output. Orchestrator sees only success/failure + summary, not full execution logs.

**Note:** For runbook execution, use `plans/*/reports/` directory. For ad-hoc work, use project-local `tmp/` (not system `/tmp/`). Report naming varies with delegation pattern.

**Preferred agent:** Use `quiet-task` agent for execution tasks. It implements the quiet pattern by default (reports to files, terse returns). Avoid generic Task agents that return verbose output to orchestrator context.

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

### Task Agent Tool Usage

**Rule:** Task agents must use specialized tools, not Bash one-liners.

**When delegating tasks, remind agents to:**

- Use **LS** instead of `ls`
- Use **Grep** instead of `grep` or `rg`
- Use **Glob** instead of `find`
- Use **Read** instead of `cat`, `head`, `tail`
- Use **Write** instead of `echo >` or `cat <<EOF`
- Use **Edit** instead of `sed`, `awk`
- **NEVER use heredocs** (`<<EOF`) in bash commands - sandbox blocks them
- Use **tmp/** in project directory for temp files, NOT `/tmp/`

**Critical:** Always include this reminder in task prompts to prevent bash tool misuse.

## Tool Batching

**Planning phase (before tool calls):**
1. Identify ALL changes needed for current task
2. Group by file: same-file edits sequential, different-file edits parallel
3. For multi-edit files: list insertion points, plan bottom-to-top order (avoids line shifts)

**Execution phase:**
4. **Batch reads:** Read multiple files in one message when needed soon
5. **Different files:** Edit in parallel when independent
6. **Same file:** Edit sequentially, bottom-to-top when inserting
7. **Refresh context:** If you plan to modify a file again in next iteration, Read it in the batch

---

# Hashtag Conventions

Semantic markers for agent communication and task tracking:

## Core Hashtags

### #stop
**Indicates a hard stop point**
- Used when encountering unexpected results
- Signals that continuation requires human review
- Example: "Validation failed #stop - unclear how to proceed"

### #delegate
**Indicates task handoff**
- Used when delegating to another agent
- Includes handoff protocol and acceptance criteria
- Example: "#delegate to specialized agent for code review"

### #tools
**Indicates tool usage guidance**
- Used when explaining or constraining tool selection
- Helps maintain consistency across tasks
- Example: "#tools use Grep instead of shell grep"

### #quiet
**Indicates minimal output preferred**
- Used for routine operations with expected results
- Reduces unnecessary verbosity
- Example: "Running tests #quiet"

## Usage Patterns

### In Task Descriptions
```
"Run validation checks #tools - use Bash for git, Grep for searching"
```

### In Status Updates
```
"Tests passed #quiet - proceeding to next step"
```

### In Handoffs
```
"Implement feature #delegate to specialized agent with requirement X"
```

### In Unexpected States
```
"Configuration not found #stop - cannot determine next action"
```

## Implementation Notes

- Hashtags are semantic markers, not strict constraints
- Used in agent-to-agent communication
- Help with task routing and escalation
- Enable consistent behavior across projects

See communication.md for broader communication guidelines.

