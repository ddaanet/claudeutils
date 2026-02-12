# Cycle 0.5

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 0

---

## Cycle 0.5: Word-overlap tiebreaker

**RED Phase:**

**Test:** `test_word_overlap_tiebreaker`
**Assertions:**
- Given two candidates with identical fzf scores (construct carefully):
  `score_match("auth fail", "when auth fails")` > `score_match("auth fail", "auth failover config")` when fzf scores are tied
- More specifically: "auth fail" has 2 word overlaps with "when auth fails" vs 1 with "auth failover config" (validates tiebreaker logic)

**Expected failure:** AssertionError — tied scores remain tied

**Why it fails:** No word-overlap tiebreaker logic

**Verify RED:** `pytest tests/test_when_fuzzy.py::test_word_overlap_tiebreaker -v`

**GREEN Phase:**

**Implementation:** Add word-overlap tiebreaker to scoring.

**Behavior:**
- After fzf-style scoring, compute word overlap between query words and candidate words
- Each overlapping word adds a small bonus (0.5 or similar — smaller than fzf score granularity but breaks ties)
- Word matching is case-insensitive, exact word match only

**Approach:** Split query and candidate into word sets. Count intersecting words. Add fractional bonus per overlap.

**Changes:**
- File: `src/claudeutils/when/fuzzy.py`
  Action: Add word overlap calculation as secondary scoring factor
  Location hint: At end of score_match, after primary scoring

**Verify GREEN:** `pytest tests/test_when_fuzzy.py::test_word_overlap_tiebreaker -v`
**Verify no regression:** `pytest tests/ -q`

---
