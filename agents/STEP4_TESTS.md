# Step 4 Tests: Recursive Sub-Agent Processing

## Objective

Implement functions to discover sub-agent sessions and recursively extract feedback from all nested sessions, **including interrupted, failed, or killed agents**.

## TDD Iteration Rules

**CRITICAL:** Each test must require writing NEW code. If a test passes without adding code, the test sequence is wrong.

**Enforcement:**
1. Write test N
2. Run it - must FAIL
3. Write MINIMAL code to pass test N only
4. Test N passes, but test N+1 must still fail
5. Move to test N+1

If implementing test N also makes test N+1 pass, the tests are poorly ordered.

---

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

## Test Cases (13 tests)

### Group A: `find_related_agent_files` - Basic Discovery (Tests 1-5)

#### Test 1: `test_find_agents_empty_directory`
**Given:** History directory exists but contains no agent files
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]`

**Implementation scope:**
- Get history directory path
- List files matching `agent-*.jsonl` pattern
- Return empty list when no matches

---

#### Test 2: `test_find_agents_no_matching_session`
**Given:** History directory with one agent file referencing session "other-456"
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]`

**Implementation scope:**
- Read first line of agent file
- Parse JSON
- Check if `sessionId` matches target
- Return empty list if no match

**Fixture data:**
```python
# agent-a1.jsonl (first line)
{"type":"user","sessionId":"other-456","agentId":"a1","message":{"content":"test"},"timestamp":"2025-12-16T10:00:00.000Z"}
```

---

#### Test 3: `test_find_agents_single_match`
**Given:** History directory with one agent file referencing session "main-123"
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns list containing one Path to `agent-a1.jsonl`

**Implementation scope:**
- When sessionId matches, add file path to results list
- Return list of matching Paths

**Fixture data:**
```python
# agent-a1.jsonl
{"type":"user","sessionId":"main-123","agentId":"a1","message":{"content":"test"},"timestamp":"2025-12-16T10:00:00.000Z"}
```

---

#### Test 4: `test_find_agents_multiple_matches_filters_correctly`
**Given:** History directory with 3 agent files:
- `agent-a1.jsonl` → session "main-123"
- `agent-a2.jsonl` → session "other-456"
- `agent-a3.jsonl` → session "main-123"

**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns list `[agent-a1.jsonl, agent-a3.jsonl]` (only matching files)

**Implementation scope:**
- Loop through all agent files
- Filter based on sessionId match
- Collect all matching paths

---

