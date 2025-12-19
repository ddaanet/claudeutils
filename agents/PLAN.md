# Feature Plan: Feedback Processing Pipeline

**Status:** Planning
**Created:** 2025-12-19
**Source:** Analysis of tmp-* exploratory scripts

---

## Overview

Integrate the feedback analysis pipeline (currently in tmp-* scripts) into claudeutils as proper CLI subcommands. This enables systematic extraction, filtering, and rule identification from conversation history.

### Current State

The existing CLI provides:
- `list` - Show top-level sessions
- `extract SESSION_PREFIX` - Extract feedback from one session recursively

### Proposed Additions

Three new subcommands for batch feedback processing:

| Command | Purpose | Source Script |
|---------|---------|---------------|
| `collect` | Batch extract from all sessions | tmp-collect_feedback.py |
| `analyze` | Filter noise, categorize feedback | tmp-analyze_feedback.py |
| `rules` | Extract rule-worthy items | tmp-extract_rules.py |

---

## Feature 1: Filtering Module

**Goal:** Provide reusable filtering functions for noise removal and categorization.

### New Module: `src/claudeutils/filtering.py`

Functions to extract:
1. `is_noise(content: str) -> bool` - Detect command outputs, warmups, system messages
2. `filter_feedback(items: list[FeedbackItem]) -> list[FeedbackItem]` - Remove noise
3. `categorize_feedback(item: FeedbackItem) -> str` - Assign category by keywords

### Categories

| Category | Keywords |
|----------|----------|
| instructions | don't, never, always, must, should |
| corrections | no, wrong, incorrect, fix, error |
| code_review | review, refactor, improve, clarity |
| process | plan, next step, workflow, before, after |
| preferences | prefer, i want, make sure, ensure |
| other | (default) |

### Noise Patterns

Skip content containing:
- `<command-name>`, `<local-command-stdout>`, `<bash-input>`, `<bash-stdout>`
- `Warmup`, `Caveat:`, `<tool_use_error>`
- `Exit code`, `error: Recipe`
- Content length < 10 characters

### Test Specification

#### Group A: Noise Detection (Tests 1-4)

##### Test 1: `test_is_noise_command_output_detected`
**Given:** Content containing `<command-name>/clear</command-name>`
**When:** `is_noise(content)` is called
**Then:** Returns True

**Implementation scope:**
- Create is_noise() function
- Check for command output marker `<command-name>`
- Return False for content without markers (default)
- Does NOT require: other noise types, length checks

##### Test 2: `test_is_noise_bash_output_detected`
**Given:** Content containing `<bash-stdout>test output</bash-stdout>`
**When:** `is_noise(content)` is called
**Then:** Returns True

**Implementation scope:**
- Add `<bash-stdout>` and `<bash-input>` to marker list
- Does NOT require: length checks, system messages

##### Test 3: `test_is_noise_system_message_detected`
**Given:** Content containing `Caveat: The messages below`
**When:** `is_noise(content)` is called
**Then:** Returns True

**Implementation scope:**
- Add `Caveat:`, `Warmup`, `<tool_use_error>` to marker list
- Does NOT require: length checks

##### Test 4: `test_is_noise_short_message_detected`
**Given:** Content "hello" (5 characters, no markers)
**When:** `is_noise(content)` is called
**Then:** Returns True

**Implementation scope:**
- Add length check (< 10 chars)
- Does NOT require: categorization

**⏸ CHECKPOINT A1:** Noise detection complete. Run `just test -k is_noise` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review.

#### Group B: Categorization (Tests 5-8)

##### Test 5: `test_categorize_instruction`
**Given:** FeedbackItem with content "Don't use git add -A"
**When:** `categorize_feedback(item)` is called
**Then:** Returns "instructions"

