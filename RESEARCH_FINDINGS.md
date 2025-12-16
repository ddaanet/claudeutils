# Research Findings: Claude Code Conversation History Storage

**Research Date:** 2025-12-16
**Project:** claudeutils - Extract user feedback tool
**Agent IDs:** ae9906a, ad67fd8

## Primary Findings

### Storage Locations

**Global user input history:**
- Path: `~/.claude/history.jsonl`
- Content: ONLY user inputs (no assistant messages, no tool results)
- Format: Simple JSONL with `display`, `timestamp`, `project`, `sessionId`
- Size: ~804 KB for ~3,700 entries over 2.5 months

**Full conversation data:**
- Path: `~/.claude/projects/[ENCODED-PATH]/*.jsonl`
- Content: Complete conversation transcripts (user + assistant + tool results)
- Files:
  - Top-level sessions: UUID-named (e.g., `e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl`)
  - Sub-agents: `agent-[id].jsonl` (e.g., `agent-a6755ed.jsonl`)

### Path Encoding

**Algorithm:** Replace `/` with `-` and remove leading dash
- Example: `/Users/david/code/claudeutils` → `-Users-david-code-claudeutils`
- Full path: `~/.claude/projects/-Users-david-code-claudeutils/`

### JSONL Entry Structure

**User message (simple text):**
```json
{
  "type": "user",
  "message": {"role": "user", "content": "Design a python script..."},
  "timestamp": "2025-12-16T08:39:26.932Z",
  "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
  "agentId": "a6755ed",
  "slug": "fluffy-cuddling-forest"
}
```

**Tool denial (error with is_error=true):**
```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [{
      "type": "tool_result",
      "is_error": true,
      "content": "The user doesn't want to proceed with this tool use...",
      "tool_use_id": "toolu_0165cVNnbPXQCt22gTrTXnQq"
    }]
  },
  "timestamp": "2025-12-16T08:43:43.789Z",
  "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1",
  "agentId": "a6755ed"
}
```

**Request interruption:**
```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [{"type": "text", "text": "[Request interrupted by user for tool use]"}]
  },
  "timestamp": "2025-12-16T08:43:43.872Z",
  "sessionId": "e12d203f-ca65-44f0-9976-cb10b74514c1"
}
```

**Assistant message (with tool_use):**
```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "I'll help you..."},
      {"type": "tool_use", "id": "toolu_01Q9...", "name": "Task", "input": {...}}
    ]
  }
}
```

### Agent Relationship Discovery

**Finding agent IDs from parent session:**
- Look for assistant messages with `type: "tool_use"` where `name: "Task"`
- Extract agent ID from subsequent tool_result entries
- Agent files named: `agent-[extracted-id].jsonl`

**Example:**
- Main session spawns agent via Task tool
- Agent writes to `agent-a6755ed.jsonl`
- That agent can spawn sub-agents (e.g., `agent-ae9906a.jsonl`)
- Need recursive traversal to get all feedback

### Key Metadata Fields

| Field | Type | Purpose | Always Present |
|-------|------|---------|----------------|
| `type` | string | Message type (user/assistant) | Yes |
| `timestamp` | ISO 8601 | Message time | Yes |
| `sessionId` | UUID | Groups messages | Yes |
| `agentId` | string | Sub-agent identifier | No (only in agent sessions) |
| `slug` | string | Human-readable session name | No |
| `toolUseResult` | string | Error message for denials | No (only on errors) |

### Sample Data Locations

**Current project conversation:**
- File: `~/.claude/projects/-Users-david-code-claudeutils/e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl`
- Lines: 23+ entries
- Contains: Tool denials, interruptions, substantive user feedback
- Agent files: `agent-a6755ed.jsonl`, `agent-ae9906a.jsonl`, `agent-ad67fd8.jsonl`

**Statistics:**
- 336 total JSONL files across all projects in `~/.claude`
- Mix of main sessions and agent sessions
- File sizes vary: 278 bytes to 203 KB

## Sources

All findings extracted from:
1. **Exploration Agent ae9906a** - Discovered history.jsonl structure
2. **Exploration Agent ad67fd8** - Discovered project-specific JSONL files and full schema
3. **Direct file reads:**
   - `/Users/david/.claude/projects/-Users-david-code-claudeutils/e12d203f-ca65-44f0-9976-cb10b74514c1.jsonl` (lines 0-30)

## Implementation Notes

1. **No recursion in file structure:** Agents are sibling files, not nested directories
2. **Cycle detection needed:** Agents could theoretically reference each other
3. **Trivial filtering:** Must exclude "y", "n", "continue", "resume", "g", "go", "/commands"
4. **Type safety:** Use Pydantic for validation of JSON entries
5. **Session discovery:** Only UUID-pattern files are top-level sessions
