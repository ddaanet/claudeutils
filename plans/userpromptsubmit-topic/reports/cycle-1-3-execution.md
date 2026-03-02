# Cycle 1.3: Score, rank, and cap candidates

**Timestamp:** 2026-03-01

## Execution Report

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_recall_topic_matcher.py::test_score_candidates_ranks_by_relevance_and_filters -v`

**RED result:** FAIL as expected (ImportError: cannot import name 'score_and_rank')

**GREEN result:** PASS (2/2 parametrized test cases pass)

**Regression check:** 1368/1369 passed, 1 xfail (no new regressions)

**Refactoring:**
- Added parametrized test with two scenarios: threshold filtering and entry count capping
- Restructured test cases to verify: threshold filtering, max_entries capping, descending score ordering
- Test uses minimal assertions focused on contract validation

**Files modified:**
- `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/recall/topic_matcher.py` — added `score_and_rank()` function with imports for `score_relevance` and `RelevanceScore`
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_topic_matcher.py` — added parametrized test with 2 cases (threshold filtering, max_entries capping)

**Stop condition:** none

**Decision made:**
- `score_and_rank()` uses session_id="hook" (synthetic ID per recall specification)
- Scoring calls `score_relevance()` with threshold passed through (filter applied before ranking)
- Results sorted descending by score, then sliced to max_entries if provided
- List comprehension for scoring, filter for relevance threshold, sort+slice for ranking/capping
- Test parametrized to verify both scenarios: filtering entries below threshold and capping result count
