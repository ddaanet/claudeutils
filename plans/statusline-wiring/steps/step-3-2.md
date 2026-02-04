# Cycle 3.2

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-3-2-notes.md`

---

## Cycle 3.2: Fetch plan usage from OAuth API with cache

**Objective**: get_plan_usage() calls account.usage.UsageCache to fetch 5h/7d limits from Claude OAuth API
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_plan_usage.py mocks UsageCache.get() to return mock usage data, asserts get_plan_usage() returns PlanUsageData with 5h/7d percentages and reset times

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.plan_usage'
```

**Why it fails:** plan_usage.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - plan_usage.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/plan_usage.py with get_plan_usage() that uses UsageCache.get()

**Changes:**
- File: src/claudeutils/statusline/plan_usage.py
  Action: Create with get_plan_usage() → PlanUsageData | None, call account.usage.UsageCache(...).get(), parse 5h and 7d limits
- File: src/claudeutils/statusline/models.py
  Action: Add PlanUsageData(BaseModel) with hour5_pct: float, hour5_reset: str, day7_pct: float fields

**Verify GREEN:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-3-2-notes.md

---
