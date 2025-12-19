# Roadmap

Future enhancement ideas for claudeutils.

## user-prompt MCP Tool Support

**Goal:** Extract user feedback from `user_prompt` tool results in session files.

**Reference:** https://github.com/nazar256/user-prompt-mcp

**Status:** Pending - MCP not yet installed, sample data unavailable.

**How it works:**
- The `user_prompt` MCP tool allows Claude to request input from the user
- Tool invocations and results appear in the session JSONL files (like any other tool)
- Extract user responses from `tool_result` entries where tool name is `user_prompt`

**Implementation scope:**
- Detect `user_prompt` tool uses in session entries
- Extract user responses from corresponding tool results
- Classify as a new FeedbackType (e.g., `MCP_PROMPT`)

## Session Summary Extraction

**Goal:** Extract a summary of a session for process compliance analysis.

**Output format:**
- Tool uses (without full inputs/outputs)
- User inputs
- Key assistant outputs
- Timeline of interactions

**Use case:** Analyze whether agents followed expected workflows, identify deviations from standard procedures.

## Additional Output Formats

**Goal:** Support different output formats beyond JSON.

**Potential formats:**
- Pretty-printed JSON with indentation
- CSV format for spreadsheet analysis
- Markdown format for human-readable reports

## Filtering Options

**Goal:** Allow users to filter extracted feedback.

**Potential filters:**
- `--type` - Filter by feedback type (message, tool_denial, interruption)
- `--since` / `--until` - Date range filtering
- `--agent` - Filter by agent ID
- `--exclude-trivial` - Hide filtered-out trivial messages in output
