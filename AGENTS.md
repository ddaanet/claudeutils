# Agent Instructions: Claude Code Feedback Extractor

## Project Overview

**Goal:** Extract user feedback from Claude Code conversation history for retrospective analysis.

**Architecture:** Python CLI tool with two subcommands:
1. `list` - Show top-level conversation sessions with titles
2. `extract` - Extract user feedback recursively from a session

**Implementation Approach:** Test-Driven Development (TDD) with pytest, implemented in discrete steps.

**Key Technologies:**
- Python 3.14+ with full type annotations (mypy strict)
- Pydantic for data validation
- uv for dependency management
- pytest for testing
- ruff for linting
- just for task running

---

## Skills

Skills are specialized instruction sets. **Read the skill file before performing that action.**

| Skill | File | Trigger |
|-------|------|---------|
| planning | `agents/planning.md` | Before designing test specifications |
| code | `agents/code.md` | Before implementing code |
| lint | `agents/lint.md` | Before fixing `just check` errors |
| commit | `agents/commit.md` | **Before any `git commit`** |
| remember | `agents/remember.md` | Before updating documentation |
| handoff | `agents/handoff.md` | Before ending a session |

**How to load:** Read the file using the Read tool before starting the task.

---

## Key User Preferences

### Communication Patterns

1. **Request validation periodically:** After every three test-implement cycles
2. **Stop at boundaries:** Complete assigned task then stop (no scope creep)
3. **Be explicit:** Ask clarifying questions if requirements unclear
4. **Context awareness:** Prepare handoff notes for next agent/session
5. **Transparency:** Explain sub-agent strategy before launching; user may ask for transcripts
6. **Load skills proactively:** Read skill files before operations (e.g., read `agents/commit.md` before running `git commit`)

### Code Patterns

See `agents/code.md` for TDD implementation rules and `agents/lint.md` for linting rules.

### Tool Batching

1. **Batch reads:** Before reading a file, identify other files needed soon and read them together
2. **Batch writes:** Before writing, identify other changes that can be combined in one batch
3. **Update context after writes:** Include Read calls at the end of a write batch to refresh context

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
- `AGENTS.md` - This file (core rules and skill references)
- `agents/TEST_DATA.md` - Data types and sample entries for coding
- `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
- `agents/ROADMAP.md` - Future enhancement ideas

**Skills:**

- `agents/planning.md` - Test-first design skill
- `agents/code.md` - TDD implementation skill
- `agents/lint.md` - Linting and type checking skill
- `agents/commit.md` - Git commit skill
- `agents/remember.md` - Documentation and rules maintenance skill
- `agents/handoff.md` - Session handoff skill
