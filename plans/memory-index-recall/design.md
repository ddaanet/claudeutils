# Memory Index Recall — Design

## Problem

The memory index (`agents/memory-index.md`) is a keyword-rich knowledge catalog loaded into every agent session via CLAUDE.md `@`-reference. It's designed to help agents discover relevant documentation on-demand: scan entries mentally, identify relevance, Read the referenced file.

No empirical evidence exists that this mechanism works. We don't know:
- Whether agents actually consult index entries when working on related topics
- Whether the keyword-rich format aids discovery vs. agents searching ad-hoc
- Which entries are effective and which are dead weight

## Requirements

**Functional:**
- FR-1: Extract tool calls (name, arguments, timestamp) from assistant JSONL entries
- FR-2: Parse memory-index.md into structured data (section → entries → keywords, file reference)
- FR-3: Classify session topics from user prompts via keyword extraction
- FR-4: Score relevance between session topics and index entries
- FR-5: Calculate recall: did agent Read the referenced file when entry was relevant?
- FR-6: Classify discovery pattern: direct read vs search-then-read vs not-found
- FR-7: Generate structured report with per-entry and aggregate metrics
- FR-8: CLI command to run the full analysis pipeline

**Non-functional:**
- NFR-1: Tool extraction is a general capability (reusable beyond this experiment)
- NFR-2: Analysis runs against local session history (no API calls needed)
- NFR-3: Handles malformed JSONL entries gracefully (skip + warn)

**Out of scope:**
- Controlled A/B experiments
- Real-time hook-based instrumentation
- Modifying the memory-index format
- Causal claims (correlation only)
- Sub-agent tool call tracking (index loaded in main session only)

## Architecture

### Pipeline Overview

```
Session JSONL files
    ↓
[1. Tool Extraction]  →  list[ToolCall] per session
    ↓
[2. Index Parsing]    →  list[IndexEntry] from memory-index.md
    ↓
[3. Topic Extraction] →  set[keyword] per session
    ↓
[4. Relevance Scoring] → session × entry → relevance score
    ↓
[5. Recall Calculation] → per-entry recall with discovery pattern
    ↓
[6. Report Generation] → structured analysis report
```

Stages 1-3 are independent (parallelizable). Stage 4 depends on 2+3. Stage 5 depends on 1+4. Stage 6 depends on 5.

### Module Structure

All new code in `src/claudeutils/recall/`:

| Module | Responsibility |
|--------|---------------|
| `__init__.py` | Minimal init (empty or single re-export, per project convention) |
| `tool_calls.py` | Extract tool calls from assistant JSONL entries |
| `index_parser.py` | Parse memory-index.md into structured entries |
| `topics.py` | Extract topic keywords from session user prompts |
| `relevance.py` | Score relevance between topics and index entries |
| `recall.py` | Calculate recall metrics and discovery patterns |
| `report.py` | Generate analysis report |
| `cli.py` | CLI integration (new `claudeutils recall` subcommand, click command) |

**Rationale for subpackage:** This is a distinct analytical capability, not an extension of the feedback extraction pipeline. Separate package prevents module bloat and keeps the main package focused.

**CLI integration pattern:** Follow the existing `statusline` and `account` patterns — define a click command/group in `recall/cli.py`, import and register it in the main `cli.py` click group.

## Design Decisions

### D-1: Tool Call Extraction from JSONL

**Decision:** New `ToolCall` model and extraction function that processes assistant entries.

**JSONL format for assistant tool calls:**
```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_01abc...",
        "name": "Read",
        "input": {"file_path": "/path/to/file.md"}
      }
    ]
  },
  "timestamp": "2025-12-16T08:39:27.000Z",
  "sessionId": "e12d203f-..."
}
```

**Model:**
```python
class ToolCall(BaseModel):
    tool_name: str          # "Read", "Grep", "Glob", "Bash", "Write", etc.
    tool_id: str            # tool_use id for correlation
    input: dict[str, Any]   # tool-specific arguments
    timestamp: str          # ISO 8601
    session_id: str
```

**Extraction function** processes all entries in a session file, collecting `tool_use` blocks from assistant entries. Returns `list[ToolCall]` sorted by timestamp.

