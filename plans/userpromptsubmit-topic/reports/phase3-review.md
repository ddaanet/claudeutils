# Review: UPS Phase 3 — Hook Integration

**Scope**: `src/claudeutils/recall/topic_matcher.py` (match_topics entry point), `agent-core/hooks/userpromptsubmit-shortcuts.py` (Tier 2.75 detector block), `tests/test_ups_topic_integration.py` (integration tests)
**Baseline**: ff920a01
**Date**: 2026-03-01T00:00:00
**Mode**: review + fix

## Summary

Phase 3 delivers the `match_topics` entry point, hook integration as a Tier 2.75 parallel detector, and four integration tests covering the positive match, additive, and no-match paths. The implementation faithfully follows the design: dual-channel output (D-7), silent failure wrapping (hook robustness), env-based path resolution, parallel accumulator pattern (D-3), and entry count cap (D-6). Design decisions D-1 through D-9 are all correctly implemented.

Three minor issues found: duplicate prompt tokenization in `match_topics`, a weak assertion structure in the no-match test, and two redundant positive-match integration tests. All issues are fixable.

**Overall Assessment**: Ready (post-fix)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Duplicate prompt tokenization in `match_topics`**
   - Location: `src/claudeutils/recall/topic_matcher.py:297-298`
   - Note: `match_topics` calls `extract_keywords(prompt_text)` at line 297 to produce `prompt_keywords`, then immediately calls `get_candidates(prompt_text, inverted_index)` at line 298, which internally calls `extract_keywords(prompt_text)` again. The prompt is tokenized twice. Fix: change `get_candidates` signature to accept pre-computed keywords and pass `prompt_keywords` from the call site.
   - **Status**: FIXED

2. **No-match test uses early-return instead of unconditional assertion**
   - Location: `tests/test_ups_topic_integration.py:195-214`
   - Note: The test returns early when `result == {}` with no assertion, then uses conditional checks for the non-empty case. This creates a vacuously-passing test for the expected path: the early return never asserts that the empty dict is specifically from absence of topic content (vs. no hook output at all). Fix: assert the no-topic condition unconditionally across both result shapes.
   - **Status**: FIXED

3. **Two redundant positive-match integration tests**
   - Location: `tests/test_ups_topic_integration.py:45-114`
   - Note: `test_hook_topic_injection_produces_additional_context` and `test_hook_topic_injection_end_to_end` both test the positive-match path with different prompts but identical assertion structure (`additionalContext` present, `topic` in system message). No distinct behavior is isolated between them. The additive and no-match tests cover genuinely distinct paths. Collapse to one test.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/recall/topic_matcher.py:39-52` — Changed `get_candidates` to accept `prompt_keywords: set[str]` instead of `prompt_text: str`, eliminating redundant `extract_keywords` call inside the function
- `src/claudeutils/recall/topic_matcher.py:298` — Updated `match_topics` to pass `prompt_keywords` to `get_candidates` (not `prompt_text`)
- `tests/test_recall_topic_matcher.py:7` — Merged `extract_keywords` import into existing `claudeutils.recall.index_parser` import line; updated `get_candidates` call site to pass pre-computed keywords
- `tests/test_ups_topic_integration.py:45-114` — Removed redundant `test_hook_topic_injection_produces_additional_context`; retained `test_hook_topic_injection_end_to_end` as the canonical positive-match test
- `tests/test_ups_topic_integration.py:175-214` — Replaced early-return pattern with unconditional assertions on result structure

**Validation**: `just precommit` — 1378/1379 passed, 1 pre-existing xfail. All clean.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Parse memory-index into keyword lookup | Satisfied | `build_inverted_index` + `get_or_build_index` in topic_matcher.py:30-36, 247-281 |
| FR-2: Match prompt against keyword table, rank by score | Satisfied | `get_candidates` + `score_and_rank` in topic_matcher.py:39-71 |
| FR-3: Resolve matched entries to decision file content | Satisfied | `resolve_entries` in topic_matcher.py:80-118 |
| FR-4: Cache inverted index with mtime invalidation | Satisfied | `get_or_build_index` with mtime check in topic_matcher.py:262-281 |
| FR-5: Integrate as parallel detector in hook | Satisfied | Tier 2.75 block in userpromptsubmit-shortcuts.py:935-949, additive accumulator pattern |
| FR-6: Entry count cap (max 3) | Satisfied | `max_entries=3` default in `match_topics` signature, passed to `score_and_rank` |
| FR-7: systemMessage with matched trigger lines + count header | Satisfied | `format_output` produces `"topic (N lines):\n{triggers}"` in topic_matcher.py:154 |

---

## Positive Observations

- Hook integration correctly uses try/except with silent pass — topic injection never breaks the hook (D-hook robustness)
- Import of `match_topics` is guarded with try/except ImportError, making the feature gracefully optional
- `get_or_build_index` correctly falls back to cold build when cache is missing, corrupt, or stale
- `resolve_entries` silently skips entries with missing files or sections — correct behavior per D-5
- Dual-channel output (D-7) correctly implemented: resolved sections in `additionalContext`, formatted trigger lines in `systemMessage`
- Tier 2.75 positioned between pattern guards and continuation parsing, consistent with D-3 ordering
- `format_output` correctly returns empty `TopicMatchResult` on empty input — no injection on no-match
