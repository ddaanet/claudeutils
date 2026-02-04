# Claude Code Feedback Extractor

Extract user feedback from Claude Code conversation history for retrospective analysis.

## Installation

```bash
# Clone repository
git clone <repo-url>
cd claudeutils

# Install with uv
uv tool install .
```

## Usage

### Basic Commands

```bash
# List all conversation sessions
claudeutils list

# Extract feedback from a specific session (by prefix)
claudeutils extract e12d203f

# Extract to file
claudeutils extract e12d203f --output feedback.json

# Use custom project directory
claudeutils list --project /path/to/project
claudeutils extract abc123 --project /path/to/project
```

### Token Counting

Count tokens in files using the Anthropic API. Requires `ANTHROPIC_API_KEY` environment
variable.

```bash
# Count tokens in a single file
claudeutils tokens sonnet prompt.md

# Count tokens across multiple files
claudeutils tokens opus file1.md file2.md

# JSON output format
claudeutils tokens haiku prompt.md --json

# Use full model ID instead of alias
claudeutils tokens claude-sonnet-4-5-20250929 prompt.md
```

**Supported model aliases:**

- `haiku` - Latest Claude Haiku model
- `sonnet` - Latest Claude Sonnet model
- `opus` - Latest Claude Opus model

Aliases automatically resolve to the latest available model version (cached for 24
hours). You can also use full model IDs like `claude-sonnet-4-5` or
`claude-sonnet-4-5-20250929`.

## Markdown Preprocessor

The `markdown` command preprocesses Claude-generated markdown output before dprint
formatting:

```bash
# Process files from git status
git status --short | cut -c4- | claudeutils markdown

# Or pipe file paths directly
echo "output.md" | claudeutils markdown
```

**What it fixes:**

- Consecutive emoji/symbol prefixed lines → proper lists
- Nested code blocks in `` ```markdown `` fences
- Metadata labels with following lists → indented nested lists
- Numbered list spacing issues
- And more...

**Processing Pipeline:**

```
Claude output → markdown.py → dprint → final output
```

The preprocessor handles structural issues that Claude commonly produces but aren't
valid markdown. After preprocessing, dprint applies consistent formatting.

**Note:** This is currently a standalone tool but should eventually evolve into a dprint
plugin for better integration.

### Feedback Processing Pipeline

Process feedback in stages: collect → analyze → rules

```bash
# Step 1: Collect feedback from ALL sessions into one file
claudeutils collect --output all_feedback.json

# Step 2: Analyze - filter noise and categorize
claudeutils analyze --input all_feedback.json
# Output: total count, filtered count, category breakdown

# Step 3: Extract rule-worthy items (sorted, deduplicated)
claudeutils rules --input all_feedback.json --format json

# Pipeline with stdin (no intermediate files)
claudeutils collect | claudeutils analyze -
claudeutils collect | claudeutils rules --input -
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
- **Token counting:** Count tokens in files using Anthropic API with automatic model
  alias resolution
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
├── extraction.py   # Recursive extraction
├── tokens.py       # Token counting with Anthropic API
├── tokens_cli.py   # Token counting CLI handler
└── exceptions.py   # Custom exceptions

tests/
├── test_cli_list.py
├── test_cli_extract_basic.py
├── test_cli_extract_output.py
├── test_cli_tokens.py
├── test_cli_help.py
├── test_discovery.py
├── test_parsing.py
├── test_paths.py
├── test_models.py
├── test_agent_files.py
├── test_extraction.py
├── test_tokens_count.py
├── test_tokens_resolve.py
└── test_tokens_integration.py
```

## Implementation Notes

Built with Test-Driven Development (TDD) across 5 implementation steps:

1. **Path encoding & session discovery** - Project path encoding, session listing
2. **Trivial message filter** - Filter out non-substantive responses
3. **Message parsing** - Extract feedback from conversation history
4. **Recursive sub-agent processing** - Handle nested agent sessions
5. **CLI subcommands** - User-facing interface with argparse

See `agents/decisions/` for architectural decisions and implementation
patterns.

## Architecture

**Goal:** Foundational tools to support Claude-based development processes.

**Current Features:**
- Feedback extraction from Claude Code conversation history
- Markdown formatting for CommonMark compliance
- Agent rules management and system prompt generation
- Token counting utilities

**Extensible:** New tools added as needed to support Claude workflows.

**Key Technologies:**
- Python 3.14+ with full type annotations (mypy strict)
- Pydantic for data validation and serialization
- pytest for testing with TDD workflow
- uv for dependency management
- ruff for linting
- just for task running

**Development Approach:** Test-Driven Development (TDD) with discrete implementation
steps.

## Documentation

- `agents/session.md` - Current work context and handoff information
- `CLAUDE.md` - Project overview and coding standards
- `agents/decisions/` - Architectural and implementation decisions
- `agents/TEST_DATA.md` - Data types and sample entries
- `agents/ROADMAP.md` - Future enhancement ideas
- `agents/code.md` - TDD implementation guidelines (skill)
- `agents/commit.md` - Git commit standards (skill)

## Requirements

- Python 3.14+
- Dependencies: pydantic>=2.0, anthropic, platformdirs
- Dev dependencies: pytest, mypy, ruff
- Optional: `ANTHROPIC_API_KEY` environment variable (required for token counting)

## License

[Add license here]
