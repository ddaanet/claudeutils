# Agent Instructions: Claude Code Feedback Extractor

## Project Overview

**Goal:** Extract user feedback from Claude Code conversation history for retrospective analysis.

**Architecture:** Python CLI tool with two subcommands:
1. `list` - Show top-level conversation sessions with titles
2. `extract` - Extract user feedback recursively from a session

**Implementation Approach:** Test-Driven Development (TDD) with pytest, implemented in discrete steps.

**Key Technologies:**
- Python 3.x with full type annotations (mypy strict)
- Pydantic for data validation
- uv for dependency management
- pytest for testing
- ruff for linting
- just for task running

## Development Methodology

### Test-Driven Development Cycle

**Critical:** Always follow Red-Green-Refactor cycle:

1. Write ONE test
2. Run test and see it FAIL (Red)
3. Write minimal code to make it PASS (Green)
4. Refactor if needed
5. **Request user validation before continuing**
6. Repeat with next test

🚫 **DO NOT** write all tests upfront then implement
✅ **DO** request confirmation after EACH test-implement cycle

### Implementation Steps

The project follows a 5-step TDD plan:
1. Path encoding & session discovery (✅ COMPLETE)
2. Trivial message filter (⏳ NEXT)
3. Message parsing
4. Recursive sub-agent processing
5. CLI subcommands

Each step has detailed test specifications in separate files (e.g., `STEP1_TESTS.md`).

## Code Quality Standards

### Type Safety (Non-negotiable)
- Full mypy strict mode required
- All parameters and return types must have type annotations
- No `Any` type unless justified with comment
- If using `type: ignore`, include line comment explaining why

### Linting & Style
- Ruff linting must pass with zero warnings
- No `noqa` suppressions without explanation
- Docstrings in imperative mood ("Extract content" not "Extracts content")
- Use specific type annotations (`list[str]`, not bare `list`)

### Testing Standards
- All tests in `tests/` directory
- Test fixtures should return direct values, not Generators
- Use proper pytest parametrization for similar test cases
- Test names should clearly describe what they verify

## Tooling Preferences

### Dependency Management
- **Always use `uv`** for all package operations
- Add dependencies: `uv add package-name`
- Sync environment: `uv sync`
- Run commands: `uv run command`

### Task Runner
Use `justfile` for common tasks:
```bash
just test      # Run pytest
just check     # Run ruff + mypy
just format    # Auto-format with ruff
just dev       # Run all (format, check, test)
```

### File Organization
- Implementation: `src/claudeutils/main.py`
- Tests: `tests/test_main.py`
- Configuration: `pyproject.toml`
- Plans: `PLAN.md` and `STEP*_TESTS.md`

## Git Commit Standards

### Commit Message Format
- **Concise:** Focus on WHAT changed and WHY
- **No methodology details:** Don't mention "with TDD" or implementation approach
- **No vendor credits:** Never mention "Claude", "Anthropic", or "AI-assisted"
- **Design rationale:** Include reasoning for non-obvious changes

### Examples

❌ **Bad:**
```
Implement Step 1 with TDD using pytest

Generated with Claude Code assistance
```

✅ **Good:**
```
Implement path encoding and session discovery

Add functions to encode project paths and list top-level sessions,
sorted by timestamp for easy discovery of recent conversations.
```

## Key User Preferences

### Communication Patterns
1. **Request validation frequently:** After each test-implement cycle
2. **Stop at boundaries:** Complete assigned task then stop (no scope creep)
3. **Be explicit:** Ask clarifying questions if requirements unclear
4. **Context awareness:** Prepare handoff notes for next agent/session

### Code Patterns
1. **Minimal implementation:** Write only what's needed to pass current test
2. **No premature optimization:** Solve current problem, not hypothetical future ones
3. **No suppression shortcuts:** If linter/type checker complains, fix properly
4. **Explain ignores:** Any `type: ignore` must have comment explaining what's intentional

### Documentation
1. **Update feedback files:** Add new user feedback to `USER_FEEDBACK_SESSION.md`
2. **Update handoff files:** Keep `agents/STEP*_HANDOFF.md` current with progress
3. **Avoid test counts:** Use `just test` for status, not hardcoded numbers in docs

## Session Handoff Protocol

New session start: `/clear @START.md`

This loads `START.md` which references:
1. Core context (AGENTS.md, PLAN.md)
2. Current task spec and progress notes
3. Quick commands for status checks

**Key principle:** Documentation should not duplicate dynamic state. Run `just test` to see current test counts instead of maintaining them in markdown.

## Common Anti-Patterns to Avoid

🚫 **DON'T:**
- Write all tests before implementation
- Skip user validation checkpoints
- Use `noqa` comments without explanation
- Mention TDD/methodology in commit messages
- Credit Claude/Anthropic in any output
- Suppress type warnings without comments
- Continue past assigned task scope

✅ **DO:**
- One test at a time with validation
- Stop when task complete
- Explain all ignores/suppressions
- Keep commits focused and concise
- Update documentation with feedback
- Request clarification when uncertain

## Quick Command Reference

```bash
# Development workflow
just dev              # Format, check, and test
just test             # Run pytest only
just check            # Run ruff + mypy only
just format           # Auto-format code

# Dependency management
uv add pytest         # Add dependency
uv sync               # Sync environment
uv run pytest -v      # Run with options

# Git workflow
git status            # Check staged changes
git diff              # Review changes
git commit -m "..."   # Commit with concise message
```

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

## File Reference

- `START.md` - **Handoff entry point** (read this first on session reset)
- `AGENTS.md` - This file (rules and preferences)
- `PLAN.md` - Full implementation plan
- `STEP*_TESTS.md` - Test specifications per step
- `agents/STEP*_HANDOFF.md` - Progress notes for in-progress steps
- `agents/STEP*_COMPLETION.md` - Completion notes for finished steps
- `agents/NEXT_AGENT_NOTES.md` - Cross-session learnings
