# Outline Review: UserPromptSubmit Topic Injection (PDR)

**Artifact**: plans/userpromptsubmit-topic/outline.md
**Date**: 2026-02-28
**Mode**: review + fix-all (PDR criteria)
**Prior review**: plans/userpromptsubmit-topic/reports/outline-review.md

## Summary

Second review after discussion deltas and prerequisite completion. The outline accurately reflects the flattened hook architecture (verified against current `main()` — no early returns, parallel accumulators). One major issue: D-5 specified `resolve()` for content extraction but that function uses fuzzy CLI matching against `WhenEntry` objects, not the `IndexEntry` model the hook produces. Four minor issues addressed: systemMessage join semantics, private API dependencies, missing integration test file, stale entry count.

**Overall Assessment**: Ready

## Recall Context Applied

Resolved entries from `plans/userpromptsubmit-topic/recall-artifact.md`:
- **too many rules in context** -- adherence degrades >200 rules, ~150 budget. Validates FR-6/D-6 entry cap rationale and Context budget pressure risk.
- **evaluating recall system effectiveness** -- 4.1% voluntary activation, forced injection bypasses recognition. Core motivation for this feature: mechanical injection sidesteps the metacognitive recognition barrier.
- **filter user prompt submit hooks** -- no matcher support, script-internal filtering. Confirms C-1 (single hook script, internal filtering).
- **mapping hook output channel audiences** -- additionalContext agent-only, systemMessage user-only. Validates D-7 channel assignment.

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-2 (inverted index) | Complete | Keyword table from memory-index via `parse_memory_index()` + inverted index |
| FR-2 | D-1 (scoring formula) | Complete | Entry coverage via `score_relevance()`, threshold 0.3 |
| FR-3 | D-5 (resolution), D-7 (dual-channel) | Complete | Section extraction from decision files, inject via additionalContext |
| FR-4 | D-4 (cache strategy), D-2 | Complete | project-local `tmp/` cache with mtime invalidation |
| FR-5 | D-3 (additive with all features) | Complete | Parallel detector in flattened architecture |
| FR-6 | D-6 (token budget) | Complete | Entry count cap, highest-scored wins |
| FR-7 | D-7 (dual-channel) | Complete | systemMessage with trigger lines + line count header |
| NFR-1 | D-4 (cache strategy) | Complete | 5s timeout referenced, cache avoids re-parsing |
| NFR-2 | D-3 (additive) | Complete | Parallel accumulation preserves existing behavior |
| C-1 | D-3, Architecture | Complete | Single hook script, new detector block |
| C-2 | D-7 | Complete | additionalContext + systemMessage channels |
| C-3 | D-6, D-10 | Complete | Threshold declared-ungrounded, calibration deferred |

**Traceability Assessment**: All requirements covered with explicit FR/NFR/C tags on decision headings.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **D-5 resolver interface mismatch**
   - Location: D-5 (Resolution)
   - Problem: Original D-5 said "call `resolve()` per entry to get decision section content." Verified `resolve()` in `when/resolver.py`: it takes a query string, parses the index via `when/index_parser.py`'s `WhenEntry` model, and does fuzzy matching. The hook uses `recall/index_parser.py`'s `IndexEntry` model which has `referenced_file` (file path from H2 heading) and `key` (trigger text). These are two different parser/entry models. Calling `resolve()` would re-parse the memory index through the wrong parser, use fuzzy matching instead of exact lookup, and operate on a model that lacks the `referenced_file` field the hook already has.
   - Fix: Rewrote D-5 to specify direct section extraction using `IndexEntry.referenced_file` + `IndexEntry.key` fields with `_extract_section_content()` from `when/resolver.py`. Added explicit note that `resolve()` is not called. Updated Affected Files to reference `_extract_section_content()` instead of `resolve()`.
   - **Status**: FIXED

### Minor Issues

1. **systemMessage join semantics undocumented**
   - Location: D-7 (Dual-channel output)
   - Problem: D-7 specified newline-separated trigger lines in systemMessage, but the existing hook joins `system_parts` with `" | "` (line 949 of hook). If the topic block is appended as multiple entries to `system_parts`, newlines would be lost. The topic block must be a single pre-formatted string.
   - Fix: Added clarification to D-7 that the topic block is a single entry in `system_parts` with internal newlines.
   - **Status**: FIXED

2. **Private API dependencies not flagged**
   - Location: Affected Files, Read-only dependencies
   - Problem: `_extract_keywords()` from `recall/index_parser.py` and `_extract_section_content()` from `when/resolver.py` are both private (underscore-prefixed). Using private functions across module boundaries is fragile — they can change without notice.
   - Fix: Added notes on each dependency flagging private API status and recommending promotion to public API or logic inlining during implementation.
   - **Status**: FIXED

3. **Integration test file missing from Affected Files**
   - Location: Affected Files, New section
   - Problem: Scope IN lists "Integration tests for hook output" but Affected Files only listed `tests/test_recall_topic_matcher.py` (unit tests). No integration test file was specified.
   - Fix: Added `tests/test_ups_topic_integration.py` to New files.
   - **Status**: FIXED

4. **Hardcoded entry count**
   - Location: D-4 and Risks
   - Problem: "347 entries" is a snapshot that becomes stale as memory-index.md grows. Not wrong but misleading for future readers.
   - Fix: Changed to "all entries" / "all memory-index entries" — the count is a profiling concern, not a design parameter.
   - **Status**: FIXED

## Fixes Applied

- D-5 heading -- changed from "batch resolve via resolver" to "section extraction from decision files"
- D-5 body -- rewrote to specify `IndexEntry.referenced_file` + `IndexEntry.key` path with `_extract_section_content()`; added note that `resolve()` is not called
- D-7 body -- added clarification that topic systemMessage block is single `system_parts` entry with internal newlines
- Affected Files, New -- added `tests/test_ups_topic_integration.py`
- Affected Files, Read-only -- changed `resolve()` to `_extract_section_content()` with private API note; added private API note on `_extract_keywords()`
- D-4 cold build -- removed hardcoded "347" count
- Risks, Performance -- removed hardcoded "347" count

## Positive Observations

- Scoring algorithm grounded via dedicated research report (3 reports: internal-codebase, external-research, algorithm-grounding) rather than assumed
- D-10 calibration approach honest about ungrounded parameters with concrete empirical calibration path
- Prerequisite completion verified against actual hook code -- flattened architecture confirmed
- Scope OUT section includes rationale for each exclusion
- D-8 and D-9 explicitly resolve requirements Q-1 and Q-2 with clear DROPPED/additive rationale
- systemMessage format stability note (D-10) captures the scraping contract requirement
- Recall context entries align with design decisions: forced injection bypasses recognition (motivation), channel audiences (D-7), context budget (D-6/Risks)

## Recommendations

- During implementation, decide whether to promote `_extract_keywords()` and `_extract_section_content()` to public API or inline the logic. Promotion is cleaner but changes the dependency contract; inlining duplicates but is self-contained.
- ~~The `score_relevance()` `session_id` parameter is semantically meaningless for hook use.~~ **Resolved:** Call `score_relevance()` directly. Coupling is to a stable, pure function in the same domain package. Inlining creates two copies that must stay in sync through D-10 calibration — worse than synthetic session_id.
- `system_parts` join with `" | "` may produce awkward output when topic block has internal newlines. Test visually during integration.

---

**Ready for user presentation**: Yes
