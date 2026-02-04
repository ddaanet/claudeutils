# Cycle 4.4

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-4-4-notes.md`

---

## Cycle 4.4: Parse stats-cache.json and aggregate by tier

**Objective**: get_api_usage() reads ~/.claude/stats-cache.json and aggregates tokens by model tier (opus/sonnet/haiku)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_api_usage.py mocks Path.open to return stats-cache.json with dailyModelTokens, asserts get_api_usage() returns ApiUsageData with today_opus, today_sonnet, today_haiku counts

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.api_usage'
```

**Why it fails:** api_usage.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_api_usage.py::test_get_api_usage -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - api_usage.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/api_usage.py with get_api_usage() and aggregate_by_tier() helper

**Changes:**
- File: src/claudeutils/statusline/api_usage.py
  Action: Create with get_api_usage() → ApiUsageData | None, read stats-cache.json, parse dailyModelTokens, aggregate today and last 7 days by tier
- File: src/claudeutils/statusline/api_usage.py
  Action: Add aggregate_by_tier(tokens_by_model: dict) → dict helper that does keyword matching (opus/sonnet/haiku in model name)
- File: src/claudeutils/statusline/models.py
  Action: Add ApiUsageData(BaseModel) with today_opus, today_sonnet, today_haiku, week_opus, week_sonnet, week_haiku: int fields

**Verify GREEN:** pytest tests/test_statusline_api_usage.py::test_get_api_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-4-4-notes.md

---
