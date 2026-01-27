# Architecture

Module structure, path handling, data models, and general architectural decisions.

## Module Architecture

### Minimal `__init__.py`

**Decision:** Keep `src/claudeutils/__init__.py` empty (1 line)

**Rationale:** Prefer explicit imports from specific modules over package-level re-exports for clarity

**Impact:** Users must import from specific modules:

```python
from claudeutils.models import FeedbackItem
from claudeutils.discovery import list_top_level_sessions
from claudeutils.extraction import extract_feedback_recursively
```

### Private Helpers Stay With Callers

**Decision:** `_extract_feedback_from_file()` in `parsing.py`, `_process_agent_file()` in `discovery.py`

**Rationale:** Keep helpers close to their callers for cohesion; extract only when complexity exceeds limits

**Impact:** Clear module boundaries, easier to understand data flow

### Module Split Pattern

**Decision:** Split large files by functional responsibility (models, paths, parsing, discovery, extraction, cli)

**Rationale:** Maintain 400-line limit while preserving logical grouping

**Impact:** 6 source modules + 6 test modules, all under limit

## Path Handling

### Path Encoding Algorithm

**Decision:** Simple `/` → `-` character replacement with special root handling (`"/"` → `"-"`)

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

**Rationale:** Tool denials and interruptions take priority over trivial filtering to preserve important feedback

**Implementation:** `parsing.py:extract_feedback_from_entry()`

## Session Discovery

### UUID Session Pattern

**Decision:** Validate session files with regex `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$`

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

### Docformatter vs. Ruff D205 Conflict

**Decision:** Accept docformatter wrapping as the source of D205 violations when docstring first line exceeds 80-char limit.

**Issue:** When a docstring summary exceeds 80 characters, docformatter wraps the first line, which triggers ruff D205 (blank line required between summary and description).

**Example:**
```python
# Original (E501 - line too long):
"""Convert consecutive **Label:** lines to list items and indent following lists."""

# Docformatter wraps first line to fit 80 chars:
"""Convert consecutive **Label:** lines to list items and indent following
lists.
"""
```

This triggers ruff D205 because docformatter doesn't add the blank line that ruff expects after a multi-line summary.

