# Cycle 4.5

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-5-notes.md`

---

## Cycle 4.5: Calculate week stats by summing last 7 days

**Objective**: get_api_usage() sums last 7 days of token counts for week_* fields
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks stats-cache.json with 7 days of data, asserts get_api_usage() returns week_opus/sonnet/haiku as sum of all 7 days

**Expected failure:**
```
AssertionError: assert 100 == 700  # week_opus should be 7 days * 100
```

**Why it fails:** get_api_usage() only aggregates today's stats, not week

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_week_aggregation -xvs
- Must fail with AssertionError (week counts don't sum 7 days)
- If passes, STOP - week aggregation may already exist

---

**GREEN Phase:**

**Implementation:** Add loop to sum last 7 days from dailyModelTokens array, aggregate each day by tier, accumulate totals

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Add week_stats = data["dailyModelTokens"][-7:], loop through days, aggregate each day, sum to week_by_tier dict

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_api_usage_week_aggregation -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-5-notes.md

---
