# Claude Code Feedback Extractor

Extract user feedback from Claude Code conversation history for retrospective analysis.

## Installation

```bash
# Clone repository
git clone <repo-url>
cd claudeutils

# Install with uv
uv sync
```

## Usage

### Basic Commands

```bash
# List all conversation sessions
uv run claudeutils list

# Extract feedback from a specific session (by prefix)
uv run claudeutils extract e12d203f

# Extract to file
uv run claudeutils extract e12d203f --output feedback.json

# Use custom project directory
uv run claudeutils list --project /path/to/project
uv run claudeutils extract abc123 --project /path/to/project
```

### Feedback Processing Pipeline

Process feedback in stages: collect → analyze → rules

```bash
# Step 1: Collect feedback from ALL sessions into one file
uv run claudeutils collect --output all_feedback.json

# Step 2: Analyze - filter noise and categorize
uv run claudeutils analyze --input all_feedback.json
# Output: total count, filtered count, category breakdown

# Step 3: Extract rule-worthy items (sorted, deduplicated)
uv run claudeutils rules --input all_feedback.json --format json

# Pipeline with stdin (no intermediate files)
uv run claudeutils collect | uv run claudeutils analyze -
uv run claudeutils collect | uv run claudeutils rules --input -
```

#### Categories (from analyze)

- **instructions** - Directives: "don't", "never", "always", "must", "should"
- **corrections** - Fixes: "no", "wrong", "incorrect", "fix", "error"
- **process** - Workflow: "plan", "next step", "workflow", "before", "after"
- **code_review** - Quality: "review", "refactor", "improve", "clarity"
- **preferences** - Other substantive feedback

#### Filtering (automatic)

Noise removed: command output, bash stdout, system messages, short messages (<10 chars)

Rules command applies stricter filters: removes questions ("How..."), long items (>1000
chars), and deduplicates by content prefix.

## Features

- **Session listing:** Display top-level sessions with titles and timestamps
- **Prefix matching:** Extract sessions by partial UUID prefix (e.g., `e12d203f`)
- **Recursive extraction:** Automatically processes sub-agent sessions
- **Trivial filtering:** Filters out single-character responses and common keywords
- **Structured output:** JSON format with full metadata
- **Type-safe:** Pydantic validation with strict mypy checking

## Data Model

```python
class FeedbackType(StrEnum):
    TOOL_DENIAL = "tool_denial"     # User denied tool execution
    INTERRUPTION = "interruption"   # User interrupted agent
    MESSAGE = "message"             # User message/feedback

class FeedbackItem(BaseModel):
    timestamp: str                  # ISO 8601 format
    session_id: str                 # UUID or agent ID
    feedback_type: FeedbackType
    content: str                    # User's message/feedback
    agent_id: Optional[str]         # If from sub-agent
    slug: Optional[str]             # Agent session slug
    tool_use_id: Optional[str]      # For tool denials
```

## Development

```bash
# Run full dev cycle (format, check, test)
just dev

# Run tests only
just test

# Run linting and type checking
just check
```

### Project Structure

```
src/claudeutils/
├── cli.py          # CLI entry point
├── models.py       # Pydantic models
├── paths.py        # Path encoding utilities
├── parsing.py      # Content extraction
├── discovery.py    # Session/agent discovery
└── extraction.py   # Recursive extraction

tests/
├── test_cli_list.py
├── test_cli_extract_basic.py
├── test_cli_extract_output.py
├── test_discovery.py
├── test_parsing.py
├── test_paths.py
├── test_models.py
├── test_agent_files.py
└── test_extraction.py
```

## Implementation Notes

Built with Test-Driven Development (TDD) across 5 implementation steps:

1. **Path encoding & session discovery** - Project path encoding, session listing
2. **Trivial message filter** - Filter out non-substantive responses
3. **Message parsing** - Extract feedback from conversation history
4. **Recursive sub-agent processing** - Handle nested agent sessions
5. **CLI subcommands** - User-facing interface with argparse

See `agents/DESIGN_DECISIONS.md` for architectural decisions and implementation
patterns.

## Documentation

- `START.md` - Quick start guide for contributors
- `AGENTS.md` - Project overview and coding standards
- `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
- `agents/TEST_DATA.md` - Data types and sample entries
- `agents/ROADMAP.md` - Future enhancement ideas
- `agents/code.md` - TDD implementation guidelines (skill)
- `agents/commit.md` - Git commit standards (skill)

## Requirements

- Python 3.14+
- Dependencies: pydantic>=2.0
- Dev dependencies: pytest, mypy, ruff

## License

[Add license here]
