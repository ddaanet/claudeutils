# Feature Plan: Feedback Processing Pipeline

**Status:** Planning

---

## Overview

Add three subcommands for batch feedback processing:

| Command | Purpose |
|---------|---------|
| `collect` | Batch extract from all sessions |
| `analyze` | Filter noise, categorize feedback |
| `rules` | Extract rule-worthy items |

**Dependencies:** Feature 1 (filtering) → Features 2-4 (subcommands use filtering)

---

## Feature 1: Filtering Module

**Goal:** Create `src/claudeutils/filtering.py` with reusable filtering functions.

### Group A: Noise Detection (Tests 1-4)

#### Test 1: `test_is_noise_command_output_detected`

**Given:** Content `<command-name>/clear</command-name>`
**When:** `is_noise(content)` called
**Then:** Returns `True`

**Requires:** Create `is_noise()`, check for `<command-name>` marker
**Does NOT require:** Other noise types, length checks

#### Test 2: `test_is_noise_bash_output_detected`

**Given:** Content `<bash-stdout>test output</bash-stdout>`
**When:** `is_noise(content)` called
**Then:** Returns `True`

**Requires:** Add `<bash-stdout>`, `<bash-input>` markers
**Does NOT require:** Length checks, system messages

#### Test 3: `test_is_noise_system_message_detected`

**Given:** Content `Caveat: The messages below`
**When:** `is_noise(content)` called
**Then:** Returns `True`

**Requires:** Add `Caveat:`, `Warmup`, `<tool_use_error>` markers
**Does NOT require:** Length checks

#### Test 4: `test_is_noise_short_message_detected`

**Given:** Content `hello` (5 chars, no markers)
**When:** `is_noise(content)` called
**Then:** Returns `True`

**Requires:** Add length check (< 10 chars)
**Does NOT require:** Categorization

**⏸ CHECKPOINT A1:** Run `just test -k is_noise` (must pass). Stop for user review.

### Group B: Categorization (Tests 5-8)

#### Test 5: `test_categorize_instruction`

**Given:** FeedbackItem with content `Don't use git add -A`
**When:** `categorize_feedback(item)` called
**Then:** Returns `instructions`

**Requires:** Create `categorize_feedback()`, keywords: don't, never, always, must, should
**Does NOT require:** Other categories

#### Test 6: `test_categorize_correction`

**Given:** FeedbackItem with content `No, that's the wrong approach`
**When:** `categorize_feedback(item)` called
**Then:** Returns `corrections`

**Requires:** Add keywords: no, wrong, incorrect, fix, error
**Does NOT require:** Priority handling between categories

#### Test 7: `test_categorize_process`

**Given:** FeedbackItem with content `Before committing, run the tests`
**When:** `categorize_feedback(item)` called
**Then:** Returns `process`

**Requires:** Add keywords: plan, next step, workflow, before, after
**Does NOT require:** code_review, preferences categories

#### Test 8: `test_categorize_code_review`

**Given:** FeedbackItem with content `Please review this refactored code`
**When:** `categorize_feedback(item)` called
**Then:** Returns `code_review`

**Requires:** Add keywords: review, refactor, improve, clarity
**Does NOT require:** preferences category

**⏸ CHECKPOINT A2:** Run `just test -k categorize` (must pass). Stop for user review.

### Group C: Batch Filtering (Tests 9-10)

#### Test 9: `test_filter_feedback_removes_noise`

**Given:** List with 3 items: 1 noise, 2 substantive
**When:** `filter_feedback(items)` called
**Then:** Returns list with 2 items

**Requires:** Apply `is_noise()` to filter list
**Does NOT require:** Categorization

#### Test 10: `test_filter_feedback_preserves_order`

**Given:** List with items in specific order
**When:** `filter_feedback(items)` called
**Then:** Filtered list preserves original order

**Requires:** Verify order preservation
**Does NOT require:** Sorting

**⏸ CHECKPOINT A3:** Run `just test tests/test_filtering.py` (must pass). Stop for user review before Feature 2.

---

## Feature 2: `collect` Subcommand

**Goal:** `claudeutils collect [--project PATH] [--output FILE]`

### Group A: Basic Collection (Tests 1-3)

#### Test 1: `test_collect_single_session_with_feedback`

**Given:** One session file with substantive feedback
**When:** `collect` called
**Then:** Returns JSON array with one FeedbackItem

**Requires:** Wire up argparse, call `list_top_level_sessions()`, call `extract_feedback_recursively()`, aggregate to list
**Does NOT require:** Multiple sessions, error handling

#### Test 2: `test_collect_multiple_sessions`

**Given:** Three session files with different feedback
**When:** `collect` called
**Then:** Returns aggregated array with 3 items

**Requires:** Iterate multiple sessions, combine all FeedbackItems
**Does NOT require:** Error handling, subagent recursion

#### Test 3: `test_collect_with_subagents`

**Given:** Session with nested sub-agents containing feedback
**When:** `collect` called
**Then:** Returns feedback from main AND sub-agents (4 items)

**Requires:** Verify aggregation includes nested feedback
**Does NOT require:** Error handling

**⏸ CHECKPOINT B1:** Run `just test -k test_collect` (must pass). Stop for user review.

### Group B: Error Handling (Tests 4-5)

#### Test 4: `test_collect_skips_malformed_session`