**Placement:** `src/claudeutils/recall/tool_calls.py` — in the recall subpackage since this analysis-oriented extraction differs from the feedback extraction in `parsing.py`. If tool call extraction proves broadly useful (NFR-1), promote to top-level module later.

**Verification note:** The assistant `tool_use` format is based on Anthropic API conventions and test fixture patterns. Implementation should verify against a real session file early (first test cycle).

### D-2: Memory-Index Parser

**Decision:** Parse `memory-index.md` into structured `IndexEntry` objects.

**Index format (current):**
```markdown
## agents/decisions/implementation-notes.md

@ references limitation — CLAUDE.md @ syntax only works in CLAUDE.md not skills agents tasks
SessionStart hook limitation — output discarded for new interactive sessions...
```

**Structure:**
- H2 headings define the target file (section heading = file path)
- Exception: "Behavioral Rules" and "Technical Decisions" sections have mixed/special targets
- Each line under a heading is an entry: `key — description`

**Model:**
```python
class IndexEntry(BaseModel):
    key: str                # Text before em-dash
    description: str        # Text after em-dash
    referenced_file: str    # From parent H2 heading (file path)
    section: str            # Parent H2 heading text
    keywords: set[str]      # Extracted from key + description
```

**Keyword extraction:** Split key and description on spaces/punctuation, lowercase, remove stopwords (a, the, is, for, etc.). The resulting set is the keyword surface for relevance matching.

**Special sections:**
- "Behavioral Rules (fragments — already loaded)" → referenced_file varies per entry. Since these are already loaded via CLAUDE.md, they're excluded from recall analysis (agent doesn't need to Read them — they're ambient).
- "Technical Decisions (mixed — check entry for specific file)" → referenced_file cannot be determined from heading alone. These entries are informational but won't have a clear Read target. Exclude from recall measurement.
- Named file sections (e.g., "agents/decisions/implementation-notes.md") → referenced_file is the heading text. These are the primary analysis targets.

### D-3: Session Topic Classification

**Decision:** Extract topic keywords from user prompts in each session.

**Approach:**
1. Collect all user message text from session JSONL
2. Tokenize: split on whitespace/punctuation, lowercase
3. Remove stopwords and trivial tokens (reuse `is_trivial()` logic)
4. Remove common noise words specific to Claude sessions ("please", "can", "help", "want")
5. Result: `set[str]` of topic keywords per session

**Not using LLM-based classification.** Keyword extraction is simpler, deterministic, and sufficient for this correlation analysis. LLM classification would be more accurate but adds API cost and non-determinism.

### D-4: Relevance Scoring

**Decision:** Keyword overlap between session topics and index entry keywords, with calibrated threshold.

**Algorithm:**
```
score(session, entry) = |session_keywords ∩ entry_keywords| / |entry_keywords|
```

Normalized by entry keyword count (smaller entries need fewer matches to be "relevant"). This is essentially a coverage metric: what fraction of the entry's keywords appear in the session?

**Threshold:** An entry is "relevant" to a session if `score ≥ threshold`. Default threshold = 0.3 (30% keyword overlap). Calibrate via manual pilot on 5 sessions (annotator marks ground-truth relevance, adjust threshold to maximize F1).

**Edge cases:**
- Very short entries (1-2 keywords): Even 1 match gives high score. Accept — short entries should have high-signal keywords.
- Very long entries (10+ keywords): Harder to reach threshold. Acceptable — long descriptions spread probability across many keywords.

### D-5: Recall Calculation

**Decision:** For each relevant (session, entry) pair, check if agent Read the referenced file.

**Recall definition:**
```
recall = count(relevant pairs where file was Read) / count(all relevant pairs)
```

**Discovery pattern classification:**

For each successful Read of a referenced file, classify how the agent found it:

| Pattern | Definition |
|---------|-----------|
| **Direct** | Read call to referenced file with no preceding Grep/Glob that targeted the same file or its parent directory |
| **Search-then-read** | Grep or Glob call targeting the file path or parent directory appears before the Read call in the same session |
| **User-directed** | User message containing the file path appears before the Read call (confounding factor) |