**Implementation scope:**
- Create categorize_feedback() function
- Implement keyword matching for instructions (don't, never, always, must, should)
- Return "other" as default for non-matching
- Does NOT require: other specific categories

##### Test 6: `test_categorize_correction`
**Given:** FeedbackItem with content "No, that's the wrong approach"
**When:** `categorize_feedback(item)` is called
**Then:** Returns "corrections"

**Implementation scope:**
- Add corrections keywords (no, wrong, incorrect, fix, error)
- Does NOT require: priority handling between categories

##### Test 7: `test_categorize_process`
**Given:** FeedbackItem with content "Before committing, run the tests"
**When:** `categorize_feedback(item)` is called
**Then:** Returns "process"

**Implementation scope:**
- Add process keywords (plan, next step, workflow, before, after)
- Does NOT require: code_review or preferences categories

##### Test 8: `test_categorize_code_review`
**Given:** FeedbackItem with content "Please review this refactored code"
**When:** `categorize_feedback(item)` is called
**Then:** Returns "code_review"

**Implementation scope:**
- Add code_review keywords (review, refactor, improve, clarity)
- Does NOT require: preferences category

**⏸ CHECKPOINT A2:** Categorization complete. Run `just test -k categorize` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review.

#### Group C: Batch Filtering (Tests 9-10)

##### Test 9: `test_filter_feedback_removes_noise`
**Given:** List with 3 items: 1 noise, 2 substantive
**When:** `filter_feedback(items)` is called
**Then:** Returns list with 2 substantive items

**Implementation scope:**
- Apply is_noise() to filter list
- Does NOT require: categorization

##### Test 10: `test_filter_feedback_preserves_order`
**Given:** List with items in specific order
**When:** `filter_feedback(items)` is called
**Then:** Returns filtered list preserving original order

**Implementation scope:**
- Verify order preservation
- Does NOT require: sorting

**⏸ CHECKPOINT A3:** Filtering module complete. Run `just test tests/test_filtering.py` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review before proceeding to Feature 2.

---

## Feature 2: `collect` Subcommand

**Goal:** Extract feedback from all sessions in a single command.

### Specification

```
claudeutils collect [--project PATH] [--output FILE]
```

- Iterates over all sessions from `list`
- Calls extraction logic for each session
- Aggregates results into a single JSON array
- Handles errors gracefully (skip failed sessions, log to stderr)

### Data Flow

```
list_top_level_sessions() → [SessionInfo]
    ↓ for each session
extract_feedback_recursively(session_id) → [FeedbackItem]
    ↓ aggregate
JSON array of all FeedbackItem
```

### Test Specification

#### Group A: Basic Collection (Tests 1-3)

##### Test 1: `test_collect_single_session_with_feedback`
**Given:** One session file with substantive feedback
**When:** `collect` is called
**Then:** Returns JSON array with one FeedbackItem

**Implementation scope:**
- Wire up collect subcommand to argparse
- Call list_top_level_sessions() to get sessions
- Call extract_feedback_recursively() for each session
- Aggregate results into output list
- Does NOT require: multiple sessions, error handling

**Fixture data:**
```python
# e12d203f-uuid.jsonl
{"type":"user","message":{"role":"user","content":"Don't use git add -A"},"timestamp":"2025-12-16T08:39:26.932Z","sessionId":"e12d203f-uuid"}
```

##### Test 2: `test_collect_multiple_sessions`
**Given:** Three session files, each with different feedback
**When:** `collect` is called
**Then:** Returns aggregated JSON array with 3 FeedbackItems

**Implementation scope:**
- Iterate over multiple sessions
- Combine all FeedbackItems into single list
- Does NOT require: error handling, subagent recursion

**Fixture data:**
```python
# session-1.jsonl
{"type":"user","message":{"role":"user","content":"Always use uv"},"timestamp":"2025-12-16T08:00:00.000Z","sessionId":"session-1"}
# session-2.jsonl
{"type":"user","message":{"role":"user","content":"Never use git add -A"},"timestamp":"2025-12-16T09:00:00.000Z","sessionId":"session-2"}
# session-3.jsonl
{"type":"user","message":{"role":"user","content":"Stop on unexpected results"},"timestamp":"2025-12-16T10:00:00.000Z","sessionId":"session-3"}
```

##### Test 3: `test_collect_with_subagents`
**Given:** Session with nested sub-agents containing feedback
**When:** `collect` is called
**Then:** Returns feedback from main session AND all sub-agents (4 items total)

**Implementation scope:**
- Verify aggregation includes nested feedback from sub-agents
- Recursive extraction already handled by extract_feedback_recursively
- Does NOT require: error handling

**⏸ CHECKPOINT B1:** Basic collection complete. Run `just test -k test_collect` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review.

#### Group B: Error Handling (Tests 4-5)

##### Test 4: `test_collect_skips_malformed_session`
**Given:** Two sessions: one valid with feedback, one malformed
**When:** `collect` is called
**Then:** Returns feedback from valid session only, logs warning to stderr

**Implementation scope:**
- Wrap extraction in try/except
- Log errors to stderr
- Continue processing remaining sessions
- Does NOT require: file output

##### Test 5: `test_collect_output_to_file`
**Given:** Sessions with feedback, --output flag provided
**When:** `collect --output out.json` is called
**Then:** Writes JSON to file instead of stdout

**Implementation scope:**
- Add --output argument handling
- Write to file when specified
- Does NOT require: new logic beyond existing extract pattern

**⏸ CHECKPOINT B2:** Collect subcommand complete. Run `just test -k test_collect` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review before proceeding to Feature 3.

---

## Feature 3: `analyze` Subcommand

**Goal:** Generate statistical summary with category breakdown.

### Specification

```
claudeutils analyze [--input FILE | -] [--format text|json]
```

- Reads feedback JSON from file or stdin
- Filters noise
- Categorizes remaining items
- Outputs summary statistics

### Output Format (text)

```
Total items: 1202
After filtering: 464

By category:
  instructions: 61
  corrections: 181
  code_review: 24
  process: 15
  preferences: 4
  other: 179
```

### Output Format (json)

```json
{
  "total": 1202,
  "filtered": 464,
  "categories": {
    "instructions": 61,
    "corrections": 181,
    ...
  }
}
```

### Test Specification

#### Group A: Core Analysis (Tests 1-4)

##### Test 1: `test_analyze_counts_and_categorizes`
**Given:** JSON file with 5 feedback items: 2 instructions, 2 corrections, 1 process
**When:** `analyze --input feedback.json` is called
**Then:** Reports total: 5, filtered: 5, with correct category counts

**Implementation scope:**
- Wire up analyze subcommand to argparse
- Parse --input argument, load JSON from file
- Apply filter_feedback() and categorize_feedback()
- Aggregate counts by category
- Output text summary to stdout
- Does NOT require: noise filtering, stdin, JSON output

**Fixture data:**
```python
[
  {"content": "Don't use git add -A", ...},     # instructions
  {"content": "Always run tests first", ...},  # instructions
  {"content": "No, that's wrong", ...},        # corrections
  {"content": "Fix this error", ...},          # corrections
  {"content": "Before committing, check", ...} # process
]
```

##### Test 2: `test_analyze_filters_noise`
**Given:** JSON with 8 items: 5 substantive, 3 noise (command output, short, system msg)
**When:** `analyze --input feedback.json` is called
**Then:** Reports total: 8, filtered: 5, with categories for 5 items only

**Implementation scope:**
- Apply is_noise() to filter before categorization
- Report both total (before filter) and filtered (after filter) counts
- Does NOT require: stdin, JSON output

##### Test 3: `test_analyze_from_stdin`
**Given:** JSON piped to stdin with 3 feedback items
**When:** `echo '[...]' | analyze -` is called
**Then:** Reads from stdin, reports total: 3

**Implementation scope:**
- Handle `-` as stdin indicator
- Read JSON from sys.stdin
- Does NOT require: JSON output format

##### Test 4: `test_analyze_json_format`
**Given:** JSON with 4 categorized items
**When:** `analyze --input file.json --format json` is called
**Then:** Outputs JSON object with total, filtered, categories keys

**Implementation scope:**
- Add --format argument (text default, json option)
- Output AnalysisSummary as JSON when --format json
- Does NOT require: text formatting changes

**Expected output:**
```json
{"total": 4, "filtered": 4, "categories": {"instructions": 2, "corrections": 1, "other": 1}}
```

**⏸ CHECKPOINT C:** Analyze subcommand complete. Run `just test -k test_analyze` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review before proceeding to Feature 4.

---

## Feature 4: `rules` Subcommand

**Goal:** Extract deduplicated rule-worthy feedback items.

### Specification

```
claudeutils rules [--input FILE | -] [--min-length N] [--format text|json]
```

- Applies stricter filtering than `analyze`
- Deduplicates by content prefix (first 100 chars)
- Sorts chronologically
- Outputs numbered list for manual review

### Additional Filters (beyond `analyze`)

- Skip questions (starting with "How ", "claude code:")
- Skip long items (> 1000 chars) - too context-specific
- Skip session continuation summaries
- Minimum length: 20 chars (vs 10 for analyze)

### Test Specification

#### Group A: Core Extraction (Tests 1-3)

##### Test 1: `test_rules_extracts_sorted_items`
**Given:** JSON with 3 rule-worthy items with timestamps out of order
**When:** `rules --input feedback.json` is called
**Then:** Returns 3 items sorted chronologically by timestamp

**Implementation scope:**
- Wire up rules subcommand to argparse
- Parse --input argument, load JSON
- Apply basic filtering (reuse filter_feedback from filtering module)
- Sort by timestamp
- Output numbered text format
- Does NOT require: stricter filtering, deduplication

**Fixture data:**
```python
[
  {"content": "Always use uv", "timestamp": "2025-12-16T10:00:00Z", "session_id": "sess-3"},
  {"content": "Never use git add -A", "timestamp": "2025-12-16T08:00:00Z", "session_id": "sess-1"},
  {"content": "Stop on errors", "timestamp": "2025-12-16T09:00:00Z", "session_id": "sess-2"}
]
```

**Expected output order:** sess-1 (08:00), sess-2 (09:00), sess-3 (10:00)

##### Test 2: `test_rules_deduplicates_by_prefix`
**Given:** 4 items where 2 have identical first 100 chars (different endings)
**When:** `rules --input feedback.json` is called
**Then:** Returns 3 items (duplicate removed)

**Implementation scope:**
- Track seen prefixes (first 100 chars, lowercased)
- Skip items with already-seen prefix
- Does NOT require: stricter length filters

**Fixture data:**
```python
[
  {"content": "Always use uv for dependencies", ...},
  {"content": "Never use git add -A", ...},
  {"content": "Always use uv for everything else too", ...},  # same 100-char prefix as first
  {"content": "Stop on unexpected errors", ...}
]
```

##### Test 3: `test_rules_applies_stricter_filters`
**Given:** 5 items: 2 valid, 1 question ("How do I..."), 1 long (1500 chars), 1 short (15 chars)
**When:** `rules --input feedback.json` is called
**Then:** Returns 2 items (question, long, and short excluded)

**Implementation scope:**
- Add question prefix check (starts with "How ", "claude code:")
- Add max length check (> 1000 chars)
- Add min length check (< 20 chars, stricter than analyze's 10)
- Does NOT require: JSON output

**⏸ CHECKPOINT D1:** Core rule extraction complete. Run `just test -k test_rules` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). Stop for user review.

#### Group B: Configuration and Output (Tests 4-5)

##### Test 4: `test_rules_custom_min_length`
**Given:** 3 items with lengths 18, 22, 30 chars
**When:** `rules --input feedback.json --min-length 25` is called
**Then:** Returns 1 item (only 30-char item passes)

**Implementation scope:**
- Add --min-length argument (default 20)
- Apply configurable minimum
- Does NOT require: JSON output

##### Test 5: `test_rules_json_format`
**Given:** 2 rule-worthy items
**When:** `rules --input feedback.json --format json` is called
**Then:** Returns JSON array of RuleItem objects with index, timestamp, session_id, content

**Implementation scope:**
- Add --format argument (text default, json option)
- Output as JSON array when --format json
- Include index field in each item

**Expected output:**
```json
[
  {"index": 1, "timestamp": "2025-12-16", "session_id": "abc123", "content": "Always use uv"},
  {"index": 2, "timestamp": "2025-12-16", "session_id": "def456", "content": "Never use git add -A"}
]
```

**⏸ CHECKPOINT D2:** Rules subcommand complete. Run `just test -k test_rules` (must pass). Run `just check` - if it fails, STOP (do not fix lint errors). **All features complete.** Final review with user.

---

## Validation Checkpoints Summary

| Checkpoint | Feature | Tests | Gate |
|------------|---------|-------|------|
| A1 | Filtering | 1-4 | Noise detection |
| A2 | Filtering | 5-8 | Categorization |
| A3 | Filtering | 9-10 | Module complete |
| B1 | Collect | 1-3 | Basic collection |
| B2 | Collect | 4-5 | Subcommand complete |
| C | Analyze | 1-4 | Subcommand complete |
| D1 | Rules | 1-3 | Core extraction |
| D2 | Rules | 4-5 | **All complete** |

At each checkpoint: (1) tests pass, (2) `just check` passes, (3) user reviews.

---

## Estimated Test Count

| Feature | Tests |
|---------|-------|
| filtering | 10 |
| collect | 5 |
| analyze | 4 |
| rules | 5 |
| **Total** | **24** |

---

## File Size Considerations

Current module sizes (approximate):
- cli.py: ~150 lines
- extraction.py: ~100 lines
- parsing.py: ~150 lines

New modules:
- filtering.py: ~100-150 lines (new)
- cli.py additions: ~100 lines (adds to existing)

If cli.py exceeds 300 lines after additions, consider splitting into:
- cli.py (main entry, list, extract)
- cli_batch.py (collect, analyze, rules)

---

## Data Model Extensions

### AnalysisSummary (new model for analyze output)

```python
class AnalysisSummary(BaseModel):
    total: int
    filtered: int
    categories: dict[str, int]
```

### RuleItem (new model for rules output)

```python
class RuleItem(BaseModel):
    index: int
    timestamp: str
    session_id: str
    content: str
```

---

## CLI Help Text

### collect

```
usage: claudeutils collect [-h] [--project PATH] [--output FILE]

Extract feedback from all sessions

options:
  --project PATH   Project directory (default: current directory)
  --output FILE    Output file (default: stdout)
```

### analyze

```
usage: claudeutils analyze [-h] [--input FILE] [--format {text,json}]

Analyze feedback for patterns and categories

options:
  --input FILE         Input JSON file or - for stdin
  --format {text,json} Output format (default: text)
```

### rules

```
usage: claudeutils rules [-h] [--input FILE] [--min-length N] [--format {text,json}]

Extract rule-worthy feedback items

options:
  --input FILE         Input JSON file or - for stdin
  --min-length N       Minimum content length (default: 20)
  --format {text,json} Output format (default: text)
```
