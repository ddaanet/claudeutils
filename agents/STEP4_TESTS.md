# Step 4 Tests: Recursive Sub-Agent Processing

## Objective

Implement functions to discover sub-agent sessions and recursively extract feedback from all nested sessions, **including interrupted, failed, or killed agents**.

## Data Model Insights

### Agent Files Exist Before Completion

Agent session files (`agent-{id}.jsonl`) are created when an agent **starts**, not when it completes:
- Task interrupted → agent file exists with partial data
- Claude Code killed → agent file exists with partial data
- Task errors → agent file may exist

**Design Decision:** Use scan-based discovery to find all related agents, not just successfully completed ones.

### Identifying Related Agents

Agent entries contain a `sessionId` field identifying the **parent session** that spawned them:
```python
{
    "type": "user",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",  # Parent session!
    "agentId": "ae9906a",  # This agent's ID
    ...
}
```

This enables finding all agents by scanning `agent-*.jsonl` files and checking their `sessionId`.

---

## Functions to Implement

### `find_related_agent_files(session_id: str, project_dir: str) -> list[Path]`

Scan the project history directory for all `agent-*.jsonl` files that reference the given session ID. Returns agents regardless of completion status.

### `extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]`

Recursively extract feedback from a session and all its sub-agents.

---

## Test Cases (9 tests)

### Function: `find_related_agent_files`

#### 1. Test: Find agents by session ID
**Given:** Project directory with 2 agent files, both referencing session "main-123"
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns list of 2 agent file Paths

#### 2. Test: Filter out agents from other sessions
**Given:** Project directory with 3 agent files:
- agent-a1.jsonl references session "main-123"
- agent-a2.jsonl references session "other-456"
- agent-a3.jsonl references session "main-123"
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns only [agent-a1.jsonl, agent-a3.jsonl]

#### 3. Test: Empty directory returns empty list
**Given:** Project directory with no agent files
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]`

#### 4. Test: Handle malformed agent files gracefully
**Given:** Project directory with agent file containing invalid JSON
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list (logs warning about malformed file)

#### 5. Test: Empty agent file returns empty list
**Given:** Project directory with empty `agent-a1.jsonl` file (zero bytes)
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]`

---

### Function: `extract_feedback_recursively`

#### 6. Test: Top-level only (no sub-agents)
**Given:** Session with 2 substantive user messages and no related agent files
**When:** `extract_feedback_recursively()` is called
**Then:** Returns list of 2 FeedbackItems from main session only

#### 7. Test: One level of sub-agents
**Given:**
- Main session with 1 user message
- Agent file "agent-a1" with 2 user messages, referencing main session
**When:** `extract_feedback_recursively()` is called
**Then:** Returns list of 3 FeedbackItems (1 from main + 2 from agent-a1)

#### 8. Test: Two levels of nesting (sub-agent spawns sub-agent)
**Given:**
- Main session with 1 substantive user message
- Agent "a1" references main session, has 1 user message
- Agent "a2" references main session (spawned by a1), has 1 user message
**When:** `extract_feedback_recursively()` is called
**Then:** Returns list of 3 FeedbackItems (1 from each level)

#### 9. Test: Missing project directory raises FileNotFoundError
**Given:** Non-existent project directory path
**When:** `extract_feedback_recursively()` is called
**Then:** Raises FileNotFoundError

---

## Sample Test Data

### Agent Session Entry (shows parent session reference)
```python
AGENT_SESSION_ENTRY = {
    "type": "user",
    "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",  # Parent session
    "agentId": "ae9906a",  # This agent's ID
    "slug": "fluffy-cuddling-forest",
    "timestamp": "2025-12-16T08:40:00.000Z",
    "message": {
        "role": "user",
        "content": "Search for config files in the project"
    }
}
```

### Agent File Structure
```
~/.claude/projects/-Users-david-code-foo/
├── e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl  # Main session
├── agent-ae9906a.jsonl                          # Sub-agent (refs main)
└── agent-ad67fd8.jsonl                          # Sub-agent (refs main)
```

---

## Implementation Notes

1. **Agent file path pattern:** `get_project_history_dir(project_dir) / "agent-*.jsonl"`

2. **Session ID extraction:** Read first entry of each agent file, extract `sessionId` field

3. **Recursive traversal:** Agents can spawn other agents, so recursively find related agents

4. **Logging:** Use Python's `logging` module for warnings about malformed files

5. **Order:** Return feedback sorted by timestamp

6. **Existing function reuse:**
   - Use `extract_feedback_from_entry()` for each entry
   - Use `get_project_history_dir()` for path resolution
