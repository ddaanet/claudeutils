# Runbook Outline: UserPromptSubmit Topic Injection

**Design:** `plans/userpromptsubmit-topic/outline.md`
**Requirements:** `plans/userpromptsubmit-topic/requirements.md`
**Discovery:** `plans/userpromptsubmit-topic/reports/runbook-discovery.md`

## Requirements Mapping

| Requirement | Phase | Cycles/Steps |
|-------------|-------|-------------|
| FR-1: Parse memory-index into keyword lookup table | Phase 1 | 1.1 |
| FR-2: Match user prompt against keyword table | Phase 1 | 1.2, 1.3 |
| FR-3: Resolve and inject matched entry content | Phase 1 | 1.4, 1.5 |
| FR-4: Cache keyword table for performance | Phase 2 | 2.1, 2.2, 2.3 |
| FR-5: Integrate as parallel detector in hook | Phase 3 | 3.1, 3.2, 3.3 |
| FR-6: Token budget control (entry count cap) | Phase 1 | 1.6 |
| FR-7: User-visible match feedback via systemMessage | Phase 1 | 1.7 |
| NFR-1: Hook execution within 5s timeout | Phase 2 | 2.1, 2.2 (cache avoids reparse) |
| NFR-2: No degradation of existing hook behavior | Phase 3 | 3.2, 3.3 |

## Key Decisions Reference

- **D-1:** Entry coverage via `score_relevance()` — `|Q∩D|/|D|`, threshold 0.3 → Cycle 1.3
- **D-2:** Inverted index for candidate lookup → Cycle 1.1
- **D-3:** Additive with all features (parallel detectors) → Cycle 3.2
- **D-4:** Cache in project-local `tmp/`, mtime invalidation → Cycles 2.1–2.3
- **D-5:** Section extraction from decision files → Cycle 1.4
- **D-6:** Entry count cap (max 3) → Cycle 1.6
- **D-7:** Dual-channel output (additionalContext + systemMessage) → Cycle 1.7, 3.1

## Phase Structure

### Phase 1: Matching pipeline (type: tdd, model: sonnet)

Builds `src/claudeutils/recall/topic_matcher.py` — the complete matching pipeline from index construction through scoring, resolution, and output formatting. Tests in `tests/test_recall_topic_matcher.py`.

**API promotions folded into GREEN phases:**
- Cycle 1.1: promote `_extract_keywords` → `extract_keywords` in `index_parser.py` (needed for prompt tokenization)
- Cycle 1.4: promote `_extract_section` → `extract_section` in `when/resolver.py` (needed for content extraction from decision files)

**Heading reconstruction (D-5 implementation detail):** `IndexEntry` stores `key` (trigger text) but not the `/when` vs `/how` prefix. Primary approach: try both heading forms (`## When {key}`, `## How to {key}`) — no model change needed, `_extract_section` returns empty string on miss so the fallback is free. If both miss, skip the entry (consistent with FR-3 silent-skip behavior).

- **Cycle 1.1: Build inverted index from parsed entries** [FR-1, D-2]
  - RED: `test_build_inverted_index_maps_keywords_to_entries` — given 3 IndexEntry objects with known keywords, `build_inverted_index()` returns dict mapping each keyword to its containing entries. Assert keyword "recall" maps to 2 entries, keyword "hook" maps to 1.
  - GREEN: Create `topic_matcher.py` with `build_inverted_index(entries: list[IndexEntry]) -> dict[str, list[IndexEntry]]`. Promote `_extract_keywords` → `extract_keywords` in index_parser.py (rename + update internal caller).

- **Cycle 1.2: Match prompt keywords to candidate entries** [FR-2]
  - RED: `test_match_prompt_returns_candidates_with_overlap` — given inverted index and prompt "how does the recall system work", `get_candidates()` returns set of entries whose keywords overlap with prompt keywords. Assert returns 2 entries (the ones containing "recall"), not the unrelated entry.
  - GREEN: `get_candidates(prompt_text: str, inverted_index: dict[str, list[IndexEntry]]) -> set[IndexEntry]`. Tokenize prompt with `extract_keywords()`, union entries from all matching keywords.

- **Cycle 1.3: Score and rank candidates via score_relevance** [FR-2, D-1]
  - RED: `test_score_candidates_ranks_by_relevance_and_filters` — given 3 candidates with different keyword overlaps, `score_and_rank()` returns list sorted by score descending, entries below threshold 0.3 excluded. Assert: high-overlap entry first (score ~0.8), low-overlap entry excluded (score 0.1).
  - GREEN: `score_and_rank(prompt_keywords: set[str], candidates: set[IndexEntry], threshold: float) -> list[tuple[IndexEntry, RelevanceScore]]`. Call `score_relevance()` per candidate with session_id="hook", filter by threshold, sort descending.
  - Depends on: 1.2

