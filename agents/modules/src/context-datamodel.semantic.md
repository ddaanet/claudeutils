# Context Data Model Module

---
author_model: claude-opus-4-5-20251101
semantic_type: project_context
expansion_sensitivity: low
target_rules:
  strong: 2-3
  standard: 3-4
  weak: 4-6
---

## Semantic Intent

Define the core data structures used throughout the project. Agents need to understand
these types to implement features correctly.

---

## Core Types

### FeedbackType Enum

```python
class FeedbackType(StrEnum):
    TOOL_DENIAL = "tool_denial"      # User denied a tool use request
    INTERRUPTION = "interruption"    # User interrupted agent execution
    MESSAGE = "message"              # User sent a text message
```

### FeedbackItem Model

```python
class FeedbackItem(BaseModel):
    timestamp: str                   # ISO format timestamp
    session_id: str                  # Parent session identifier
    feedback_type: FeedbackType      # Type of feedback
    content: str                     # The feedback text/reason
    agent_id: Optional[str] = None   # Sub-agent if applicable
    slug: Optional[str] = None       # Session slug/title
    tool_use_id: Optional[str] = None  # Tool use that was denied
```

---

## Usage Notes

- All models use Pydantic for validation
- Timestamps are ISO 8601 format strings
- Session IDs are directory names in the Claude storage format
- Tool use IDs reference specific tool invocations that were denied
