# Plan: Extract User Feedback from Claude Code Conversation History

## Goal
Create a Python script to extract non-trivial user feedback from Claude Code conversation history for retrospective analysis. Implementation follows TDD with pytest.

## Data Sources & Schema

**Primary source:** `~/.claude/projects/[ENCODED-PATH]/*.jsonl`
- Path encoding: `/Users/david/code/foo` → `-Users-david-code-foo`
- Files: `[session-id].jsonl` (top-level sessions) and `agent-[id].jsonl` (sub-agents)
- Each line: one JSON object representing a conversation message

**Session types:**
- **Top-level sessions:** UUID-named files (e.g., `e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl`)
- **Sub-agent sessions:** `agent-[id].jsonl` files referenced via `agentId` field in entries

**Processing approach:**
- `list` subcommand: Show top-level sessions only
- `extract` subcommand: Recursively process sub-agents by following `agentId` references

**Entry types:**
- User message with text content (string)
- Tool denial with `is_error: true` in tool_result
- Request interruption with text containing "[Request interrupted"

## Core Data Types

**FeedbackType (StrEnum):** Three types: `tool_denial`, `interruption`, `message`

**FeedbackItem (Pydantic BaseModel):** Contains:
- `timestamp`: str (ISO 8601 format)
- `session_id`: str
- `feedback_type`: FeedbackType enum value
- `content`: str (the actual feedback text)
- `agent_id`: Optional[str] = None
- `slug`: Optional[str] = None
- `tool_use_id`: Optional[str] = None (only for tool denials)

## Test Plan (TDD Approach)

### Step 1: Path & Session Discovery Tests

**Function:** `encode_project_path(project_dir: str) -> str`

Test cases:
1. Input `/Users/david/code/foo` returns `-Users-david-code-foo`
2. Input `/home/user/project` returns `-home-user-project`
3. Input `/` returns `-` (root path edge case)
4. Input `relative/path` raises ValueError (requires absolute path)

**Function:** `get_project_history_dir(project_dir: str) -> Path`

Test cases:
1. Input `/Users/david/code/foo` returns `Path.home() / ".claude" / "projects" / "-Users-david-code-foo"`
2. Returns Path object type
3. Encoded portion matches `encode_project_path()` output

**Function:** `list_top_level_sessions(project_dir: str) -> list[SessionInfo]`

SessionInfo contains: session_id, first_prompt_line, timestamp

Test cases:
1. Directory with 3 UUID.jsonl files returns 3 sessions
2. Directory with UUID.jsonl and agent-*.jsonl returns only UUID sessions
3. Sessions sorted by timestamp (most recent first)
4. Extracts first non-empty user message as prompt line
5. Empty directory returns empty list
6. Missing directory raises FileNotFoundError

### Step 2: Trivial Filter Tests
**Function:** `is_trivial(text: str) -> bool`

**Trivial patterns:** `y`, `n`, `k`, `g`, `ok`, `go`, `yes`, `no`, `continue`, `proceed`, `sure`, `okay`, `resume`

Test cases:
1. Empty string → True
2. Whitespace only → True
3. Single character → True
4. "y", "n", "ok", "go" (case insensitive) → True
5. "yes", "continue", "resume" → True
6. Slash commands "/model", "/clear" → True
7. Substantive text "Design a python script" → False
8. Mixed case "YeS" → True
9. Text with leading/trailing whitespace " continue " → True

### Step 3: Message Parsing Tests
**Function:** `extract_feedback_from_entry(entry: dict) -> FeedbackItem | None`

Test cases using sample data:
1. **Non-user message** (type="assistant") returns None
2. **Trivial user message** ("resume") returns None
3. **Substantive user message** returns FeedbackItem where:
   - feedback_type equals MESSAGE
   - timestamp equals entry timestamp
   - session_id equals entry sessionId
   - content equals message content string
   - agent_id equals entry agentId (or None if missing)
   - slug equals entry slug (or None if missing)
4. **Tool denial (main session)** returns FeedbackItem where:
   - feedback_type equals TOOL_DENIAL
   - tool_use_id equals content[0] tool_use_id
   - content equals denial error message
5. **Tool denial (sub-agent)** returns FeedbackItem where:
   - agent_id equals "a6755ed"
   - slug equals "fluffy-cuddling-forest"
   - content equals full denial message
6. **Request interruption** returns FeedbackItem where:
   - feedback_type equals INTERRUPTION
   - content contains "[Request interrupted"
7. **Missing sessionId** returns FeedbackItem with session_id=""
8. **Malformed content** (empty list) returns None
9. **Pydantic validation:** Invalid timestamp format raises ValidationError

### Step 4: Recursive Session Processing Tests
**Function:** `find_sub_agent_sessions(session_file: Path) -> list[str]`

Test cases:
1. Session with 2 agent tool calls returns 2 agent IDs
2. Session with no agents returns empty list
3. Duplicate agent IDs deduplicated
4. Only extracts from tool_use entries where name="Task"

**Function:** `extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]`

Test cases:
1. **Top-level only:** Session with no sub-agents returns only main feedback
2. **One level:** Session with 1 sub-agent returns main + sub-agent feedback
3. **Two levels:** Session with sub-agent that spawns another agent returns all three
4. **Cycle detection:** Circular agent references don't cause infinite loop
5. **Missing agent file:** References to non-existent agent-*.jsonl logged as warning
6. **Empty session:** Session with no user messages returns empty list

### Step 5: CLI Subcommands Tests

**Subcommand:** `list [--project PATH]`

Test cases:
1. **No project flag:** Uses current directory
2. **With --project:** Uses specified directory
3. **Output format:** Each line shows: `[session_id_prefix] Title text...`
4. **Session ID prefix:** First 8 characters of UUID
5. **Title extraction:** First line of first user message (non-meta)
6. **Sorted output:** Most recent session first
7. **No history:** Prints "No sessions found" to stderr
8. **Long titles:** Truncates to 80 characters with "..."

**Subcommand:** `extract SESSION_PREFIX [--project PATH] [--output FILE]`

Test cases:
1. **No flags:** Extracts from current project, outputs to stdout
2. **With --project:** Uses specified directory
3. **With --output:** Writes JSON to file
4. **Session prefix match:** "e12d203f" matches "e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl"
5. **Multiple matches:** Prints error "Multiple sessions match prefix"
6. **No match:** Prints error "No session found with prefix"
7. **Recursive processing:** Includes feedback from all sub-agents
8. **Sorted output:** Results sorted by timestamp
9. **JSON format:** Valid JSON array with all FeedbackItem fields
10. **Integration test:** Extract from real session with 2 sub-agents, verify count

## Files to Create & Dependencies

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Core implementation | ~120 |
| `test_main.py` | Pytest test suite | ~200 |
| `pyproject.toml` | uv project config | ~15 |

**Dependencies:** `uv add pytest pydantic`

## Implementation Steps (TDD)
1. **Step 1**: Path encoding & session discovery + tests
2. **Step 2**: Trivial filter + tests
3. **Step 3**: Message parsing + tests
4. **Step 4**: Recursive sub-agent processing + tests
5. **Step 5**: CLI subcommands (list/extract) + integration tests

## CLI Usage

```bash
# List all sessions in current project
python main.py list

# List sessions from specific project
python main.py list --project /path/to/project

# Extract feedback from session (by prefix)
python main.py extract e12d203f

# Extract with output to file
python main.py extract e12d203f --output feedback.json
```

---

## Test Data (from real logs - not counted in plan length)

**Sample entries for tests:**
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

