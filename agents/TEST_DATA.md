# Test Data Reference

Code-relevant details extracted from PLAN.md for TDD implementation.

---

## Core Data Types

**FeedbackType (StrEnum):** Three types: `tool_denial`, `interruption`, `message`

**FeedbackItem (Pydantic BaseModel):**
- `timestamp`: str (ISO 8601 format)
- `session_id`: str
- `feedback_type`: FeedbackType enum value
- `content`: str (the actual feedback text)
- `agent_id`: Optional[str] = None
- `slug`: Optional[str] = None
- `tool_use_id`: Optional[str] = None (only for tool denials)

**SessionInfo:** Contains `session_id`, `first_prompt_line`, `timestamp`

---

## Path Encoding

- Path encoding: `/Users/david/code/foo` → `-Users-david-code-foo`
- Primary source: `~/.claude/projects/[ENCODED-PATH]/*.jsonl`
- Top-level sessions: UUID-named files (e.g., `e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl`)
- Sub-agent sessions: `agent-[id].jsonl` files referenced via `agentId` field

---

## Trivial Patterns

Keywords (case insensitive, with optional surrounding whitespace):
`y`, `n`, `k`, `g`, `ok`, `go`, `yes`, `no`, `continue`, `proceed`, `sure`, `okay`, `resume`

Additional trivial patterns:
- Empty string
- Whitespace only
- Single character (any)
- Slash commands: `/model`, `/clear`, `/help`

---

## Sample Entries

```python
SAMPLE_USER_MESSAGE = {
    "type": "user",
    "message": {"role": "user", "content": "Design a python script to extract user feedback"},
    "timestamp": "2025-12-16T08:39:26.932Z",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1"
}

SAMPLE_TOOL_DENIAL_MAIN = {
    "type": "user",
    "message": {
        "role": "user",
        "content": [{
            "type": "tool_result",
            "is_error": True,
            "content": "[Request interrupted by user for tool use]",
            "tool_use_id": "toolu_01Q9nwwXaokrfKdLpUDCLHt7"
        }]
    },
    "timestamp": "2025-12-16T08:43:43.872Z",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1"
}

SAMPLE_TOOL_DENIAL_SUBAGENT = {
    "type": "user",
    "message": {
        "role": "user",
        "content": [{
            "type": "tool_result",
            "content": "The user doesn't want to proceed with this tool use. The tool use was rejected (eg. if it was a file edit, the new_string was NOT written to the file). STOP what you are doing and wait for the user to tell you how to proceed.",
            "is_error": True,
            "tool_use_id": "toolu_0165cVNnbPXQCt22gTrTXnQq"
        }]
    },
    "timestamp": "2025-12-16T08:43:43.789Z",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
    "agentId": "a6755ed",
    "slug": "fluffy-cuddling-forest"
}

SAMPLE_TRIVIAL = {
    "type": "user",
    "message": {"role": "user", "content": "resume"},
    "timestamp": "2025-12-16T08:43:52.198Z",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1"
}

SAMPLE_INTERRUPTION = {
    "type": "user",
    "message": {
        "role": "user",
        "content": [{"type": "text", "text": "[Request interrupted by user for tool use]"}]
    },
    "timestamp": "2025-12-16T08:43:43.872Z",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1"
}
```