**Given:** Two sessions: one valid, one malformed
**When:** `collect` called
**Then:** Returns feedback from valid session, logs warning to stderr

**Requires:** Wrap in try/except, log errors, continue processing
**Does NOT require:** File output

#### Test 5: `test_collect_output_to_file`

**Given:** Sessions with feedback, `--output` flag
**When:** `collect --output out.json` called
**Then:** Writes JSON to file

**Requires:** Add `--output` argument, write to file when specified
**Does NOT require:** New logic beyond existing patterns

**⏸ CHECKPOINT B2:** Run `just test -k test_collect` (must pass). Stop for user review before Feature 3.

---

## Feature 3: `analyze` Subcommand

**Goal:** `claudeutils analyze [--input FILE | -] [--format text|json]`

### Tests 1-4

#### Test 1: `test_analyze_counts_and_categorizes`

**Given:** JSON with 5 items: 2 instructions, 2 corrections, 1 process
**When:** `analyze --input feedback.json` called
**Then:** Reports total: 5, filtered: 5, correct category counts

**Requires:** Wire up argparse, load JSON, apply `filter_feedback()` + `categorize_feedback()`, aggregate counts, output text
**Does NOT require:** Noise filtering demo, stdin, JSON output

#### Test 2: `test_analyze_filters_noise`

**Given:** JSON with 8 items: 5 substantive, 3 noise
**When:** `analyze --input feedback.json` called
**Then:** Reports total: 8, filtered: 5

**Requires:** Apply `is_noise()` before categorization, report both counts
**Does NOT require:** stdin, JSON output

#### Test 3: `test_analyze_from_stdin`

**Given:** JSON piped to stdin with 3 items
**When:** `echo '[...]' | analyze -` called
**Then:** Reads from stdin, reports total: 3

**Requires:** Handle `-` as stdin indicator, read from `sys.stdin`
**Does NOT require:** JSON output format

#### Test 4: `test_analyze_json_format`

**Given:** JSON with 4 categorized items
**When:** `analyze --input file.json --format json` called
**Then:** Outputs `{"total": 4, "filtered": 4, "categories": {...}}`

**Requires:** Add `--format` argument, output JSON when specified
**Does NOT require:** Text formatting changes

**⏸ CHECKPOINT C:** Run `just test -k test_analyze` (must pass). Stop for user review before Feature 4.

---

## Feature 4: `rules` Subcommand

**Goal:** `claudeutils rules [--input FILE | -] [--min-length N] [--format text|json]`

### Group A: Core Extraction (Tests 1-3)

#### Test 1: `test_rules_extracts_sorted_items`

**Given:** JSON with 3 items, timestamps out of order
**When:** `rules --input feedback.json` called
**Then:** Returns 3 items sorted chronologically

**Requires:** Wire up argparse, load JSON, apply `filter_feedback()`, sort by timestamp, output numbered text
**Does NOT require:** Stricter filtering, deduplication

#### Test 2: `test_rules_deduplicates_by_prefix`

**Given:** 4 items where 2 share first 100 chars
**When:** `rules --input feedback.json` called
**Then:** Returns 3 items (duplicate removed)

**Requires:** Track seen prefixes (first 100 chars, lowercased), skip duplicates
**Does NOT require:** Stricter length filters

#### Test 3: `test_rules_applies_stricter_filters`

**Given:** 5 items: 2 valid, 1 question (`How do I...`), 1 long (1500 chars), 1 short (15 chars)
**When:** `rules --input feedback.json` called
**Then:** Returns 2 items

**Requires:** Question prefix check (`How `, `claude code:`), max length (> 1000), min length (< 20)
**Does NOT require:** JSON output

**⏸ CHECKPOINT D1:** Run `just test -k test_rules` (must pass). Stop for user review.

### Group B: Configuration (Tests 4-5)

#### Test 4: `test_rules_custom_min_length`

**Given:** 3 items with lengths 18, 22, 30 chars
**When:** `rules --input feedback.json --min-length 25` called
**Then:** Returns 1 item (only 30-char passes)

**Requires:** Add `--min-length` argument (default 20)
**Does NOT require:** JSON output

#### Test 5: `test_rules_json_format`

**Given:** 2 rule-worthy items
**When:** `rules --input feedback.json --format json` called
**Then:** Returns `[{"index": 1, "timestamp": "...", "session_id": "...", "content": "..."}]`

**Requires:** Add `--format` argument, output JSON array with index field
**Does NOT require:** Additional filtering

**⏸ CHECKPOINT D2:** Run `just test -k test_rules` (must pass). **All features complete.** Final user review.

---

## Data Models

Add to `src/claudeutils/models.py`:

```python
class AnalysisSummary(BaseModel):
    total: int
    filtered: int
    categories: dict[str, int]

class RuleItem(BaseModel):
    index: int
    timestamp: str
    session_id: str
    content: str
```

---

## Checkpoint Summary

| Checkpoint | Tests | Gate |
|------------|-------|------|
| A1 | 1-4 | Noise detection |
| A2 | 5-8 | Categorization |
| A3 | 9-10 | Filtering module complete |
| B1 | 1-3 | Basic collection |
| B2 | 4-5 | Collect complete |
| C | 1-4 | Analyze complete |
| D1 | 1-3 | Core extraction |
| D2 | 4-5 | **All complete** |
