# Agent Instructions

**Role-specific instructions:** See `agents/role-*.md` for specialized behaviors.
**Skill commands:** See `skills/skill-*.md` for on-demand actions.
**Current work state:** Read `agents/context.md` for active tasks and decisions.
**Architecture decisions:** See `agents/design-decisions.md` for technical rationale.

---

## Communication Rules

1. **Stop on unexpected results** - If something fails OR succeeds unexpectedly, describe expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction** - Do NOT proceed with a plan or TodoWrite list unless user explicitly says "continue" or equivalent
3. **Be explicit** - Ask clarifying questions if requirements unclear
4. **Stop at boundaries** - Complete assigned task then stop (no scope creep)

## Delegation Principle

**Delegate everything.** The orchestrator (main agent) coordinates work but does not implement directly:

1. **Break down** complex requests into discrete tasks
2. **Assign** each task to a specialized agent (role) or invoke a skill
3. **Monitor** progress and handle exceptions
4. **Synthesize** results for the user

Specialized agents focus on their domain; the orchestrator maintains context and flow.

### Model Selection for Delegation

**Rule:** Match model cost to task complexity.

- **Haiku:** Execution, implementation, simple edits, file operations
- **Sonnet:** Default for most work, balanced capability
- **Opus:** Architecture, planning, complex design decisions only

**Critical:** Never use opus for straightforward execution tasks (file creation, edits, running commands). This wastes cost and time.

### Quiet Execution Pattern

**Rule:** Execution agents report to files, not to orchestrator context.

**For haiku execution tasks:**

1. Specify output file path in task prompt (e.g., `tmp/execution-report.md` or `agents/reports/task-name.md`)
2. Instruct agent to write detailed output to that file
3. Agent returns only: filename (success) or error message (failure)
4. Use second agent to read report and provide distilled summary to user

**Goal:** Prevent orchestrator context pollution with verbose task output. Orchestrator sees only success/failure + summary, not full execution logs.

**Note:** Use `agents/` or `tmp/` directories in project for report files. Always use project-local `tmp/` (not system `/tmp/`).

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

## Roles, Rules, and Skills

**Roles** define agent behavior modes. **Rules** apply during specific actions. **Skills** are on-demand operations.

### Roles

| Role     | File                      | Purpose                    |
| -------- | ------------------------- | -------------------------- |
| planning | `agents/role-planning.md` | Design test specifications |
| code     | `agents/role-code.md`     | TDD implementation         |
| lint     | `agents/role-lint.md`     | Fix lint/type errors       |
| refactor | `agents/role-refactor.md` | Plan refactoring changes   |
| execute  | `agents/role-execute.md`  | Execute planned changes    |
| review   | `agents/role-review.md`   | Code review and cleanup    |
| remember | `agents/role-remember.md` | Update agent documentation |

### Rules (Action-Triggered)

| Rule    | File                      | Trigger                 |
| ------- | ------------------------- | ----------------------- |
| commit  | `agents/rules-commit.md`  | Before any `git commit` |
| handoff | `agents/rules-handoff.md` | Before ending a session |

### Skills (On-Demand)

| Skill | File                    | Trigger  | Purpose                        |
| ----- | ----------------------- | -------- | ------------------------------ |
| shelf | `skills/skill-shelf.md` | `/shelf` | Archive context to todo, reset |

**Loading:**
- **Roles:** Read at session start
- **Rules:** Read before the triggering action
- **Skills:** Read when user invokes the trigger command

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

