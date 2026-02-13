# Deliverable Review: memory-index-recall

## 1. Inventory

| Deliverable | Type | Lines |
|-------------|------|-------|
| `src/claudeutils/recall/__init__.py` | Code | 1 |
| `src/claudeutils/recall/cli.py` | Code | 205 |
| `src/claudeutils/recall/index_parser.py` | Code | 167 |
| `src/claudeutils/recall/recall.py` | Code | 290 |
| `src/claudeutils/recall/relevance.py` | Code | 85 |
| `src/claudeutils/recall/report.py` | Code | 139 |
| `src/claudeutils/recall/tool_calls.py` | Code | 157 |
| `src/claudeutils/recall/topics.py` | Code | 140 |
| `tests/test_recall_calculation.py` | Test | 293 |
| `tests/test_recall_index_parser.py` | Test | 169 |
| `tests/test_recall_integration.py` | Test | 156 |
| `tests/test_recall_relevance.py` | Test | 210 |
| `tests/test_recall_tool_calls.py` | Test | 130 |
| `tests/test_recall_topics.py` | Test | 170 |

**Totals:** 8 Code modules (1184 lines), 6 Test modules (1128 lines).

## 2. Gap Analysis

### Missing deliverables (specified but not implemented)

| Requirement | Design Reference | Status |
|-------------|-----------------|--------|
| Baseline comparison (with-index vs without-index sessions) | D-5, D-6, D-7 (`--baseline-before` arg) | **Not implemented.** CLI accepts `--baseline-before` parameter but names it `_baseline_before` (underscore prefix = unused). No code splits sessions into baseline vs with-index. Report has no baseline recall or lift metrics. |
| User-directed discovery pattern detection | D-5 | **Not implemented.** `DiscoveryPattern.USER_DIRECTED` enum value exists and is tracked in aggregation counters, but `classify_discovery_pattern()` never returns it. No code reads user messages to check for file path mentions. |
| Temporal constraint on recall | D-5 | **Not implemented.** Design specifies: "Only count Reads that occur after the first user prompt containing keywords that match the relevant entry." The `_relevant_entry` parameter is accepted but unused (underscore-prefixed). All Reads are counted regardless of when they occur relative to topic prompts. |
| Missing entry detection | D-6 | **Not implemented.** Design specifies: "Identify files that agents Grep/Glob for frequently but have no corresponding index entry." No code generates this analysis. Report Recommendations section only classifies existing entries by recall rate. |
| Confidence intervals | Implementation Notes (Sample Size) | **Not implemented.** Design notes: "Report confidence intervals where possible." No statistical computation present. |

### Unspecified deliverables (implemented but not in design)

None identified. All modules correspond to design-specified pipeline stages.

### CLI option naming deviation

Design D-7 specifies `--format {markdown,json}`. Implementation uses `--output-format {markdown,json}`. The rename is reasonable (avoids collision with `click.format_help`) but deviates from the design specification without documented justification.

## 3. Per-Deliverable Review

---

### `src/claudeutils/recall/__init__.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Satisfies D-2 design note: "Minimal init (empty or single re-export, per project convention)." Contains only a docstring. |
| Functional correctness | N/A (no logic). |
| Functional completeness | Complete for its role. |
| Vacuity | Not vacuous; docstring enables package import. |
| Excess | None. |
| Robustness | N/A. |
| Modularity | Correct. |
| Testability | N/A. |
| Idempotency | N/A. |
| Error signaling | N/A. |

No findings.

---

### `src/claudeutils/recall/tool_calls.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Matches D-1 ToolCall model exactly: `tool_name`, `tool_id`, `input`, `timestamp`, `session_id`. Extraction from assistant entries with `tool_use` content blocks matches the specified JSONL format. |
| Functional correctness | Correct. Parses JSON lines, filters to `type: assistant`, iterates content blocks for `type: tool_use`, extracts fields, sorts by timestamp. |
| Functional completeness | Complete. Handles empty files, non-assistant entries, malformed JSON, missing fields. |
| Vacuity | Does real work. Each function performs non-trivial parsing and validation. |
| Excess | None. |
| Robustness | Good. Graceful degradation on malformed entries (NFR-3 satisfied). Missing `name` or `id` logged and skipped. OSError caught for file read. |
| Modularity | Clean. `_parse_json_line` and `_extract_tool_call_from_block` are well-factored private helpers. |
| Testability | High. Pure functions with file I/O isolated to `extract_tool_calls_from_session`. |
| Idempotency | Yes. Read-only. |
| Error signaling | Warnings via logger, returns empty list on file errors. Consistent with project patterns (graceful degradation). |

