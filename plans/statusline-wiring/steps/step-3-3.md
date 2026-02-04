# Cycle 3.3

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-3-3-notes.md`

---

## Cycle 3.3: Handle OAuth API failures gracefully

**Objective**: get_plan_usage() returns None when UsageCache.get() fails (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_plan_usage.py mocks UsageCache.get() to raise exception, asserts get_plan_usage() returns None without propagating exception

**Expected failure:**
```
Exception: API call failed
```

**Why it fails:** No exception handling for UsageCache.get() failures

**Verify RED:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage_api_failure -xvs
- Must fail with Exception
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap UsageCache.get() in try/except, return None on any exception

**Changes:**
- File: src/claudeutils/statusline/plan_usage.py
  Action: Add try/except around UsageCache.get(), catch all exceptions, return None

**Verify GREEN:** pytest tests/test_statusline_plan_usage.py::test_get_plan_usage_api_failure -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-3-3-notes.md

---

**Light Checkpoint** (end of Phase 3)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 3 implementations against design. Check for stubs.

---