- **Cycle 1.4: Resolve matched entries to section content** [FR-3, D-5]
  - RED: `test_resolve_entries_extracts_decision_content` — given a matched entry referencing a decision file (created in tmp_path), `resolve_entries()` returns list of resolved content strings containing the section heading and body text. Assert content contains the heading text and at least one body line.
  - GREEN: `resolve_entries(entries: list[tuple[IndexEntry, RelevanceScore]], project_dir: Path) -> list[ResolvedEntry]`. Promote `_extract_section` → `extract_section` in `when/resolver.py` (update internal callers at lines 117, 225). For each entry: construct heading from entry key (try both `## When {key}` and `## How to {key}` — see heading reconstruction note above), call `extract_section(file_path, heading)`.
  - Depends on: 1.3

- **Cycle 1.5: Handle missing files and sections gracefully** [FR-3]
  - RED: `test_resolve_skips_missing_files_and_sections` — given entries referencing nonexistent file AND entry referencing file with missing section heading, `resolve_entries()` returns empty list for both (no errors raised). Assert len(result) == 0.
  - GREEN: `extract_section()` already returns empty string on missing file/section. Filter out empty results in `resolve_entries()`.
  - Depends on: 1.4

- **Cycle 1.6: Cap entries by count** [FR-6, D-6]
  - RED: `test_entry_cap_limits_to_max_entries` — given 5 scored entries all above threshold, `score_and_rank()` with max_entries=3 returns only top 3 by score. Assert len(result) == 3 and all scores >= score of 4th entry.
  - GREEN: Add `max_entries` parameter to `score_and_rank()`, slice after sort.
  - Depends on: 1.3

- **Cycle 1.7: Format dual-channel output** [FR-7, D-7, C-2]
  - RED: `test_format_output_produces_context_and_system_parts` — given 2 resolved entries with known content, `format_output()` returns `TopicMatchResult` where `context` contains both resolved sections with headings and source file attribution, and `system_message` contains trigger lines with count header matching pattern `"topic (N lines):\ntrigger1 | extras"`.
  - GREEN: Define `TopicMatchResult` dataclass with `context: str` and `system_message: str`. `format_output(resolved: list[ResolvedEntry]) -> TopicMatchResult`. Context: heading + content + source per entry, joined with `\n\n`. System message: `"topic (N lines):\n"` + trigger lines (key + extras from original index entry, `/when` prefix stripped).
  - Depends on: 1.4

**Light checkpoint** after Phase 1: `just dev` + functional review.

### Phase 2: Index caching (type: tdd, model: sonnet)

Adds caching layer to `topic_matcher.py` so repeated prompts don't re-parse memory-index.md. Cache stored in project-local `tmp/` per D-4.

- **Cycle 2.1: Cache build and store** [FR-4, D-4]
  - RED: `test_cache_stores_index_to_project_tmp` — after calling `get_or_build_index()` with a valid memory-index file, a cache file exists at `tmp/topic-index-{hash}.json`. Assert file exists, JSON loads without error, contains "entries" and "inverted_index" keys.
  - GREEN: `get_or_build_index(index_path: Path, project_dir: Path) -> tuple[list[IndexEntry], dict[str, list[IndexEntry]]]`. On cache miss: parse + build index + write JSON to `project_dir / "tmp" / f"topic-index-{hash}.json"`. Hash from index_path + project_dir (same pattern as continuation registry).

- **Cycle 2.2: Cache hit avoids reparsing** [FR-4]
  - RED: `test_cache_hit_skips_parse` — call `get_or_build_index()` twice with same inputs, monkeypatch `parse_memory_index` to track call count. Assert parse called exactly once (second call uses cache).
  - GREEN: Load cache file, validate timestamp > source mtime, return cached data.
  - Depends on: 2.1

- **Cycle 2.3: Cache invalidation on source modification** [FR-4]
  - RED: `test_cache_invalidates_on_mtime_change` — build cache, modify source file (touch), call `get_or_build_index()` again. Assert parse called again (cache invalidated). Monkeypatch `parse_memory_index` call count.
  - GREEN: Compare source file mtime against cache timestamp. If source newer, invalidate and rebuild.
  - Depends on: 2.1

**Light checkpoint** after Phase 2: `just dev` + functional review.

### Phase 3: Hook integration (type: tdd, model: sonnet)

Integrates topic matching into `agent-core/hooks/userpromptsubmit-shortcuts.py` as a parallel detector block. Tests in `tests/test_ups_topic_integration.py`.