No findings.

---

### `src/claudeutils/recall/index_parser.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Matches D-2 specification. `IndexEntry` model has all specified fields: `key`, `description`, `referenced_file`, `section`, `keywords`. Skips Behavioral Rules and Technical Decisions sections per D-2 special section rules. |
| Functional correctness | Correct. H2 heading detection, em-dash splitting, keyword extraction all work as specified. |
| Functional completeness | Complete for specified behavior. |
| Vacuity | Does real work. |
| Excess | None. |
| Robustness | Good. Handles missing file, empty file, lines without em-dash, empty key/description. |
| Modularity | Clean. `_extract_keywords` is a well-factored helper. |
| Testability | High. Single public function with file path input. |
| Idempotency | Yes. Read-only. |
| Error signaling | Logger warning on file read failure, returns empty list. |

**Finding:** STOPWORDS set (59 entries) is duplicated verbatim in `topics.py`. See cross-cutting checks.

---

### `src/claudeutils/recall/topics.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Matches D-3 specification. Collects user message text, tokenizes, removes stopwords and noise words. Uses `extract_content_text()` and `is_trivial()` from existing infrastructure per design's "Existing Infrastructure to Reuse" section. |
| Functional correctness | Correct. Filters user entries, handles both string and array content formats, tokenizes with the same regex pattern as `index_parser.py`, removes stopwords and session-specific noise words. |
| Functional completeness | Complete. |
| Vacuity | Does real work. |
| Excess | None. |
| Robustness | Good. Graceful degradation on malformed JSON (logged and skipped), nonexistent files (logged, returns empty set). |
| Modularity | Clean. Single public function. |
| Testability | High. |
| Idempotency | Yes. Read-only. |
| Error signaling | Logger warning on file errors. |

No findings beyond STOPWORDS duplication (see cross-cutting).

---

### `src/claudeutils/recall/relevance.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Matches D-4 specification. Score formula is `|session_keywords intersection entry_keywords| / |entry_keywords|`. Default threshold 0.3. |
| Functional correctness | Correct. Set intersection, normalized by entry keyword count. Edge case for empty keywords handled (returns 0.0). |
| Functional completeness | Complete. `score_relevance` for individual scoring, `find_relevant_entries` for batch filtering. |
| Vacuity | Does real work. The algorithm is meaningful: measures what fraction of an entry's keyword surface appears in the session. |
| Excess | None. |
| Robustness | Handles empty keywords, empty session keywords, empty entry list. |
| Modularity | Clean separation of single-entry scoring and batch filtering. |
| Testability | High. Pure functions, no I/O. |
| Idempotency | Yes. Stateless computation. |
| Error signaling | N/A (no error paths for pure computation). |

No findings.

---

### `src/claudeutils/recall/recall.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Partially conforms to D-5. Discovery pattern enum matches design. Recall calculation formula matches: `count(relevant pairs where file was Read) / count(all relevant pairs)`. **Deviations:** (1) USER_DIRECTED never returned by classify_discovery_pattern, (2) temporal constraint not implemented, (3) baseline comparison not implemented. |
| Functional correctness | Partially correct. The recall calculation is mathematically sound for what it computes. `_matches_file_or_parent` has a logic issue: it checks `not tool_path.suffix` to determine if a path is a directory, which is an unreliable heuristic (e.g., a file without extension would be treated as a directory). However, this is unlikely to cause real issues in practice since most index-referenced files have extensions. |
| Functional completeness | **Incomplete.** Three features specified in D-5 are absent: user-directed detection, temporal constraint, baseline comparison. |
| Vacuity | The implemented parts do real work. `classify_discovery_pattern` genuinely inspects tool call sequences. However, two parameters (`_relevant_entry`, `_session_id`) are accepted but never used, indicating the function was scaffolded for features never completed. |
| Excess | `DiscoveryPattern.USER_DIRECTED` enum value and its aggregation counters are excess relative to what the code can produce. They will always be zero. |
| Robustness | Reasonable. Handles missing entries in entry_map, empty inputs, zero-division guards. |
| Modularity | Good separation between `classify_discovery_pattern` (per-pair) and `calculate_recall` (aggregation). `_extract_file_from_input` and `_matches_file_or_parent` are clean helpers. |
| Testability | High. Pure functions. |
| Idempotency | Yes. Stateless. |
| Error signaling | N/A (no I/O). |

