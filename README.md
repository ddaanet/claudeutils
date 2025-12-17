# Claude Code Feedback Extractor

Extract user feedback from Claude Code conversation history for retrospective analysis.

## Quick Reference Files

| File | Purpose |
|------|---------|
| `agents/PLAN.md` | Full implementation plan with TDD test specifications |
| `agents/STATUS.md` | Current project status and next steps |
| `agents/USER_FEEDBACK_SESSION.md` | All user feedback from planning session |
| `agents/RESEARCH_FINDINGS.md` | Technical findings about conversation history storage |

## Project Goal

Create a Python CLI tool with two subcommands:
1. `list` - Show top-level conversation sessions with titles
2. `extract` - Extract user feedback recursively from a session

## Implementation Status

**Phase:** Planning Complete ✅
**Next:** Step 1 - Path encoding & session discovery tests

## Quick Start (After Implementation)

```bash
# Install dependencies
uv add pytest pydantic

# List sessions
python main.py list

# Extract feedback
python main.py extract e12d203f --output feedback.json
```

## Data Model

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

## Key Features

- Recursively processes sub-agent sessions
- Filters out trivial responses (y, n, continue, etc.)
- Validates input with Pydantic
- Outputs structured JSON
- Session prefix matching for easy extraction

## Files to Implement

- `main.py` (~120 lines)
- `test_main.py` (~200 lines)
- `pyproject.toml` (~15 lines)

See `agents/PLAN.md` for detailed test specifications and `agents/STATUS.md` for step-by-step implementation guide.
