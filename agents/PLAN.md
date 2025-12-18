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

**Detailed test specification:** See `STEP2_TESTS.md` for comprehensive TDD test plan (12 tests)

Test case summary:
1. Empty string → True
2. Whitespace only (spaces, tabs, newlines) → True
3. Single character (any char) → True
4. Yes/no variants: "y", "n", "yes", "no" (case insensitive) → True
5. Short keywords: "ok", "k", "go", "g" (case insensitive) → True
6. Continuation keywords: "continue", "proceed", "sure", "okay", "resume" → True
7. Keywords with whitespace: " continue ", "\tok\t" → True
8. Slash commands: "/model", "/clear", "/help" → True
9. Substantive text: "Design a python script" → False
10. Words containing keywords: "yesterday", "continuous", "going" → False
11. Sentences with keywords: "yes I think that works" → False
12. Mixed case exact matches: "YeS" → True, "Yes please" → False

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

**Function:** `find_related_agent_files(session_id: str, project_dir: str) -> list[Path]`

Scan-based discovery finds ALL related agents, including interrupted/failed/killed ones (agent files exist before task completion).

Test cases:
1. Find agents by session ID (2 agent files referencing same session)
2. Filter out agents from other sessions
3. Empty directory returns empty list
4. Handle malformed agent files gracefully
5. Empty agent file returns empty list

**Function:** `extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]`

Test cases:
1. **Top-level only:** Session with no sub-agents returns only main feedback
2. **One level:** Session with 1 sub-agent returns main + sub-agent feedback
3. **Two levels:** Session with sub-agent that spawns another agent returns all three
4. **Missing directory:** Raises FileNotFoundError

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

## Project Structure (After Refactoring)

### Source Modules (6 files, all < 400 lines)

| File | Purpose | Lines |
|------|---------|-------|
| `src/claudeutils/models.py` | Pydantic models and enums | 33 |
| `src/claudeutils/paths.py` | Path encoding utilities | 19 |
| `src/claudeutils/parsing.py` | Content extraction and feedback parsing | 168 |
| `src/claudeutils/discovery.py` | Session and agent file discovery | 170 |
| `src/claudeutils/extraction.py` | Recursive feedback extraction | 53 |
| `src/claudeutils/cli.py` | CLI entry point | 5 |

### Test Modules (6 files, all < 400 lines)

| File | Purpose | Lines |
|------|---------|-------|
| `tests/test_models.py` | Pydantic validation tests | 25 |
| `tests/test_paths.py` | Path encoding tests | 50 |
| `tests/test_parsing.py` | Parsing and filtering tests | 236 |
| `tests/test_discovery.py` | Session/agent ID discovery tests | 301 |
| `tests/test_agent_files.py` | Agent file discovery tests | 126 |
| `tests/test_extraction.py` | Recursive extraction tests | 155 |

### Configuration & Documentation

| File | Purpose |
|------|---------|
| `pyproject.toml` | uv project config with dependencies |
| `STEP*_TESTS.md` | Detailed TDD test specifications |
| `agents/REFACTORING_COMPLETION.md` | File split completion notes |

**Dependencies:** `uv add pytest pydantic` (already installed)

## Implementation Steps (TDD)
1. **Step 1**: Path encoding & session discovery + tests (✅ COMPLETE)
   - See `STEP1_TESTS.md` for detailed test specifications
   - See `agents/STEP1_COMPLETION.md` for completion notes
2. **Step 2**: Trivial filter + tests (✅ COMPLETE)
   - See `STEP2_TESTS.md` for detailed test specifications
3. **Step 3**: Message parsing + tests (✅ COMPLETE)
   - See `STEP3_TESTS.md` for detailed test specifications
   - See `agents/STEP3_COMPLETION.md` for completion notes
4. **Step 4**: Recursive sub-agent processing + tests (✅ COMPLETE)
   - See `STEP4_TESTS.md` for detailed test specifications (13 tests)
   - See `agents/STEP4_COMPLETION.md` for completion notes
   - Scan-based discovery: finds interrupted/failed/killed agents
5. **Step 5**: CLI subcommands (list/extract) + integration tests (⏳ NEXT)

---

## Future Features (Roadmap)

### user-prompt MCP Tool Support

**Goal:** Extract user feedback from `user_prompt` tool results in session files.

**Reference:** https://github.com/nazar256/user-prompt-mcp

**Status:** Pending - MCP not yet installed, sample data unavailable.

**How it works:**
- The `user_prompt` MCP tool allows Claude to request input from the user
- Tool invocations and results appear in the session JSONL files (like any other tool)
- Extract user responses from `tool_result` entries where tool name is `user_prompt`

**Scope:**
- Detect `user_prompt` tool uses in session entries
- Extract user responses from corresponding tool results
- Classify as a new FeedbackType (e.g., `MCP_PROMPT`)

### Session Summary Extraction

**Goal:** Extract a summary of a session for process compliance analysis.

**Output format:**
- Tool uses (without full inputs/outputs)
- User inputs
- Key assistant outputs
- Timeline of interactions

**Use case:** Analyze whether agents followed expected workflows, identify deviations from standard procedures.

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