---

### `src/claudeutils/recall/report.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Partially matches D-6. Report structure has Summary, Per-Entry Analysis, and Recommendations sections. **Missing:** baseline recall, lift computation, missing entry detection section. |
| Functional correctness | One dead code line: `report.py:34` calls `pattern_summary.get("not_found", 0)` but discards the return value (not assigned to a variable). This is harmless but indicates incomplete cleanup. |
| Functional completeness | **Incomplete.** D-6 specifies: sessions analyzed split (with-index: M, baseline: K), lift in percentage points, missing entry detection. None implemented. |
| Vacuity | Does real work. Report generation is non-trivial (markdown table formatting, recommendation classification, JSON serialization). |
| Excess | None beyond the dead `.get()` call. |
| Robustness | Handles empty per_entry_results (guards against zero division in average calculation). |
| Modularity | Clean. Two public functions, one per format. |
| Testability | High. String output from pure functions. |
| Idempotency | Yes. |
| Error signaling | N/A. |

---

### `src/claudeutils/recall/cli.py`

**Type:** Code

| Axis | Assessment |
|------|------------|
| Conformance | Partially matches D-7. Accepts `--index`, `--sessions`, `--baseline-before`, `--threshold`, `--output`. Deviations: (1) `--format` renamed to `--output-format`, (2) `--baseline-before` accepted but unused (`_baseline_before` parameter). |
| Functional correctness | The pipeline orchestration works: parse index, list sessions, extract data, calculate recall, generate report. Validation helper checks for empty index/sessions/entries before proceeding. |
| Functional completeness | **Incomplete.** `--baseline-before` is dead functionality. The parameter exists in the CLI signature but the underscore-prefixed name `_baseline_before` means it's explicitly ignored. |
| Vacuity | Does real work. Non-trivial orchestration of the pipeline stages. |
| Excess | `_validate_inputs` accepts pre-parsed `index_entries` and `all_sessions` but also takes `index` as string to re-derive `index_path` for the error message. The function signature is awkward: `index_path` is computed but only used for the error message (and the existence check is redundant since Click's `type=click.Path(exists=True)` already validates existence). The returned `index_path` from the tuple is captured as `_` at the call site (line 175). |
| Robustness | Good. Catches OSError and ValueError at top level. Uses Click's path validation. Creates output directories. |
| Modularity | Well-factored into `_validate_inputs`, `_extract_session_data`, `_generate_and_output_report`. |
| Testability | Moderate. CLI function is testable via Click's test runner. No unit tests exist for the CLI itself. |
| Idempotency | Yes. Analysis is read-only. |
| Error signaling | Errors to stderr via `click.echo(err=True)`, `sys.exit(1)`. Follows project pattern. |

---

### `tests/test_recall_tool_calls.py`

**Type:** Test

| Axis | Assessment |
|------|------------|
| Conformance | Tests D-1 extraction behavior: empty files, user-only files, single tool call, multiple tools per entry, sorting, malformed JSON, different tool types. |
| Functional correctness | All 9 tests pass. Assertions verify correct field extraction and ordering. |
| Functional completeness | Good coverage of specified behaviors. |
| Vacuity | Tests are non-vacuous. Each test creates realistic JSONL, extracts, and asserts against specific extracted values (field contents, counts, ordering). |
| Excess | `test_tool_call_model_validation` tests Pydantic model construction (Pydantic already validates this). Minor excess. |
| Specificity | Good. Each test targets a single behavior. Failure messages would indicate the specific broken behavior. |
| Coverage | Missing: test for assistant entry with `content` that is not a list (string content). The implementation handles this (line 133: `if not isinstance(content, list): continue`) but no test exercises it. |
| Independence | Good. Tests verify outputs, not implementation details. Uses real file I/O with `tmp_path`. |

---

### `tests/test_recall_index_parser.py`

**Type:** Test

| Axis | Assessment |
|------|------------|
| Conformance | Tests D-2 parsing behavior. |
| Functional correctness | All 11 tests pass. |
| Functional completeness | Good. Tests simple entry, multiple entries, multiple sections, special section skipping, keyword extraction, nonexistent file, empty file, no-em-dash lines, model validation, realistic format. |
| Vacuity | `test_parse_memory_index_entry_model` is borderline vacuous: constructs an `IndexEntry` and asserts the fields match what was passed in. This tests Pydantic model construction, not parser behavior. |
| Excess | None beyond the model test. |
| Specificity | Good. Each test targets one parsing behavior. |
| Coverage | Adequate. Missing: test for entry with empty key or empty description after em-dash split (the code filters these at line 152 but no test exercises it). |
| Independence | Good. File-based tests with `tmp_path`. |

---

### `tests/test_recall_relevance.py`

**Type:** Test

| Axis | Assessment |
|------|------------|
| Conformance | Tests D-4 relevance scoring behavior. |
| Functional correctness | All 10 tests pass. |
| Functional completeness | Good. Tests exact match, partial match, no match, threshold boundary, matched keywords recording, single relevant, multiple relevant, sorted output, empty keywords, no entries. |
| Vacuity | Non-vacuous. Tests exercise the scoring formula with known inputs and verify numeric results. `test_score_relevance_partial_match` checks `pytest.approx(2.0 / 3.0)` which validates the actual formula. |
| Excess | `test_score_relevance_threshold` accepts `tmp_path` parameter but does not use it. |
| Specificity | Good. Each test isolates one aspect of scoring/filtering. |
| Coverage | Missing: test for entry with empty `keywords` set (the code handles this edge case at relevance.py:38 but no test covers it). |
| Independence | Excellent. Pure function tests with no I/O. |

---

### `tests/test_recall_calculation.py`

**Type:** Test

| Axis | Assessment |
|------|------------|
| Conformance | Tests D-5 recall calculation and discovery patterns. |
| Functional correctness | All 7 tests pass. |
| Functional completeness | Tests direct pattern, search-then-read, not-found, simple recall, multi-session recall, per-entry metrics, empty input. |
| Vacuity | Non-vacuous. Tests construct realistic tool call sequences and verify pattern classification and metric calculation. `test_calculate_recall_per_entry_metrics` verifies cross-session aggregation with two entries across two sessions. |
| Excess | None. |
| Specificity | Good. Pattern tests each isolate one classification path. |
| Coverage | **Missing:** No test for `USER_DIRECTED` discovery pattern (because it's never returned by the implementation). No test for `_matches_file_or_parent` with path containment edge cases (e.g., relative vs absolute paths, paths without extensions). No test for the temporal constraint (because it's not implemented). |
| Independence | Good. Constructs inputs directly, no mocking. |

---

### `tests/test_recall_integration.py`

**Type:** Test

| Axis | Assessment |
|------|------------|
| Conformance | Intended to test the full pipeline per design. |
| Functional correctness | `test_recall_pipeline_end_to_end` **fails when run** with `AssertionError: assert 3 == 4`. Line 60 asserts `len(tool_calls) == 4` with comment "1 grep, 3 reads" but the fixture data contains 1 Grep + 2 Reads = 3 tool calls. The test is excluded from the default run by `@pytest.mark.e2e` marker, so the "50 tests pass" count does not include it. |
| Functional completeness | Only 3 tests (including the broken e2e). The passing tests cover no-match scenario and report formatting. |
| Vacuity | `test_recall_report_formatting` uses `__import__` to construct ToolCall and RelevanceScore objects (lines 117, 127-129), which is an unusual pattern that obscures the test. The test is non-vacuous (verifies report structure and JSON validity) but the import style is noisy. |
| Excess | None. |
| Specificity | Moderate. Pipeline tests necessarily cover multiple modules. |
| Coverage | Weak. The e2e test is broken. No test covers the CLI entry point. No test covers the `--output` file-writing path. |
| Independence | Good. Uses `tmp_path` fixtures. |

---

### `tests/test_recall_topics.py`

**Type:** Test

| Axis | Assessment |
|------|------------|
| Conformance | Tests D-3 topic extraction. |
| Functional correctness | All 11 tests pass. |
| Functional completeness | Good. Tests empty session, no user messages, trivial messages, single message, multiple messages, array content format, lowercase normalization, noise word filtering, nonexistent file, slash commands, punctuation tokenization. |
| Vacuity | Non-vacuous. Tests verify keyword presence/absence from realistic JSONL inputs. |
| Excess | None. |
| Specificity | Good. Each test isolates one tokenization/filtering behavior. |
| Coverage | Good coverage of the specified behaviors. |
| Independence | Good. File-based with `tmp_path`. |

---

## 4. Cross-Cutting Checks

### STOPWORDS duplication

`index_parser.py` (lines 12-59) and `topics.py` (lines 25-72) define identical 37-element STOPWORDS sets. This violates DRY. A shared constant module or extraction to a common location would be appropriate.

### Path handling inconsistency

`_matches_file_or_parent` in `recall.py` uses `Path` objects for comparison, but index entries store `referenced_file` as relative paths (e.g., `agents/decisions/testing.md`) while tool call inputs may contain absolute paths (e.g., `/Users/david/code/claudeutils/agents/decisions/testing.md`). The `Path.__eq__` comparison will fail because `Path("agents/decisions/testing.md") != Path("/Users/.../agents/decisions/testing.md")`. This means recall will systematically be under-counted when comparing real session data (absolute tool paths) against index entries (relative paths). No test exercises this cross-module interaction with mixed path types.

### API contract alignment

Module interfaces are consistent:
- `ToolCall`, `IndexEntry`, `RelevanceScore` models are imported correctly across modules.
- `recall.py` imports from `index_parser`, `relevance`, and `tool_calls` correctly.
- `cli.py` orchestrates all modules in the correct pipeline order.
- `report.py` consumes `RecallAnalysis` which is the output of `calculate_recall`.

### Naming uniformity

Generally consistent. One deviation: `_baseline_before` in `cli.py` uses underscore prefix to indicate "unused parameter" rather than following Click's standard approach of omitting unused options or raising NotImplementedError.

### Unused parameters pattern

Multiple functions accept parameters they don't use:
- `classify_discovery_pattern`: `_relevant_entry`, `_session_id`
- `recall` CLI function: `_baseline_before`

These indicate scaffolded-but-unimplemented features. The underscore convention makes the intent clear but the dead parameters add confusion about the function's actual capabilities.

---

## 5. Findings

### Critical

| # | File:Line | Axis | Description |
|---|-----------|------|-------------|
| C-1 | `recall.py:112-159` | Functional completeness | `classify_discovery_pattern` never returns `USER_DIRECTED`. The enum value exists, aggregation counters track it, but no code path produces it. D-5 specifies user-directed detection: "User message containing the file path appears before the Read call." This is a specified feature that is entirely absent from the implementation. |
| C-2 | `recall.py:112-159` | Conformance | Temporal constraint from D-5 not implemented. Design requires: "Only count Reads that occur after the first user prompt containing keywords that match the relevant entry." All Reads are counted regardless of temporal position. This inflates recall for sessions where the agent read the file before the relevant topic was mentioned. |
| C-3 | `cli.py:156`, `recall.py`, `report.py` | Functional completeness | Baseline comparison (D-5, D-6, D-7) is entirely unimplemented. The `--baseline-before` CLI option is accepted but ignored. No code splits sessions by date, no baseline recall computed, no lift metric. The report lacks the "with-index: M, baseline: K" and "Lift: Z percentage points" fields specified in D-6. This was a core design requirement for measuring the marginal impact of the memory index. |

### Major

| # | File:Line | Axis | Description |
|---|-----------|------|-------------|
| M-1 | `test_recall_integration.py:60` | Functional correctness | `test_recall_pipeline_end_to_end` has incorrect assertion: `assert len(tool_calls) == 4` with comment "1 grep, 3 reads" but fixture data contains 1 Grep + 2 Reads = 3 tool calls. Test fails when run (`-m e2e`). Excluded from default run by `@pytest.mark.e2e` marker, masking the failure. |
| M-2 | `recall.py:77-109` | Functional correctness | `_matches_file_or_parent` compares paths using `Path.__eq__`, which requires identical path representations. Real sessions use absolute paths in tool inputs (`/Users/.../agents/decisions/testing.md`) while index entries use relative paths (`agents/decisions/testing.md`). These will never match, meaning recall will be systematically zero on real data. No normalization (e.g., checking if one path ends with the other) is performed. |
| M-3 | `report.py` | Functional completeness | Missing entry detection not implemented. D-6 specifies: "Identify files that agents Grep/Glob for frequently but have no corresponding index entry. These are candidates for new entries." The Recommendations section only categorizes existing entries by recall rate. |
| M-4 | `recall.py:17-23` | Vacuity/Excess | `DiscoveryPattern.USER_DIRECTED` enum value is dead code. It's defined, tracked in aggregation counters (`recall.py:198-202`, `recall.py:224-228`), reported in percentages (`recall.py:252-256`), and displayed in reports, but will always be zero because no code path produces it. This creates misleading output: users see "user_directed: 0" suggesting no user-directed reads occurred, when in fact the detection was never implemented. |

### Minor

| # | File:Line | Axis | Description |
|---|-----------|------|-------------|
| m-1 | `report.py:34` | Functional correctness | Dead code: `pattern_summary.get("not_found", 0)` return value is discarded. The `not_found` count is computed but never assigned to a variable or used. |
| m-2 | `index_parser.py:12-59`, `topics.py:25-72` | Modularity | STOPWORDS set (37 entries) duplicated verbatim across two modules. Should be extracted to a shared location. |
| m-3 | `cli.py:116-120` | Excess | `click.Path(exists=True)` validates file existence, making the `index_path.exists()` check in `_validate_inputs` redundant. Click raises `BadParameter` before the function runs if the file doesn't exist. |
| m-4 | `cli.py:142-145` | Conformance | CLI option named `--output-format` instead of `--format` as specified in D-7. Minor deviation without documented rationale. |
| m-5 | `test_recall_relevance.py:63` | Excess | `test_score_relevance_threshold` accepts `tmp_path: Path` parameter but never uses it. |
| m-6 | `test_recall_integration.py:117-129` | Functional correctness | Uses `__import__("claudeutils.recall.tool_calls", fromlist=["ToolCall"])` instead of direct imports. The module is already imported at the top of the file. Unnecessarily obscure. |
| m-7 | `recall.py:96-102` | Robustness | `_matches_file_or_parent` uses `not tool_path.suffix` as heuristic for "is a directory." Files without extensions (e.g., `Makefile`, `Dockerfile`) would be incorrectly treated as directories. |
| m-8 | `recall.py:112-116` | Excess | Two unused parameters (`_relevant_entry`, `_session_id`) in `classify_discovery_pattern` signature indicate unimplemented features. |

---

## 6. Summary

| Severity | Count |
|----------|-------|
| Critical | 3 |
| Major | 4 |
| Minor | 8 |

### By axis

| Axis | Critical | Major | Minor |
|------|----------|-------|-------|
| Functional completeness | 2 | 1 | 0 |
| Conformance | 1 | 0 | 1 |
| Functional correctness | 0 | 2 | 2 |
| Vacuity/Excess | 0 | 1 | 4 |
| Modularity | 0 | 0 | 1 |
| Robustness | 0 | 0 | 1 |

### Assessment

The pipeline's implemented stages (tool extraction, index parsing, topic extraction, relevance scoring) are well-built: clean modularity, correct algorithms, good error handling, and non-vacuous tests. The foundational modules (tool_calls, index_parser, topics, relevance) are production-quality.

The critical gap is in the *analysis layer*. Three of the most important design requirements are unimplemented: baseline comparison, user-directed detection, and temporal constraints. These aren't edge features; they're the core of what makes this tool analytically useful. Without baseline comparison, the tool cannot measure the memory index's marginal impact. Without temporal constraints, recall is inflated by pre-topic reads. Without user-directed detection, confounded reads cannot be separated from index-guided reads.

The relative-vs-absolute path mismatch (M-2) means the tool would produce systematically zero recall on real session data, making the entire pipeline non-functional for its intended purpose despite all unit tests passing.

The broken e2e test (M-1), hidden behind a marker, is symptomatic: the integration path was not validated end-to-end with realistic data.
