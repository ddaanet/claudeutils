# TDD Test Plan — Remember Skill Update

Test plan for Phases 1 and 4 (the two TDD phases).

## Phase 1: Validation (learnings.py)

**Baseline:** 7 tests in `tests/test_validation_learnings.py`, all passing.
**Target:** `src/claudeutils/validation/learnings.py` — add When/How prefix check + min 2 content words check.

**Content words:** Words after stripping prefix ("When " or "How to "). Min 2 content words means:
- "When X Y" (3 total) → 2 content → pass
- "When X" (2 total) → 1 content → fail
- "How to X Y" (4 total) → 2 content → pass
- "How to X" (3 total) → 1 content → fail

Combined with max 5 total (C-2): valid range is 3-5 total for "When", 4-5 for "How to".

### Current Behavior

`validate()` checks:
- Word count max 5 (line 64)
- Uniqueness case-insensitive (line 71)
- Preamble skip (first 10 lines)
- H2 format extraction (TITLE_PATTERN)

### Fixture Impact

Adding prefix check breaks 5 of 7 existing tests — fixtures use titles like "Learning One", "First Learning Title". These must migrate to When/How prefixed titles in the GREEN phase.

Affected tests:
- `test_valid_learnings_file_returns_no_errors` — "Learning One", "Learning Two"
- `test_title_exceeding_max_word_count_returns_error` — long non-prefixed title
- `test_duplicate_titles_detected_case_insensitive` — "First Learning Title"
- `test_preamble_first_10_lines_skipped` — "First Valid Title"
- `test_multiple_errors_reported` — mixed non-prefixed titles

### Cycle 1.1: When/How prefix required

**RED:**
- New test: `test_title_without_prefix_returns_error`
- Fixture: learnings file with `## Bad Title` after preamble
- Assert: `validate()` returns error containing both "prefix" (or "When"/"How") and line number
- Expected failure: No prefix check in validate(), returns `[]`

**GREEN:**
- Add prefix check in `validate()`: title must start with `When ` or `How to `
- Update ALL 5 affected test fixtures to use When/How prefixed titles:
  - "Learning One" -> "When learning one"
  - "Learning Two" -> "When learning two"
  - "First Learning Title" -> "When first learning"
  - "First Valid Title" -> "When valid title"
  - Long title -> `## When this title has way too many words for the validator`
  - Multiple errors fixture: update all titles to use prefixes while preserving error conditions
- Verify: All 8 tests pass (7 existing + 1 new)

### Cycle 1.2: Min 2 content words required

**RED:**
- New test: `test_insufficient_content_words_returns_error`
- Fixture: learnings file with `## When testing` (1 content word after prefix)
- Assert: `validate()` returns error mentioning content words and line number
- Expected failure: No content word count check, returns `[]`

**GREEN:**
- Strip prefix ("When " or "How to ") from title, count remaining words
- Check: `if len(content_words) < 2:` error with descriptive message
- Verify: All 9 tests pass

### Cycle 1.3: Edge cases and combined validation

**RED:**
- New test: `test_how_to_prefix_accepted`
  - "## How to encode paths" (4 words) -> passes
- New test: `test_how_without_to_rejected`
  - "## How encode" (no "to" after "How") -> fails with prefix error
- New test: `test_combined_errors_reported`
  - Title "## Bad" → prefix error (content word check N/A without valid prefix)
  - Title "## When testing" → valid prefix, 1 content word → content words error
  - Title "## How to X" → valid prefix, 1 content word → content words error
  - Verify prefix and content-word errors can coexist across titles

**GREEN:**
- Adjust implementation if any edge case isn't handled
- Key decision: Does "## How encode" fail prefix (not "How to") or something else?
  - Answer: prefix check requires "When " or "How to " — "How " alone fails prefix.
- Verify: All 12 tests pass (7 original + 5 new)

### Precommit Integration (not a TDD cycle)

No new cycle needed — `cli.py` already imports and calls `validate_learnings()` at line 108. New checks propagate automatically. Verify via regression: `just precommit` should still pass.

