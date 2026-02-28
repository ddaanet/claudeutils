# Simplification Report

**Outline:** plans/userpromptsubmit-topic/runbook-outline.md
**Date:** 2026-02-28

## Summary

- Items before: 13
- Items after: 10
- Consolidated: 3 items across 3 patterns

## Consolidations Applied

### 1. Resolve entries + error handling (Phase 1)
- **Type:** identical-pattern
- **Items merged:** Cycle 1.4 (resolve matched entries), Cycle 1.5 (handle missing files/sections)
- **Result:** Cycle 1.4: Resolve matched entries with error-path coverage
- **Rationale:** Both test `resolve_entries()` with identical test structure. 1.5 tests the same function with missing-file and missing-section fixtures. Parametrized test covers happy path (valid file/section), missing file, and missing section heading in a single cycle. The outline's own expansion guidance flagged this: "could be parametrized into cycle 1.4's test." Total assertions: ~6 (under 8 limit).

### 2. Score/rank + entry cap (Phase 1)
- **Type:** identical-pattern
- **Items merged:** Cycle 1.3 (score and rank candidates), Cycle 1.6 (cap entries by count)
- **Result:** Cycle 1.3: Score, rank, and cap candidates
- **Rationale:** Both modify `score_and_rank()`. Cycle 1.6 adds one parameter (`max_entries`) and a slice operation — the outline flags this as a "thin cycle." The cap test becomes an additional parametrized case in 1.3's test. Same function, same test pattern, only input data varies (no cap vs with cap). Total assertions: ~5 (under 8 limit). Both share dependency chain (1.3 depends on 1.2; 1.6 depended on 1.3).

### 3. Cache hit + cache invalidation (Phase 2)
- **Type:** identical-pattern
- **Items merged:** Cycle 2.2 (cache hit avoids reparsing), Cycle 2.3 (cache invalidation on mtime change)
- **Result:** Cycle 2.2: Cache hit and invalidation
- **Rationale:** Both test `get_or_build_index()` with identical structure: call twice, monkeypatch `parse_memory_index` call count, assert parse invocation count. Only the condition varies (same inputs vs modified mtime). Both depend on 2.1. Parametrized test with 2 rows: `(same_inputs, expect_1_parse)` and `(touch_source, expect_2_parses)`. Total assertions: ~4 (under 8 limit).

## Patterns Not Consolidated

- **Cycles 3.2 + 3.3 (additive + no-match passthrough):** Same test structure (invoke `main()`, check output) but different GREEN implementation work. 3.2 expects no new code (parallel architecture handles it); 3.3 requires empty-result handling in `match_topics()`. Different implementation scopes prevent consolidation despite similar test patterns.
- **Cycles 1.1 + 1.2 (build index + match candidates):** Both create functions in `topic_matcher.py`, but 1.2's `get_candidates()` takes the inverted index dict type introduced by 1.1's `build_inverted_index()`. While testably independent (1.2 uses a pre-built fixture dict), they build on the same type and the GREEN for 1.1 also includes an API promotion in `index_parser.py`. Keeping separate preserves clean RED-GREEN boundaries.

## Requirements Mapping

Updated mapping (merged items absorb all original FR references):

| Requirement | Phase | Cycles/Steps |
|-------------|-------|-------------|
| FR-1: Parse memory-index into keyword lookup table | Phase 1 | 1.1 |
| FR-2: Match user prompt against keyword table | Phase 1 | 1.2, 1.3 |
| FR-3: Resolve and inject matched entry content | Phase 1 | 1.4 |
| FR-4: Cache keyword table for performance | Phase 2 | 2.1, 2.2 |
| FR-5: Integrate as parallel detector in hook | Phase 3 | 3.1, 3.2, 3.3 |
| FR-6: Token budget control (entry count cap) | Phase 1 | 1.3 |
| FR-7: User-visible match feedback via systemMessage | Phase 1 | 1.5 |
| NFR-1: Hook execution within 5s timeout | Phase 2 | 2.1, 2.2 (cache avoids reparse) |
| NFR-2: No degradation of existing hook behavior | Phase 3 | 3.2, 3.3 |
