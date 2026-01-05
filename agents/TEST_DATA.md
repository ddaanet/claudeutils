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

---

## Markdown Cleanup Examples

The markdown module preprocesses Claude-generated markdown output before dprint
formatting. These examples show common patterns and transformations.

### Checklist Detection

**Input:**

```
✅ Issue #1: XPASS tests visible
✅ Issue #2: Setup failures captured
❌ Issue #3: Not fixed yet
```

**Output:**

```
- ✅ Issue #1: XPASS tests visible
- ✅ Issue #2: Setup failures captured
- ❌ Issue #3: Not fixed yet
```

### Code Block Nesting

**Input:**

````
```markdown
# Example
```python
code
```
```
````

**Output:**

`````
````markdown
# Example
```python
code
```
````
`````

**Error Case (Invalid):**

````
```python
def foo():
    """
    Example:
    ```
    code
    ```
    """
```

Error: Inner fence detected in non-markdown block (prevents dprint failure)
````

### Metadata List Indentation

**Input:**

```
**Plan Files:**
- `plans/phase-1.md`
- `plans/phase-2.md`
```

**Output:**

```
- **Plan Files:**
  - `plans/phase-1.md`
  - `plans/phase-2.md`
```

---

### Pipeline Flow

```
Claude generates markdown
  ↓
markdown.py preprocessor (fix structure)
  ├─ fix_dunder_references
  ├─ fix_metadata_blocks
  ├─ fix_warning_lines (extended)
  ├─ fix_nested_lists
  ├─ fix_metadata_list_indentation (new)
  ├─ fix_numbered_list_spacing
  └─ fix_markdown_code_blocks (new)
  ↓
dprint formatter (consistent style)
  ↓
Final markdown output
```