**Solution:** Shorten docstring summaries to fit within 80 characters (docformatter's wrap-summaries limit), preventing the wrap and avoiding the D205 violation.

**Rationale:** docformatter handles docstring reformatting (which ruff doesn't do). The wrap-summaries setting exists for readability. The conflict is expected but surprising when the first line should be shortened.

**Don't do:** Ignore D205 globally or disable docformatter.

### Complexity Management

**Decision:** Extract helper functions when cyclomatic complexity exceeds limits

**Examples:**

- `_extract_feedback_from_file()` extracted from main extraction logic
- `_process_agent_file()` extracted to handle agent file processing

**Rationale:** Ruff/pylint complexity checks enforced at build time; refactor rather than suppress

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

**Rationale:** Mirrors the exploratory workflow in tmp-\* scripts; each stage builds on previous output

**Data flow:**

- `collect`: Batch extract from all sessions → JSON array of FeedbackItem
- `analyze`: Filter noise, categorize → Statistics summary
- `rules`: Stricter filter, deduplicate → Rule-worthy items for manual review

### Filtering Module as Foundation

**Decision:** Create `filtering.py` module with reusable `is_noise()` and `categorize_feedback()` functions

**Rationale:** Both `analyze` and `rules` need noise filtering; DRY principle

**Impact:** Filtering module implemented first; other features depend on it

### Noise Detection Patterns

**Decision:** Multi-marker detection with length threshold

**Markers (return True if present):**

- Command outputs: `<command-name>`, `<bash-stdout>`, `<bash-input>`, `<local-command-stdout>`
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

**Rationale:** Simple O(1) keyword matching; categories derived from feedback summary analysis

### Deduplication Strategy

**Decision:** First 100 characters as dedup key, case-insensitive

**Rationale:** Handles repeated feedback across sessions; 100 chars captures intent while allowing variation in endings

**Implementation:** Track seen prefixes in set; skip items with already-seen prefix

### Stricter Filtering for Rules

**Decision:** `rules` applies additional filters beyond `analyze`

**Additional filters:**

- Skip questions: starts with "How ", "claude code:"
- Skip long items: > 1000 characters (too context-specific)
- Higher min length: 20 chars (vs 10 for analyze)

**Rationale:** Rule extraction needs higher signal-to-noise; context-specific feedback isn't generalizable

## Token Counting

### Model as First Positional Argument

**Decision:** Model is first positional argument in CLI, required parameter in functions

**Rationale:** Token counts vary by model; explicit model choice ensures accurate counts

**CLI Usage:** `uv run claudeutils tokens sonnet file.md`

**Implementation:** `count_tokens_for_file(path: Path, model: str)`

**Supported models:** haiku, sonnet, opus (short aliases preferred)

### Model Alias Support

**Decision:** Hybrid approach - support Anthropic's official aliases directly, with runtime probing fallback for unversioned aliases

**Rationale:**

- Anthropic provides official aliases like `claude-sonnet-4-5` that auto-update to latest snapshots
- Power users can use full model IDs (`claude-sonnet-4-5-20250929`) or official aliases (`claude-sonnet-4-5`)
- Casual users can use simple aliases ("sonnet", "haiku", "opus") which resolve via runtime probing
- 24-hour cache avoids repeated API calls

**Implementation:**

1. **Pass-through**: If model starts with "claude-", use unchanged (no resolution needed)
2. **Unversioned alias resolution**: For simple aliases like "sonnet":
   - Check cache first (24-hour TTL in user config directory)
   - If cache miss/expired, query `client.models.list()` API
   - Filter models where ID contains the alias (case-insensitive)
   - Select latest by `created_at` timestamp
   - Cache full model list with timestamp
3. **Fallback**: If alias not found, pass through unchanged (API will error)
4. **Cache location**: Platform-appropriate user cache directory via `platformdirs`

**Cache format:**

```json
{
  "fetched_at": "2025-12-29T10:30:00Z",
  "models": [
    {"id": "claude-sonnet-4-5-20250929", "created_at": "2025-09-29T00:00:00Z"},
    ...
  ]
}
```

### Anthropic API Integration

**Decision:** Use official Anthropic SDK with default environment variable handling

**Rationale:** SDK handles API details, retries, error types; avoid custom HTTP logic

**Implementation:** `tokens.py` module

**API Key:** `ANTHROPIC_API_KEY` environment variable (SDK default)

### Empty File Optimization

**Decision:** Return 0 for empty files without API call

**Rationale:** Avoid unnecessary API calls; empty content always has 0 tokens across all models

**Performance:** Reduces API usage for module development workflows

### No Glob Expansion (Initial Release)

**Decision:** Defer glob pattern expansion to future release

**Rationale:** Simplify initial implementation; users can use shell expansion if needed (e.g., `uv run claudeutils tokens *.md --model sonnet`)

**Future:** May add built-in glob support in later version

## Markdown Cleanup Architecture

**Decision Date:** 2026-01-04

**Context:** Extend markdown preprocessor for Claude output patterns

### Problem

Claude generates markdown-like output that isn't always valid markdown:

1. Consecutive lines with emoji/symbol prefixes that should be lists
2. Code blocks with improper fence nesting
3. Metadata labels followed by lists needing indentation

These patterns break dprint formatting or produce suboptimal output.

### Solution

**Preprocessor approach:**

- Run markdown.py fixes BEFORE dprint formatting
- Fix structural issues while preserving content
- Error out on invalid patterns (prevent silent failures)

**Pipeline:**

```
Claude output → markdown.py (structure) → dprint (style) → final output
```

### Design Decisions

#### Extend vs. New Functions

**Decision:** Extend `fix_warning_lines` for checklist detection, create new functions for code blocks and metadata indentation.

**Rationale:**

- Checklist detection is conceptually similar to existing warning line handling
- Code block nesting is fundamentally different (block-based vs. line-based)
- Metadata list indentation is a new pattern distinct from metadata blocks

**Alternatives considered:**

- Create all new functions → More code duplication
- Single mega-function → Harder to test and maintain

#### Error on Invalid Patterns

**Decision:** Error out when inner fences detected in non-markdown blocks.

**Rationale:**

- Prevents dprint formatting failures downstream
- Makes issues visible immediately (fail fast)
- Invalid patterns indicate malformed Claude output that needs fixing

**Alternatives considered:**

- Silent skip → Hides problems, dprint fails later
- Auto-fix → Risk of corrupting code content

#### Processing Order

**Decision:**

```python
1. fix_dunder_references        # Line-based
2. fix_metadata_blocks          # Line-based
3. fix_warning_lines            # Line-based (extended)
4. fix_nested_lists             # Line-based
5. fix_metadata_list_indentation # Line-based (new)
6. fix_numbered_list_spacing    # Spacing (after structure)
7. fix_markdown_code_blocks     # Block-based (last)
```

**Rationale:**

- Line-based fixes before block-based (avoid interference)
- Spacing fixes after structural changes
- Code block nesting last (operates on complete structure)

**Alternatives considered:**

- Random order → Some fixes would break others
- All new fixes at end → Spacing issues with numbered lists

#### Prefix Detection Strategy

**Decision:** Generic prefix detection (any consistent non-markup prefix), not hard-coded patterns.

**Rationale:**

- Handles current patterns (✅, ❌, [TODO], etc.)
- Adapts to new patterns Claude might generate
- Reduces maintenance (no pattern list to update)

**Alternatives considered:**

- Whitelist specific prefixes → Brittle, needs updates
- No grouping logic → Each pattern needs separate fix

#### Indentation Amount

**Decision:** 2 spaces for nested lists.

**Rationale:**

- Standard markdown convention
- Matches dprint default formatting
- Consistent with existing codebase style

**Alternatives considered:**

- 3 spaces → Not standard
- 4 spaces → Too much nesting, harder to read

### Future Direction

**Evolution to dprint plugin:**

Current preprocessor is a separate step. Ideally, this should be a dprint plugin that runs during formatting. Benefits:

- Single-pass processing
- Better integration with dprint configuration
- Cleaner toolchain

**Migration path:**

1. Keep preprocessor functional (backwards compatibility)
2. Develop dprint plugin with same logic
3. Test plugin thoroughly
4. Deprecate preprocessor, migrate users
5. Remove preprocessor once plugin is stable

## Markdown Formatter Selection

### remark-cli Over Prettier

**Decision Date:** 2026-01-07

**Decision:** Use remark-cli as markdown formatter, not Prettier or markdownlint-cli2.

**Rationale:**

| Criterion | Prettier | markdownlint-cli2 | remark-cli (chosen) |
|-----------|----------|-------------------|---------------------|
| Primary Purpose | Formatter | Linter only | Formatter |
| Idempotent | ❌ No (documented bugs) | ❓ N/A | ✅ Yes |
| CommonMark Compliance | ⚠️ Mostly | ✅ Yes | ✅ 100% |
| Nested Code Blocks | ⚠️ Issues | ❓ Unclear | ✅ Correct |
| YAML Frontmatter | ⚠️ Strips comments | ✅ Yes | ✅ Exact preservation |
| Configuration | 2 options | 60+ lint rules | 17+ format options |

**Prettier issues disqualifying it:**
- Non-idempotent: Multiple documented bugs (empty sub-bullets, mid-word underscores, lists with extra indent)
- YAML frontmatter: Strips comments, breaks on long lists
- Nested code blocks: Inconsistent backtick reduction
- Limited configurability

**markdownlint-cli2 limitations:**
- Not a comprehensive formatter (only fixes rule violations)
- No idempotency guarantee

**remark-cli advantages:**
- Idempotent by design with fixed configuration
- 100% CommonMark compliance via micromark
- Handles nested code blocks correctly per spec
- Preserves YAML frontmatter exactly (doesn't parse or modify)
- Highly configurable (17+ formatting options)
- Active maintenance by unified collective
- 150+ plugin ecosystem

**Test Results:** Both Prettier and remark-cli passed test corpus validation (3 runs, idempotent). However, Prettier has documented edge cases that fail in production use.

**Configuration chosen:**
```json
{
  "settings": {
    "bullet": "*",
    "fence": "`",
    "fences": true,
    "rule": "*",
    "emphasis": "*",
    "strong": "*",
    "incrementListMarker": true,
    "listItemIndent": "one"
  },
  "plugins": [
    "remark-gfm",
    "remark-frontmatter",
    "remark-preset-lint-consistent"
  ]
}
```

**Reference:** Full evaluation in `plans/formatter-comparison.md` (archived after cleanup)

## Claude Code Rule Files

### Rule Files for Context Injection

**Decision Date:** 2026-01-27

**Decision:** Use `.claude/rules/` with `paths` frontmatter for automatic context injection when editing domain-specific files.

**Rationale:**
- Documentation-only enforcement (CLAUDE.md tables) relies on model memory/attention - unreliable
- Hooks cannot detect skill loading state (only see tool inputs, not conversation context)
- Rule files with path prefixes provide automatic, hierarchical context injection

**Implementation:**
- `.claude/rules/skill-development.md` → `.claude/skills/**/*`
- `.claude/rules/hook-development.md` → `.claude/hooks/**/*`
- `.claude/rules/agent-development.md` → `.claude/agents/**/*`
- `.claude/rules/command-development.md` → `.claude/commands/**/*`

**Limitations:**
- Rule files provide passive reminders, not enforcement
- Models can still ignore rule context (requires compliance)
- Trade-off accepted: Better discoverability than CLAUDE.md bloat, but not foolproof

**Impact:**
- Improved discoverability of pre-edit requirements
- Automatic context loading when editing domain files
- Removed 13 lines of Pre-Edit Checks table from CLAUDE.md

## Model Terminology

### Premium/Standard/Efficient Naming

**Decision Date:** 2026-01-27

**Decision:** Use "premium/standard/efficient" terminology for model tiers instead of "T1/T2/T3".

**Rationale:**
- T3 terminology ambiguous: Could mean "tier 3" (lowest) or "T-3" (third from top)
- Premium/standard/efficient clearly communicates capability hierarchy
- Aligns with cost and performance expectations

**Mapping:**
- Premium = Opus (architecture, complex design)
- Standard = Sonnet (general work, planning)
- Efficient = Haiku (execution, simple edits)

**Impact:**
- Clear model selection guidance in delegation
- No ambiguity in documentation and skill instructions
- Easier for users to understand model choices