---

## Phase 4: Recall CLI Fix

**Baseline:** 5 tests in `tests/test_when_cli.py`, all passing.
**Targets:**
- `src/claudeutils/when/cli.py` — rewrite Click command signature
- `agent-core/bin/when-resolve.py` — may need arg changes
- `src/claudeutils/when/resolver.py` — no signature changes (CLI does parsing)

### Current Behavior

Click command: `@click.argument("operator", type=click.Choice(["when", "how"]))` + `@click.argument("query", nargs=-1, required=True)`

Invocation: `when-resolve.py when "writing mock tests"` (two positional args)

All 5 tests use two-arg pattern: `["when", "when", "writing", "mock", "tests"]`

### Target Behavior (FR-12)

Invocation: `when-resolve.py "when writing mock tests"` (one arg with operator prefix)
Batch: `when-resolve.py "when X" "how Y" "when Z"` (multiple queries)

### Resolver Interface

`resolve(operator, query, index_path, decisions_dir)` stays unchanged. CLI parses operator from query prefix, then calls resolve() with separated args. For batch, CLI iterates.

### Cycle 4.1: One-arg syntax replaces two-arg

**RED:**
- New test: `test_single_arg_query_parsed`
- Invoke: `["when", "when writing mock tests"]` (single quoted arg with operator prefix)
- Assert: resolve() called with operator="when", query="writing mock tests"
- Expected failure: CLI expects separate operator arg, "when writing mock tests" is invalid Choice value

**GREEN:**
- Rewrite Click command:
  - Remove `operator` argument
  - Change `query` to variadic args, each containing operator prefix
  - Parse prefix from each query string
  - Call resolve() with parsed operator and remaining query
- Update ALL 5 existing tests to new invocation syntax
- Verify: All 6 tests pass

### Cycle 4.2: Batched recall

**RED:**
- New test: `test_batched_recall_multiple_queries`
- Invoke: `["when", "when writing mock tests", "how encode paths"]`
- Assert: resolve() called twice (once per query), output contains results for both
- Expected failure: After 4.1, CLI handles single query but not iteration over multiple

**GREEN:**
- Implement batch loop: iterate over queries, collect and concatenate results
- Separator between results (e.g., `\n---\n`)
- Verify: All 7 tests pass

### Cycle 4.3: Invalid prefix rejection

**RED:**
- New test: `test_invalid_prefix_rejected`
- Invoke: `["when", "no prefix query"]`
- Assert: exit code != 0, error message mentions "when" or "how" prefix required
- Expected failure: No prefix validation on query strings (old CLI had Click.Choice)

**GREEN:**
- Add prefix validation: query must start with "when " or "how "
- Error message: descriptive, no suggested recovery (per CLI error conventions)
- Verify: All 8 tests pass

### Dot-prefix Preservation (not a separate cycle)

After Cycle 4.1, test with `["when", "when .Section"]` should work because:
- Parse: operator="when", query=".Section"
- resolve() handles dot-prefix routing internally (lines 25-28 of resolver.py)
- Covered in existing test update during 4.1 GREEN (test_query_variadic_argument already tests dot prefix)

---

## Summary

| Phase | Cycles | New Tests | Fixture Updates | Existing Tests |
|-------|--------|-----------|-----------------|----------------|
| 1     | 3      | ~5        | 5 of 7 updated  | 7 preserved    |
| 4     | 3      | 3         | 5 of 5 rewritten| 5 preserved    |
| **Total** | **6** | **~8** | **10** | **12 preserved** |

## Risk Areas

- **Phase 1 fixture migration:** 5 tests need title updates in Cycle 1.1 GREEN. Must preserve the error conditions they test (word count, duplicates) while adding valid prefixes.
- **Phase 4 test rewrite:** All 5 existing tests change invocation syntax. Each must verify same behavioral contract with new API.
- **Resolver stability:** Phase 4 changes CLI only. resolver.py signature unchanged. If resolver changes needed, scope expands.