**xfail integration test:** At phase start, write xfail test for full hook → topic injection pipeline. Remove xfail at cycle 3.1 GREEN.

- **Cycle 3.1: Topic detector block in hook** [FR-5, D-3]
  - RED: `test_hook_topic_injection_produces_additional_context` — invoke hook `main()` with prompt matching known memory-index entries (fixture index + decision file in tmp_path). Assert JSON output contains `additionalContext` with resolved decision content AND `systemMessage` containing trigger line.
  - GREEN: Add topic injection detector block in `main()` between pattern guards and continuation parsing. Call `match_topics()` (new top-level entry point wrapping get_or_build_index + get_candidates + score_and_rank + resolve_entries + format_output). Append result to `context_parts` and `system_parts`.
  - Depends on: Phase 1 (complete matching pipeline in topic_matcher.py), Phase 2 (cache layer via get_or_build_index)

- **Cycle 3.2: Additive with existing features** [FR-5, NFR-2, D-3]
  - RED: `test_topic_injection_additive_with_commands` — invoke hook with prompt `"s\nhow does recall work"` (command "s" on first line + topic keywords on second line). Assert output contains BOTH command expansion in systemMessage AND topic content in additionalContext. Both features fire.
  - GREEN: No new code expected — the parallel accumulation architecture handles this. If test fails, debug the accumulation logic.
  - Depends on: 3.1

- **Cycle 3.3: No-match passthrough** [FR-5]
  - RED: `test_topic_injection_silent_on_no_match` — invoke hook with prompt "hello world" (no matching keywords). Assert either no JSON output (clean pass-through) or JSON output without any topic-related content in additionalContext/systemMessage. Existing features (if any match) still fire.
  - GREEN: `match_topics()` returns empty result when no candidates above threshold. Hook skips appending to accumulators when result is empty.
  - Depends on: 3.1

**Full checkpoint** after Phase 3 (final phase): `just dev` + review + functional.

## Complexity Assessment

| Phase | Cycles | Complexity | Notes |
|-------|--------|------------|-------|
| Phase 1 | 7 | Medium | New module, reuses existing infrastructure |
| Phase 2 | 3 | Low | Follows established caching pattern |
| Phase 3 | 3 | Medium | Hook integration, test fixture setup for hook invocation |

**Total: 13 cycles across 3 phases.**

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- Cycle 1.5 (missing files/sections) tests `resolve_entries()` error paths — could be parametrized into cycle 1.4's test. Keep separate only if error handling warrants distinct setup/teardown.
- Cycle 1.6 (entry cap) adds one parameter + slice to `score_and_rank()`. Thin cycle — collapse into cycle 1.3 if the runbook author prefers fewer cycles. The branch point (cap enforcement) is real but minimal.

**Cycle expansion:**
- **Phase 1 cycles 1.1-1.3** share `test_recall_topic_matcher.py` and build incrementally. Each GREEN extends `topic_matcher.py`.
- **Cycle 1.4** modifies `when/resolver.py` (API promotion). GREEN must update internal callers at lines 117 and 225 of `resolver.py` (`_extract_section` → `extract_section`).
- **Cycle 1.1** API promotion: `_extract_keywords` has internal callers at lines 113 and 138 of `index_parser.py` — update both.
- **Heading reconstruction in 1.4:** Try both `## When {key}` and `## How to {key}` forms — `_extract_section` returns empty on miss, so the fallback is free. No `IndexEntry` model change needed.
- **Cycle 1.7 systemMessage format:** Terminal constraint ~60 chars for content after "UserPromptSubmit says: " prefix. The `system_message` field in `TopicMatchResult` becomes one entry in `system_parts` — the hook joins system_parts with `" | "`. The topic block must be pre-formatted as one string with internal newlines. Refer to D-7 for format spec.

**Checkpoint guidance:**
- Phase 1 light checkpoint: `just dev` + verify `topic_matcher.py` exports `match_topics()` entry point
- Phase 2 light checkpoint: `just dev` + verify cache file creation in `tmp/`
- Phase 3 full checkpoint: `just dev` + run integration tests + verify dual-channel output

**References to include:**
- **Recall entries for Common Context:** "when too many rules in context" (context budget), "when hook fragment alignment needed" (output quality)
- **Phase-specific recall:** Phase 3 preamble should resolve "when mapping hook output channel audiences" and "when writing hook user-visible messages"
- **Phase 3 test patterns:** Check existing hook integration test patterns in the test suite before writing fixtures — may need subprocess invocation or `main()` import with env/stdin mocking
