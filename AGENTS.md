# Agent Instructions: Claude Code Feedback Extractor

## Project Overview

**Goal:** Extract user feedback from Claude Code conversation history for retrospective
analysis.

**Architecture:** Python CLI tool with two subcommands:

1. `list` - Show top-level conversation sessions with titles
2. `extract` - Extract user feedback recursively from a session

**Implementation Approach:** Test-Driven Development (TDD) with pytest, implemented in
discrete steps.

**Key Technologies:**

- Python 3.14+ with full type annotations (mypy strict)
- Pydantic for data validation
- uv for dependency management
- pytest for testing
- ruff for linting
- just for task running

---

## Roles and Rules

Roles define agent behavior modes. Rules apply during specific actions.

### Roles

| Role     | File                      | Model       | Purpose                    |
| -------- | ------------------------- | ----------- | -------------------------- |
| planning | `agents/role-planning.md` | opus/sonnet | Design test specifications |
| code     | `agents/role-code.md`     | haiku       | TDD implementation         |
| lint     | `agents/role-lint.md`     | haiku       | Fix lint/type errors       |
| refactor | `agents/role-refactor.md` | sonnet      | Plan refactoring changes   |
| execute  | `agents/role-execute.md`  | haiku       | Execute planned changes    |
| review   | `agents/role-review.md`   | sonnet      | Code review and cleanup    |
| remember | `agents/role-remember.md` | opus        | Update agent documentation |

### Rules (Action-Triggered)

| Rule    | File                      | Trigger                 |
| ------- | ------------------------- | ----------------------- |
| commit  | `agents/rules-commit.md`  | Before any `git commit` |
| handoff | `agents/rules-handoff.md` | Before ending a session |

**Loading:** Read the role file at session start. Read rule files before the triggering
action.

---

## Key User Preferences

### Communication Patterns

#### Tier 1 - Critical (Always Follow)

1. **Stop on unexpected results:** If something fails OR succeeds unexpectedly, describe
   expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction:** Do NOT proceed with a plan or TodoWrite list
   unless user explicitly says "continue" or equivalent
3. **Request validation every 3 cycles:** After every three test-implement cycles, stop
   and request confirmation

#### Tier 2 - Important

4. **Load skills proactively:** Read skill files before operations (e.g., read
   `agents/rules-commit.md` before `git commit`)
5. **Stop at boundaries:** Complete assigned task then stop (no scope creep)
6. **Be explicit:** Ask clarifying questions if requirements unclear

### Code Patterns

See `agents/role-code.md` for TDD implementation rules and `agents/role-lint.md` for
linting rules.

### Tool Batching

**Planning phase (before any tool calls):**

1. Identify ALL changes needed for the current task
2. Group by file: same-file edits are sequential, different-file edits can be parallel
3. For multi-edit files: list insertion points, plan bottom-to-top order (avoids line
   shifts)

**Execution phase:**

4. **Batch reads:** Read multiple files in one message when needed soon
5. **Different files:** Edit in parallel when independent
6. **Same file:** Edit sequentially, bottom-to-top when inserting
7. **Refresh context:** If you plan to modify a file again in the next iteration, Read
   this file in the batch.

---

## Data Model Reference

```python
class FeedbackType(StrEnum):
    TOOL_DENIAL = "tool_denial"
    INTERRUPTION = "interruption"
    MESSAGE = "message"

class FeedbackItem(BaseModel):
    timestamp: str
    session_id: str
    feedback_type: FeedbackType
    content: str
    agent_id: Optional[str] = None
    slug: Optional[str] = None
    tool_use_id: Optional[str] = None
```

---

## Quick Command Reference

```bash
# Tool usage
uv run claudeutils list                        # List all sessions
uv run claudeutils extract <prefix>            # Extract feedback by session prefix
uv run claudeutils extract <prefix> -o out.json  # Extract to file
uv run claudeutils list --project /path        # Use custom project directory

# Development workflow
just dev              # Format, check, and test
just test ...         # Run pytest only, arguments are passed to pytest
just check            # Run ruff + mypy only
just format           # Auto-format code

# Dependency management
uv add pytest         # Add dependency

# Git workflow
git status            # Check staged changes
git diff              # Review changes
git commit -m "..."   # Commit with concise message
```

---

## File Reference

- `START.md` - **Handoff entry point** (read this first on session reset)
- `AGENTS.md` - This file (core rules and role/rule definitions)
- `agents/TEST_DATA.md` - Data types and sample entries for coding
- `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
- `agents/ROADMAP.md` - Future enhancement ideas

**Roles:**

- `agents/role-planning.md` - Design test specifications
- `agents/role-code.md` - TDD implementation
- `agents/role-lint.md` - Fix lint/type errors
- `agents/role-refactor.md` - Plan refactoring changes
- `agents/role-execute.md` - Execute planned changes
- `agents/role-review.md` - Code review and cleanup
- `agents/role-remember.md` - Update agent documentation

**Rules:**

- `agents/rules-commit.md` - Git commit guidelines
- `agents/rules-handoff.md` - Session handoff guidelines
