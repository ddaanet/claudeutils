# Design Decisions

Key architectural and implementation decisions made during project development.

## Module Architecture

### Minimal `__init__.py`

**Decision:** Keep `src/claudeutils/__init__.py` empty (1 line)

**Rationale:** Prefer explicit imports from specific modules over package-level
re-exports for clarity

**Impact:** Users must import from specific modules:

```python
from claudeutils.models import FeedbackItem
from claudeutils.discovery import list_top_level_sessions
from claudeutils.extraction import extract_feedback_recursively
```

### Private Helpers Stay With Callers

**Decision:** `_extract_feedback_from_file()` in `parsing.py`, `_process_agent_file()`
in `discovery.py`

**Rationale:** Keep helpers close to their callers for cohesion; extract only when
complexity exceeds limits

**Impact:** Clear module boundaries, easier to understand data flow

### Module Split Pattern

**Decision:** Split large files by functional responsibility (models, paths, parsing,
discovery, extraction, cli)

**Rationale:** Maintain 400-line limit while preserving logical grouping

**Impact:** 6 source modules + 6 test modules, all under limit

## Path Handling

### Path Encoding Algorithm

**Decision:** Simple `/` → `-` character replacement with special root handling (`"/"` →
`"-"`)

**Rationale:** Matches Claude Code's actual encoding; simple and reversible

**Implementation:** `paths.py:encode_project_path()`

### History Directory Resolution

**Decision:** Use `~/.claude/projects/[ENCODED-PATH]/` as standard location

**Rationale:** Matches Claude Code storage convention

**Implementation:** `paths.py:get_project_history_dir()`

## Content Parsing

### Title Extraction

**Decision:** Handle both string and array (text blocks) content formats

**Rationale:** Claude Code sessions use both formats depending on content type

**Implementation:** `parsing.py:extract_content_text()`

- String content: return directly
- Array content: find first `type="text"` dict and extract `text` field
- Default: return empty string

### Title Formatting

**Decision:** Replace newlines with spaces, truncate to 80 chars with "..." suffix

**Rationale:** Display constraint (terminal width), readability

**Implementation:** `parsing.py:format_title()`

## Filtering Logic

### Trivial Message Detection

**Decision:** Multi-layer filter - empty, single-char, slash commands, keyword set

**Algorithm:**

1. Strip whitespace
2. Check if empty → trivial
3. Check if single character → trivial
4. Check if starts with `/` → trivial
5. Check if lowercase matches keyword set → trivial
6. Otherwise → substantive

**Rationale:** O(1) set lookup, case-insensitive exact matching only

**Keywords:**
`{"y", "n", "k", "g", "ok", "go", "yes", "no", "continue", "proceed", "sure", "okay", "resume"}`

### Feedback Extraction Layering

**Decision:** Type filter → error check → interruption check → trivial filter

**Rationale:** Tool denials and interruptions take priority over trivial filtering to
preserve important feedback

**Implementation:** `parsing.py:extract_feedback_from_entry()`

## Session Discovery

### UUID Session Pattern

**Decision:** Validate session files with regex
`^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$`

**Rationale:** Filter out agent files (agent-*.jsonl) and other non-session files

**Implementation:** `discovery.py:list_top_level_sessions()`

### Sorted Glob Results

**Decision:** Use `sorted(history_dir.glob("*.jsonl"))` instead of raw glob

**Rationale:** Glob doesn't guarantee file order; tests require predictable results

**Impact:** Consistent ordering across runs

### First-Line Parsing

**Decision:** Parse only first JSONL line for session metadata (title, timestamp)

**Rationale:** Session metadata is in first entry; avoids reading entire file

**Performance:** O(1) per session file

## Agent Processing

### Recursive Pattern: AgentId → SessionId

**Decision:** Agent IDs become session IDs for child agents

**Example:** Main session "main-123" has agent "a1", agent "a1" has agent "a2"

- Recursion: `main-123` → `find_related_agents("main-123")` → agent `a1`
- Next level: `a1` → `find_related_agents("a1")` → agent `a2`
- Result: All feedback from main-123, a1, a2 combined

**Rationale:** Matches Claude Code's actual architecture where agents spawn child agents

**Impact:** True tree recursion without special tracking

### Agent ID Extraction

**Decision:** Extract `agentId` from first line when processing agent files

**Rationale:** Agent ID is consistent throughout file; avoids repeated extraction

**Implementation:** `discovery.py:_process_agent_file()`

## Error Handling

### Graceful Degradation

**Decision:** Skip malformed entries, log warnings, continue processing

**Examples:**

- Empty files → skip
- Malformed JSON → log warning, skip entry
- Missing sessionId field → treat as non-match
- Non-existent history dir → raise FileNotFoundError

**Rationale:** Partial data better than complete failure; user can investigate warnings

### Optional Field Defaults

**Decision:** Use `.get(field, default)` for optional fields (sessionId, agentId, slug)

**Rationale:** Pydantic handles None values; graceful handling of missing data

**Implementation:** Throughout `parsing.py` and `discovery.py`

## CLI Design

### Path.cwd() vs os.getcwd()

**Decision:** Use `Path.cwd()` for default project directory

**Rationale:** Consistency with pathlib usage throughout codebase

**Implementation:** `cli.py:main()`

### Error Output Pattern

**Decision:** Print errors to stderr using `print(..., file=sys.stderr)` before
`sys.exit(1)`

**Rationale:** Standard Unix convention - errors to stderr, data to stdout

**Examples:**

- "No session found with prefix 'xyz'" → stderr, exit 1
- "Multiple sessions match prefix 'abc'" → stderr, exit 1

### Entry Point Configuration