#### Test 5: `test_find_agents_empty_file`
**Given:** History directory with empty `agent-a1.jsonl` file (0 bytes)
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]` (skips file, no error)

**Implementation scope:**
- Handle empty files gracefully
- Skip files that can't be read
- Continue processing other files

---

### Group B: `find_related_agent_files` - Error Handling (Tests 6-7)

#### Test 6: `test_find_agents_malformed_json`
**Given:** History directory with `agent-a1.jsonl` containing invalid JSON: `{invalid json`
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]` and logs warning about malformed file

**Implementation scope:**
- Wrap JSON parsing in try/except
- Log warning using Python's `logging` module
- Continue processing (don't crash)

**Implementation hint:**
```python
import logging
logger = logging.getLogger(__name__)
# In function:
try:
    entry = json.loads(line)
except json.JSONDecodeError:
    logger.warning(f"Malformed JSON in {file_path}")
    continue
```

---

#### Test 7: `test_find_agents_missing_session_id_field`
**Given:** Agent file with valid JSON but missing `sessionId` field:
```json
{"type":"user","agentId":"a1","message":{"content":"test"}}
```
**When:** `find_related_agent_files("main-123", project_dir)` is called
**Then:** Returns empty list `[]` (skips file with missing field)

**Implementation scope:**
- Check for presence of `sessionId` key before comparing
- Skip files missing required field

---

### Group C: `extract_feedback_recursively` - Error Cases (Test 8)

#### Test 8: `test_extract_recursive_missing_project_directory`
**Given:** Non-existent project directory path
**When:** `extract_feedback_recursively("main-123", "/nonexistent/path")` is called
**Then:** Raises `FileNotFoundError`

**Implementation scope:**
- Check if history directory exists before processing
- Raise FileNotFoundError with clear message if not found

---

### Group D: `extract_feedback_recursively` - Basic Extraction (Tests 9-10)

#### Test 9: `test_extract_recursive_no_messages_no_agents`
**Given:**
- Session file exists but contains only non-user entries (assistant messages only)
- No agent files
**When:** `extract_feedback_recursively("main-123", project_dir)` is called
**Then:** Returns empty list `[]`

**Implementation scope:**
- Read session file
- Parse entries
- Use existing `extract_feedback_from_entry()` function
- Return results (empty in this case)
- Do NOT implement agent discovery yet

**Fixture data:**
```python
# main-123.jsonl
{"type":"assistant","message":{"content":"Hello"},"timestamp":"2025-12-16T10:00:00.000Z"}
```

---

#### Test 10: `test_extract_recursive_top_level_only`
**Given:**
- Session file with 2 user messages
- No agent files
**When:** `extract_feedback_recursively("main-123", project_dir)` is called
**Then:** Returns list of 2 `FeedbackItem` objects from main session only

**Implementation scope:**
- Extract feedback from main session file
- Return list sorted by timestamp
- Still no agent discovery

**Fixture data:**
```python
# main-123.jsonl
{"type":"user","message":{"content":"First message"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}
{"type":"user","message":{"content":"Second message"},"timestamp":"2025-12-16T11:00:00.000Z","sessionId":"main-123"}
```

---

### Group E: `extract_feedback_recursively` - Agent Recursion (Tests 11-13)

#### Test 11: `test_extract_recursive_one_level_of_agents`
**Given:**
- Main session with 1 user message
- Agent file `agent-a1.jsonl` with 1 user message, referencing main session
**When:** `extract_feedback_recursively("main-123", project_dir)` is called
**Then:** Returns list of 2 FeedbackItems (1 from main + 1 from agent)

**Implementation scope:**
- Call `find_related_agent_files()` to discover agents
- For each agent file, extract feedback
- Combine main session feedback + agent feedback
- Sort by timestamp

**Fixture data:**
```python
# main-123.jsonl
{"type":"user","message":{"content":"Main message"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"main-123"}

# agent-a1.jsonl
{"type":"user","sessionId":"main-123","agentId":"a1","message":{"content":"Agent message"},"timestamp":"2025-12-16T10:05:00.000Z"}
```

---

#### Test 12: `test_extract_recursive_multiple_agents_same_level`
**Given:**
- Main session with 1 user message
- Agent file `agent-a1.jsonl` with 1 user message
- Agent file `agent-a2.jsonl` with 1 user message
- Both agents reference main session
**When:** `extract_feedback_recursively("main-123", project_dir)` is called
**Then:** Returns list of 3 FeedbackItems (1 main + 2 agents), sorted by timestamp

**Implementation scope:**
- Process multiple agent files
- Combine all feedback
- Ensure proper sorting

---

#### Test 13: `test_extract_recursive_nested_agents`
**Given:**
- Main session "main-123" with 1 user message
- Agent "a1" with sessionId="main-123", has 1 user message
- Agent "a2" with sessionId="a1" (nested!), has 1 user message
**When:** `extract_feedback_recursively("main-123", project_dir)` is called
**Then:** Returns list of 3 FeedbackItems (all levels combined)

**Implementation scope:**
- Implement true recursion
- For each agent found, recursively call `find_related_agent_files()` using agentId as sessionId
- Build complete tree of feedback
- Return flattened, sorted list

**Important:** Agent IDs can be session IDs for their children. The recursion pattern:
```python
def extract_feedback_recursively(session_id, project_dir):
    # Extract from main session
    feedback = extract_from_session_file(session_id)

    # Find and process direct child agents
    agent_files = find_related_agent_files(session_id, project_dir)
    for agent_file in agent_files:
        agent_id = extract_agent_id(agent_file)
        # Recursive call using agent_id as session
        feedback.extend(extract_feedback_recursively(agent_id, project_dir))

    return sorted(feedback, key=lambda x: x.timestamp)
```

---

## Test Fixture Template

Use this pattern in `test_main.py` for Step 4 tests:

```python
@pytest.fixture
def temp_history_dir(tmp_path, monkeypatch):
    """Mock history directory for agent file testing"""
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    # Mock get_project_history_dir to return our temp directory
    def mock_get_history(proj):
        return history_dir

    monkeypatch.setattr("main.get_project_history_dir", mock_get_history)

    return tmp_path / "project", history_dir
```

---

## Implementation Notes

### For `find_related_agent_files`

1. **File pattern:** Use `history_dir.glob("agent-*.jsonl")` to find agent files
2. **First-line parsing:** Only read first line of each agent file for sessionId check
3. **Path return:** Return list of Path objects, not strings
4. **Error resilience:** Wrap file operations in try/except, log warnings, continue
5. **Empty handling:** Empty files should be skipped (no crash)

**Minimal implementation scaffold:**

```python
def find_related_agent_files(session_id: str, project_dir: str) -> list[Path]:
    history_dir = get_project_history_dir(project_dir)
    matching_files = []

    for agent_file in history_dir.glob("agent-*.jsonl"):
        # Read first line, check sessionId, add to results if match

    return matching_files
```

---

### For `extract_feedback_recursively`

1. **Base case:** Extract feedback from the given session file
2. **Recursive case:** Find related agents, extract from each recursively
3. **Agent ID extraction:** Agent file `agent-a1.jsonl` has agent_id="a1" in its entries
4. **Recursion pattern:** Use agent ID as session ID for next level
5. **Flattening:** Collect all feedback from all levels into single list
6. **Sorting:** Final result sorted by timestamp (chronological order)

**Minimal implementation scaffold:**

```python
def extract_feedback_recursively(session_id: str, project_dir: str) -> list[FeedbackItem]:
    # Check history dir exists
    history_dir = get_project_history_dir(project_dir)
    if not history_dir.exists():
        raise FileNotFoundError(f"History directory not found: {history_dir}")

    feedback = []

    # Extract from main session file (if exists)
    session_file = history_dir / f"{session_id}.jsonl"
    if session_file.exists():
        for line in session_file.read_text().strip().split('\n'):
            if line:
                entry = json.loads(line)
                result = extract_feedback_from_entry(entry)
                if result:
                    feedback.append(result)

    # Find and recursively process child agents
    # (Implement in tests 11-13)

    return sorted(feedback, key=lambda x: x.timestamp)
```

---

## Reusable Functions

Call these existing functions from previous steps:

- `get_project_history_dir(project_dir) -> Path` - Returns history directory path
- `extract_feedback_from_entry(entry: dict) -> FeedbackItem | None` - Parses single entry

---

## Success Criteria

✅ All 13 tests pass in sequence
✅ Each test initially fails before implementation
✅ Implementing test N does NOT make test N+1 pass
✅ `pytest test_main.py::test_find_agents_empty_directory -v` → PASS
✅ `pytest test_main.py -k "step4" -v` → 13 passed

---

## Common TDD Violations to Avoid

❌ **Writing test 1 and implementing full function** - Should only pass test 1
❌ **Implementing filtering before test 4** - Tests 1-3 don't need filtering
❌ **Implementing recursion in test 10** - Recursion not needed until test 11
❌ **Batch-implementing tests 11-13** - Each requires new code

✅ **Correct approach:**

- Test 1 → Return `[]` always
- Test 2 → Read file, check sessionId, return `[]` if no match
- Test 3 → When match found, return `[path]`
- Test 4 → Loop through multiple files, collect matches
- etc.