**Temporal constraint:** Only count Reads that occur after the first user prompt containing keywords that match the relevant entry. A Read that happens before relevance is triggered doesn't count as index-guided discovery.

**Baseline comparison:**
- **With-index sessions:** Recent sessions where memory-index.md exists in the repo
- **Without-index sessions:** Historical sessions before memory-index.md was created (use `git log` to find the introduction date)
- For baseline sessions, "relevant" means the same keyword matching would have triggered if the index existed

### D-6: Report Format

**Decision:** Structured markdown report with three sections.

**Report structure:**

```markdown
# Memory Index Recall Report

## Summary
- Sessions analyzed: N (with-index: M, baseline: K)
- Relevant (session, entry) pairs: P
- Overall recall rate: X% (baseline: Y%)
- Lift: Z percentage points
- Discovery pattern: A% direct, B% search-then-read, C% user-directed

## Per-Entry Analysis
| Entry Key | File | Recall | Direct% | Sessions |
|-----------|------|--------|---------|----------|
| Path encoding | paths.py | 80% | 100% | 5 |
| ... | ... | ... | ... | ... |

## Recommendations
- High-recall entries (effective, keep as-is): ...
- Low-recall entries (ineffective, rephrase/remove): ...
- Missing entries (files frequently searched but no index entry): ...
```

**Missing entry detection:** Identify files that agents Grep/Glob for frequently but have no corresponding index entry. These are candidates for new entries.

### D-7: CLI Integration

**Decision:** New `claudeutils recall` subcommand.

```bash
# Run full analysis on local session history
claudeutils recall --index agents/memory-index.md

# Specify session count and baseline cutoff
claudeutils recall --index agents/memory-index.md --sessions 30 --baseline-before 2025-06-01

# Output formats
claudeutils recall --index agents/memory-index.md --format json
claudeutils recall --index agents/memory-index.md --format markdown  # default
```

**Arguments:**
- `--index PATH`: Path to memory-index.md (required)
- `--sessions N`: Number of recent sessions to analyze (default: 30)
- `--baseline-before DATE`: ISO date cutoff for baseline sessions (auto-detect from git log if omitted)
- `--threshold FLOAT`: Relevance threshold (default: 0.3)
- `--format {markdown,json}`: Output format
- `--output PATH`: Write report to file (default: stdout)

## Implementation Notes

### JSONL Format Verification

The assistant `tool_use` format is inferred from Anthropic API conventions and existing test fixtures. **First implementation step must verify the format against a real session file.** Create a quick script to dump the first assistant entry with tool calls from an actual session.

### Existing Infrastructure to Reuse

| Existing | Reuse For |
|----------|-----------|
| `discovery.list_top_level_sessions()` | Enumerate sessions for analysis |
| `paths.get_project_history_dir()` | Find session JSONL files |
| `parsing.extract_content_text()` | Extract text from user messages for topic classification |
| `parsing.is_trivial()` | Filter noise from topic keywords |
| `models.SessionInfo` | Session metadata (timestamp, title) |
| JSONL line-by-line parsing pattern | Tool call extraction follows same pattern |

### Testing Strategy

- **Unit tests:** Mock JSONL data with known tool calls, verify extraction
- **Index parser tests:** Sample index entries, verify keyword extraction
- **Relevance tests:** Known session/entry pairs with expected scores
- **Recall tests:** End-to-end with synthetic sessions containing known Read patterns
- **Integration:** Run against a small set of real sessions (marked `@pytest.mark.e2e`)

### Sample Size Considerations

With 20-30 sessions and ~100 index entries, we expect ~50-200 relevant (session, entry) pairs (depending on threshold calibration). This is sufficient for point estimates of recall rate but not for statistical significance testing. Report confidence intervals where possible.

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/data-processing.md` — module patterns, path handling, data models
- `agents/decisions/testing.md` — testing conventions
- `agents/decisions/cli.md` — CLI patterns and conventions

**Additional research allowed:** Planner may explore `src/claudeutils/` modules directly for implementation patterns.

## Next Steps

1. Route to `/plan-adhoc` (general workflow — this is analysis tooling, not behavioral/TDD)
2. Plan should tier-assess: likely Tier 2 (moderate, clear requirements, well-scoped modules)