**Decision:** Add `[project.scripts]` in pyproject.toml:
`claudeutils = "claudeutils.cli:main"`

**Rationale:** Simpler invocation (`uv run claudeutils list` vs
`uv run python -m claudeutils.cli list`)

**Impact:** Direct command usage after install

## Test Organization

### Test Module Split Strategy

**Decision:** Split test files to mirror source module structure + separate CLI test
modules by subcommand

**Structure:**

```
tests/
├── test_models.py          # Pydantic validation
├── test_paths.py           # Path encoding
├── test_parsing.py         # Content extraction, filtering
├── test_discovery.py       # Session listing
├── test_agent_files.py     # Agent file discovery
├── test_extraction.py      # Recursive extraction
├── test_cli_list.py        # List command
├── test_cli_extract_basic.py   # Extract command, session matching
└── test_cli_extract_output.py  # JSON output, integration
```

**Rationale:** Maintain 400-line limit while keeping related tests together

### Mock Patching Pattern

**Decision:** Patch where object is **used**, not where it's **defined**

**Example:**

```python
# If module A defines foo(), and module B imports and uses it:
# Patch at usage location:
monkeypatch.setattr("pkg.b.foo", mock)  # ✅ Correct
monkeypatch.setattr("pkg.a.foo", mock)  # ❌ Won't work
```

**Rationale:** Python imports create references in the importing module's namespace

**Applied:** Mock patches target `claudeutils.discovery.*` and
`claudeutils.extraction.*` for functions used in those modules

## Data Models

### Pydantic for Validation

**Decision:** Use Pydantic BaseModel for all data structures (SessionInfo, FeedbackItem)

**Benefits:**

- Automatic type validation
- ISO 8601 timestamp validation
- JSON serialization with `model_dump(mode="json")`
- Clear field definitions

**Impact:** Type safety at runtime, not just static analysis

### FeedbackType Enum

**Decision:** Use StrEnum for feedback types (MESSAGE, TOOL_DENIAL, INTERRUPTION)

**Rationale:** Type-safe string constants, clear intent, better than string literals

**Impact:** IDE autocomplete, validation errors for invalid types

## Code Quality

### Complexity Management

**Decision:** Extract helper functions when cyclomatic complexity exceeds limits

**Examples:**

- `_extract_feedback_from_file()` extracted from main extraction logic
- `_process_agent_file()` extracted to handle agent file processing

**Rationale:** Ruff/pylint complexity checks enforced at build time; refactor rather
than suppress

### No Suppression Shortcuts

**Decision:** Fix linting issues properly instead of using `# noqa` suppressions

**Rationale:** Suppressions hide problems; proper fixes improve code quality

**Examples:**

- G004: Use lazy % formatting for logging
- E501: Split long lines properly
- C901/PLR0912: Extract helper functions

### Type Annotations

**Decision:** Full type annotations in strict mypy mode

**Rationale:** Catch bugs early, self-documenting code, IDE support

**Impact:** Zero runtime overhead, significant development-time benefit

## Feedback Processing Pipeline

### Pipeline Architecture

**Decision:** Three-stage pipeline: `collect` → `analyze` → `rules`

**Rationale:** Mirrors the exploratory workflow in tmp-\* scripts; each stage builds on
previous output

**Data flow:**

- `collect`: Batch extract from all sessions → JSON array of FeedbackItem
- `analyze`: Filter noise, categorize → Statistics summary
- `rules`: Stricter filter, deduplicate → Rule-worthy items for manual review

### Filtering Module as Foundation

**Decision:** Create `filtering.py` module with reusable `is_noise()` and
`categorize_feedback()` functions

**Rationale:** Both `analyze` and `rules` need noise filtering; DRY principle

**Impact:** Filtering module implemented first; other features depend on it

### Noise Detection Patterns

**Decision:** Multi-marker detection with length threshold

**Markers (return True if present):**

- Command outputs: `<command-name>`, `<bash-stdout>`, `<bash-input>`,
  `<local-command-stdout>`
- System messages: `Caveat:`, `Warmup`, `<tool_use_error>`
- Error outputs: `Exit code`, `error: Recipe`

**Length threshold:** < 10 characters (configurable for `rules`)

**Rationale:** Based on analysis of 1200 feedback items; these patterns dominated noise

### Categorization by Keywords

**Decision:** Keyword-based category assignment with priority order

**Categories and keywords:**

| Category     | Keywords                                 |
| ------------ | ---------------------------------------- |
| instructions | don't, never, always, must, should       |
| corrections  | no, wrong, incorrect, fix, error         |
| code_review  | review, refactor, improve, clarity       |
| process      | plan, next step, workflow, before, after |
| preferences  | prefer, i want, make sure, ensure        |
| other        | (default)                                |

**Rationale:** Simple O(1) keyword matching; categories derived from feedback summary
analysis

### Deduplication Strategy

**Decision:** First 100 characters as dedup key, case-insensitive

**Rationale:** Handles repeated feedback across sessions; 100 chars captures intent
while allowing variation in endings

**Implementation:** Track seen prefixes in set; skip items with already-seen prefix

### Output Format Options

**Decision:** Support both `--format text` (default) and `--format json`

**Rationale:** Text for human review, JSON for piping to other tools

**Impact:** All batch commands (`analyze`, `rules`) support both formats

### Stricter Filtering for Rules

**Decision:** `rules` applies additional filters beyond `analyze`

**Additional filters:**

- Skip questions: starts with "How ", "claude code:"
- Skip long items: > 1000 characters (too context-specific)
- Higher min length: 20 chars (vs 10 for analyze)

**Rationale:** Rule extraction needs higher signal-to-noise; context-specific feedback
isn't generalizable
